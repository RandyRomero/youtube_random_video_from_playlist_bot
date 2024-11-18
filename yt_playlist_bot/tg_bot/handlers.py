import structlog
from aiogram.types import Message

from yt_playlist_bot.link_processor.main import process_link

logger = structlog.getLogger(__name__)


async def reply_start_command_message_handler(message: Message) -> None:
    """Replies to /start command"""
    logger.info("Got /start command.", chat_id=message.chat.id)

    await message.answer(
        text="Sent me a link to a YouTube playlist (not a public one) and I will send you back to you a link to random video from this playlist.",  # noqa: E501 line too long
    )
    logger.info("Replied to the message.", chat_id=message.chat.id)


async def reply_message_handler(message: Message) -> None:
    """Replies to any message."""
    logger.info("Got a new general message.", chat_id=message.chat.id)

    try:
        link = process_link(message.text or "")
    except ValueError as err:
        logger.error(err)
        await message.answer(str(err))
        return

    await message.answer(
        text=link,
    )

    logger.info("Replied to the message", chat_id=message.chat.id)
