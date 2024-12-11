import asyncio
import typing

import structlog
from aiogram import Bot

from yt_playlist_bot import settings
from yt_playlist_bot.link_processor.main import process_link

logger = structlog.get_logger(__name__)


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
    await bot.send_message(chat_id=chat_id, text=msg_text)
    logger.debug("Sent a link to a random video back to the chat", chat_id=chat_id)
    await bot.session.close()
    logger.debug("Closed the bot connection for the link processor.")
