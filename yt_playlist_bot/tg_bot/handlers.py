import structlog
from aiogram.types import Message

from yt_playlist_bot.link_processor.main import process_link

logger = structlog.getLogger(__name__)


async def reply_start_command_message_handler(message: Message) -> None:
    """Accepts any unexpected messages and gives a hint to use the button to get a note."""
    logger.info("Got a new message", chat_id=message.chat.id)

    await message.answer(text="Sent me a link to a YouTube playlist (not a public one)")
    logger.info("Replied to the message", chat_id=message.chat.id)

async def reply_message_handler(message: Message) -> None:
    """Accepts any unexpected messages and gives a hint to use the button to get a note."""
    logger.info("Got a new message", chat_id=message.chat.id)

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

