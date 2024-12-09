import asyncio
import typing

from aiogram import Bot

from yt_playlist_bot import settings
from yt_playlist_bot.link_processor.main import process_link


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
    bot = Bot(token=settings.BOT_TOKEN)
    await bot.send_message(chat_id=message_body["requester_telegram_id"], text=msg_text)
    await bot.session.close()
