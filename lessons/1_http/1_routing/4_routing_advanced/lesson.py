import uuid
from datetime import date

from litestar import Litestar, Request, get, route

from logger_setup import logger


@get("/users/{user_id:uuid}")
async def get_user(user_id: uuid.UUID) -> dict:
    logger.info(f"get_user: {user_id}")
    return {"user_id": str(user_id), "type": "uuid"}


@get("/events/{event_date:date}")
async def get_events(event_date: date) -> dict:
    logger.info(f"get_events: {event_date}")
    return {"date": event_date.isoformat(), "events": []}


@route("/ping", http_method=["GET", "HEAD"], sync_to_thread=False)
def ping() -> dict:
    return {"pong": True}


@get("/public")
async def public_endpoint() -> dict:
    return {"access": "public"}


@get("/admin/secret", opt={"auth": "required"}, name="admin_secret")
async def admin_secret(request: Request) -> dict:
    url = request.app.route_reverse("admin_secret")
    return {"secret": True, "self_url": url}


@get(
    "/admin/dashboard",
    opt={"auth": "required", "role": "admin"},
    name="admin_dashboard",
)
async def admin_dashboard(request: Request) -> dict:
    url = request.app.route_reverse("admin_dashboard")
    return {"dashboard": True, "self_url": url}


app = Litestar(
    route_handlers=[get_user, get_events, ping, public_endpoint, admin_secret, admin_dashboard]
)
