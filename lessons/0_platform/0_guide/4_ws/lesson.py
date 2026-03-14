import json
from datetime import datetime

from litestar import Litestar, WebSocket, websocket
from litestar.exceptions import WebSocketDisconnect

from logger_setup import logger


@websocket(path="/ws")
async def ws_handler(socket: WebSocket) -> None:
    await socket.accept()
    logger.info("WebSocket connected")
    try:
        while True:
            raw = await socket.receive_data(mode="text")
            try:
                data = json.loads(raw)
                event = data.get("event", "echo")
                logger.info(f"WS event: {event}")
                if event == "ping":
                    reply = {"event": "pong", "status": "ok"}
                elif event == "greet":
                    reply = {"event": "greet", "message": f"Hello, {data.get('name', 'world')}!"}
                elif event == "time":
                    reply = {"event": "time", "value": datetime.now().isoformat()}
                else:
                    reply = {"event": "echo", "received": data}
            except json.JSONDecodeError:
                reply = {"event": "echo", "received": raw}
            await socket.send_text(json.dumps(reply))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


app = Litestar([ws_handler])
