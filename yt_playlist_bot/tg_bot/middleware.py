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

    if getattr(event, "message", None):
        chat_id = event.message.chat.id  # type: ignore
    elif getattr(event, "callback_query", None):
        # it means we got a reply to an inline keyboard button instead of a message in a chat
        chat_id = event.callback_query.from_user.id  # type: ignore
    else:
        logger.error("Incoming Telegram message doesn't have chat id. Will not process.")
        return

    structlog.contextvars.bind_contextvars(
        request_uuid=request_uuid,
        chat_id=chat_id,
    )
    data["request_uuid"] = request_uuid
    return await handler(event, data)
