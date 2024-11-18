import typing as tp
import uuid

import structlog
from aiogram.types import Update

logger = structlog.getLogger(__name__)


async def request_id_insert_middleware(
    handler: tp.Callable[[Update, dict[str, tp.Any]], tp.Awaitable[tp.Any]],
    event: Update,
    data: dict[str, tp.Any]
) -> tp.Any:
    request_uuid = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_uuid)
    return await handler(event, data)