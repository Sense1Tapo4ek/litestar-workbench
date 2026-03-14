import asyncio
import json
import re
import time
from typing import Any

import httpx
from loguru import logger
import aio_pika

from ..models import ScenarioStep, StepResult, StepType


class ScenarioExecutor:
    def __init__(self, rabbitmq_url: str) -> None:
        self._context: dict[str, Any] = {}
        self._cookies: dict[str, str] = {}
        self.rabbitmq_url = rabbitmq_url

    def reset_context(self) -> None:
        self._context.clear()
        self._cookies.clear()

    def resolve_variables(self, value: str) -> str:
        def replace(match: re.Match) -> str:
            expr = match.group(1)
            parts = expr.split(".")
            obj = self._context
            for part in parts:
                if isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    return match.group(0)
                if obj is None:
                    return match.group(0)
            return str(obj)

        return re.sub(r"\$\{([^}]+)\}", replace, value)

    async def execute_step(self, step: ScenarioStep, port: int) -> StepResult:
        if step.step_type == StepType.WEBSOCKET:
            return await self._execute_ws_step(step, port)
        elif step.step_type == StepType.FASTSTREAM:
            return await self._execute_faststream_step(step)
        return await self._execute_http_step(step, port)

    async def _execute_faststream_step(self, step: ScenarioStep) -> StepResult:
        messages = step.stream_messages or []
        start = time.perf_counter()

        try:
            connection = await aio_pika.connect_robust(self.rabbitmq_url)
            async with connection:
                channel = await connection.channel()

                all_passed = True
                results = []

                for msg in messages:
                    topic_str = self.resolve_variables(msg.topic)
                    payload_str = self.resolve_variables(msg.payload)

                    queue = None
                    if msg.expect_topic:
                        # Декларируем очередь перед отправкой, чтобы поймать ответ
                        expect_topic_str = self.resolve_variables(msg.expect_topic)
                        queue = await channel.declare_queue(
                            expect_topic_str, auto_delete=True
                        )

                    # Публикуем сообщение в дефолтный обменник (routing_key = имя очереди)
                    await channel.default_exchange.publish(
                        aio_pika.Message(body=payload_str.encode()),
                        routing_key=topic_str,
                    )

                    ok = True
                    received = None

                    if queue:
                        try:
                            async with queue.iterator() as q_iter:
                                async with asyncio.timeout(5.0):
                                    async for message in q_iter:
                                        async with message.process():
                                            received = message.body.decode()
                                            break

                            if (
                                msg.expect_contains
                                and msg.expect_contains not in received
                            ):
                                ok = False
                        except TimeoutError:
                            ok = False
                            received = "<timeout>"

                    results.append(
                        {
                            "topic": topic_str,
                            "published": payload_str,
                            "received": received,
                            "passed": ok,
                        }
                    )

                    if not ok:
                        all_passed = False

            elapsed_ms = (time.perf_counter() - start) * 1000
            body_str = json.dumps(results, ensure_ascii=False, indent=2)

            return StepResult(
                step_id=step.id,
                actual_status=200 if all_passed else 400,
                elapsed_ms=round(elapsed_ms, 1),
                passed=all_passed,
                response_body=body_str,
                step_type=StepType.FASTSTREAM,
            )

        except Exception as exc:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error=f"FastStream Error: {str(exc)}",
                step_type=StepType.FASTSTREAM,
            )

    async def _execute_ws_step(self, step: ScenarioStep, port: int) -> StepResult:
        try:
            import websockets
        except ImportError:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error="websockets package not installed. Run: uv add websockets",
                step_type=StepType.WEBSOCKET,
            )

        path = self.resolve_variables(step.path)
        url = f"ws://127.0.0.1:{port}{path}"
        messages = step.messages or []
        start = time.perf_counter()

        try:
            async with websockets.connect(url, open_timeout=5) as ws:
                all_passed = True
                results = []
                for msg in messages:
                    await ws.send(msg.send)
                    received = await asyncio.wait_for(ws.recv(), timeout=5)
                    ok = True
                    if msg.expect is not None:
                        ok = received == msg.expect
                    elif msg.expect_contains is not None:
                        ok = msg.expect_contains in received
                    results.append(
                        {"sent": msg.send, "received": received, "passed": ok}
                    )
                    if not ok:
                        all_passed = False

            elapsed_ms = (time.perf_counter() - start) * 1000
            body_str = json.dumps(results, ensure_ascii=False, indent=2)
            return StepResult(
                step_id=step.id,
                actual_status=101,
                elapsed_ms=round(elapsed_ms, 1),
                passed=all_passed,
                response_body=body_str,
                step_type=StepType.WEBSOCKET,
            )
        except OSError:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error="WebSocket connection refused. Is the lesson server running?",
                step_type=StepType.WEBSOCKET,
            )
        except Exception as exc:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error=str(exc),
                step_type=StepType.WEBSOCKET,
            )

    async def _execute_http_step(self, step: ScenarioStep, port: int) -> StepResult:
        base_url = f"http://127.0.0.1:{port}"
        path = self.resolve_variables(step.path)

        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
                method = step.method.lower()
                kwargs: dict = {}
                if step.body:
                    kwargs["json"] = step.body
                # Merge accumulated cookies with step-specific cookies
                merged_cookies = dict(self._cookies)
                if step.cookies:
                    merged_cookies.update(
                        {k: self.resolve_variables(v) for k, v in step.cookies.items()}
                    )
                if merged_cookies:
                    kwargs["cookies"] = merged_cookies
                if step.headers:
                    kwargs["headers"] = {
                        k: self.resolve_variables(v) for k, v in step.headers.items()
                    }

                start = time.perf_counter()
                response = await getattr(client, method)(path, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                # Persist any new cookies from the response for subsequent steps
                self._cookies.update(dict(response.cookies))

            try:
                body = response.json()
                body_str = json.dumps(body, ensure_ascii=False, indent=2)
            except Exception:
                body_str = response.text

            passed = response.status_code == step.expect_status

            if step.save_as and passed:
                try:
                    self._context[step.save_as] = response.json()
                except Exception:
                    pass

            if step.save_cookies:
                self._context[step.save_cookies] = dict(response.cookies)

            logger.info(
                f"Step {step.id}: {step.method} {path} → {response.status_code} "
                f"({'OK' if passed else 'FAIL'}) {elapsed_ms:.0f}ms"
            )

            return StepResult(
                step_id=step.id,
                actual_status=response.status_code,
                response_body=body_str,
                elapsed_ms=round(elapsed_ms, 1),
                passed=passed,
                response_headers=dict(response.headers),
                response_cookies=dict(response.cookies),
            )

        except httpx.ConnectError:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error="Connection refused. Is the lesson server running?",
            )
        except Exception as exc:
            return StepResult(
                step_id=step.id,
                actual_status=0,
                elapsed_ms=0.0,
                passed=False,
                error=str(exc),
            )
