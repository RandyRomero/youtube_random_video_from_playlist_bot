import typing as tp
import uuid

import structlog
from aiogram.types import Update

logger = structlog.getLogger(__name__)


async def request_id_insert_middleware(
    handler: tp.Callable[[Update, dict[str, tp.Any]], tp.Awaitable[tp.Any]],
    event: Update,
    data: dict[str, tp.Any],
) -> tp.Any:
    request_uuid = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()

    chat_id = None
    try:
        chat_id = event.message.chat.id  # type: ignore
    except AttributeError as error:
        logger.error("Incoming Telegram message doesn't have chat id", original_error=str(error))

    structlog.contextvars.bind_contextvars(
        request_uuid=request_uuid,
        chat_id=chat_id,
    )
    data["request_uuid"] = request_uuid
    return await handler(event, data)
