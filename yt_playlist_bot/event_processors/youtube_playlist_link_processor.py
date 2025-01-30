import asyncio
import typing

import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from yt_playlist_bot import constants, settings
from yt_playlist_bot.link_processor.main import process_link
from yt_playlist_bot.tg_bot.callbacks import OneMoreVideoCallback

logger = structlog.get_logger(__name__)


def _extract_playlist_id(playlist_link: str) -> str:
    """Extracts playlist ID from playlist link."""
    if playlist_link.startswith(constants.YOUTUBE_PLAYLIST_LINK_TEMPLATES[0]):
        playlist_id = playlist_link.replace(constants.YOUTUBE_PLAYLIST_LINK_TEMPLATES[0], "")
    elif playlist_link.startswith(constants.YOUTUBE_PLAYLIST_LINK_TEMPLATES[1]):
        playlist_id = playlist_link.replace(constants.YOUTUBE_PLAYLIST_LINK_TEMPLATES[1], "")
    else:
        raise ValueError("Invalid playlist link")
    return playlist_id


async def process_get_a_video_events(
    event_loop: asyncio.AbstractEventLoop,
    message_body: dict[str, typing.Any],
) -> None:
    link = await event_loop.run_in_executor(
        None,
        process_link,
        message_body["playlist_link"],
    )

    msg_text = f"There is your random video from your playlist: {link}"

    # todo: find a way not to initialize it every time
    # maybe to keep an open bot in another consumer and send message via rabbitmq there
    bot = Bot(token=settings.BOT_TOKEN)
    chat_id = message_body["requester_telegram_id"]
    telegram_message_id = message_body["telegram_message_id"]

    # extract playlist id from playlist link because the whole link doesn't
    # fit into the InlineKeyboardButton callback
    playlist_id = _extract_playlist_id(message_body["playlist_link"])

    await bot.send_message(
        chat_id=chat_id,
        text=msg_text,
        reply_to_message_id=telegram_message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="One more video from this playlist",
                        callback_data=OneMoreVideoCallback(playlist_id=playlist_id).pack(),
                    ),
                ],
            ],
        ),
    )

    logger.debug("Sent a link to a random video back to the chat", chat_id=chat_id)
    await bot.session.close()
    logger.debug("Closed the bot connection for the link processor.")
