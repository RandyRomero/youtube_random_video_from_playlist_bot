import structlog
from aiogram.types import CallbackQuery, Message

from yt_playlist_bot import constants
from yt_playlist_bot.tg_bot.callbacks import OneMoreVideoCallback
from yt_playlist_bot.tg_bot.controller import Controller
from yt_playlist_bot.tg_bot.message_texts import MessageTexts

logger = structlog.getLogger(__name__)

YOUTUBE_LINK_TEMPLATES = constants.YOUTUBE_PLAYLIST_LINK_TEMPLATES


class TelegramBotHandlers:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller

    @staticmethod
    async def reply_start_command_message_handler(message: Message) -> None:
        """Replies to /start command"""
        logger.info("Got /start command.")

        await message.answer(text=MessageTexts.START_COMMAND_REPLY)
        logger.info("Replied to the /start command.")

    async def reply_message_handler(self, message: Message, request_uuid: str) -> None:
        """Replies to any message."""
        logger.info("Got a new general message.")

        if not message.text:
            await message.reply(text=MessageTexts.GOT_EMPTY_MESSAGE)
            return

        if not (
            message.text.startswith(YOUTUBE_LINK_TEMPLATES[0])
            or message.text.startswith(YOUTUBE_LINK_TEMPLATES[1])
        ):
            await message.reply(text=MessageTexts.INVALID_YOUTUBE_PLAYLIST_LINK)
            return

        await self.controller.request_link(
            playlist_link=message.text,
            requester_telegram_id=message.chat.id,
            telegram_message_id=message.message_id,
            request_uuid=request_uuid,
        )

        await message.reply(text=MessageTexts.REQUEST_LINK_REPLY)
        logger.info("Replied to the message")

    async def reply_one_more_video_callback(
        self,
        query: CallbackQuery,
        callback_data: OneMoreVideoCallback,
        request_uuid: str,
    ) -> None:
        """Replies to button for one more video from the same playlist."""
        link = f"https://youtube.com/playlist?list={callback_data.playlist_id}"

        if not getattr(query, "message", None):
            await query.answer(text=MessageTexts.SOMETHING_WRONG_WITH_THE_MESSAGE)
            logger.warning("Callback query doesn't have message attribute set.")
            return

        await self.controller.request_link(
            playlist_link=link,
            requester_telegram_id=query.message.chat.id,  # type: ignore
            telegram_message_id=query.message.message_id,  # type: ignore
            request_uuid=request_uuid,
        )

        await query.answer(text=MessageTexts.REQUEST_LINK_REPLY)
        logger.info("Replied to the message")
