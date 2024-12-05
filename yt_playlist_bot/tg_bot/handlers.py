import structlog
from aiogram.types import Message

from yt_playlist_bot import constants
from yt_playlist_bot.tg_bot.controller import Controller
from yt_playlist_bot.tg_bot.message_texts import MessageTexts

logger = structlog.getLogger(__name__)


class TelegramBotHandlers:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller

    @staticmethod
    async def reply_start_command_message_handler(message: Message) -> None:
        """Replies to /start command"""
        logger.info("Got /start command.")

        await message.answer(text=MessageTexts.START_COMMAND_REPLY)
        logger.info("Replied to the /start command.")

    async def reply_message_handler(self, message: Message) -> None:
        """Replies to any message."""
        logger.info("Got a new general message.")

        if not message.text:
            await message.answer(text=MessageTexts.GOT_EMPTY_MESSAGE)
            return

        if not message.text.startswith(constants.YOUTUBE_PLAYLIST_LINK_TEMPLATE):
            await message.answer(text=MessageTexts.INVALID_YOUTUBE_PLAYLIST_LINK)
            return

        await self.controller.request_link(
            playlist_link=message.text,
            requester_telegram_id=message.chat.id,
        )

        await message.answer(text=MessageTexts.REQUEST_LINK_REPLY)
        logger.info("Replied to the message")
