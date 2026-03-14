from litestar import Litestar, Controller, Router, get
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers import BaseRouteHandler

from logger_setup import logger


# --- Guards ---


def app_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    logger.info("guard: APP level")
    api_key = connection.headers.get("x-api-key")
    if not api_key:
        raise NotAuthorizedException(detail="API key required")


def admin_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    logger.info("guard: ADMIN (controller level)")
    role = connection.headers.get("x-role", "")
    if role != "admin":
        raise PermissionDeniedException(detail="Admin access required")


def superadmin_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    logger.info("guard: SUPERADMIN (handler level)")
    level = connection.headers.get("x-level", "0")
    if int(level) < 10:
        raise PermissionDeniedException(detail="Superadmin level 10+ required")


# --- Controller ---


class AdminController(Controller):
    path = "/admin"
    guards = [admin_guard]

    @get("/dashboard")
    async def dashboard(self) -> dict[str, str]:
        logger.info("handler: admin dashboard")
        return {"page": "Admin Dashboard"}

    @get("/settings", guards=[superadmin_guard])
    async def settings(self) -> dict[str, str]:
        logger.info("handler: admin settings (superadmin)")
        return {"page": "Admin Settings -- superadmin only"}


# --- Public (no controller guard) ---


@get("/public")
async def public_page() -> dict[str, str]:
    logger.info("handler: public")
    return {"page": "Public -- only app guard"}


# --- Router ---

admin_router = Router(path="/api", route_handlers=[AdminController, public_page])

app = Litestar(route_handlers=[admin_router], guards=[app_guard])
