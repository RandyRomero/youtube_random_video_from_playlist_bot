import asyncio

from yt_playlist_bot import settings
from yt_playlist_bot.logging_setup import setup_logging
from yt_playlist_bot.settings import BOT_TOKEN, JSON_LOGS, LOG_LEVEL
from yt_playlist_bot.tg_bot.bot import get_new_bot


async def main(event_loop: asyncio.AbstractEventLoop) -> None:
    bot = await get_new_bot(
        BOT_TOKEN,
        event_loop=event_loop,
        rabbit_connect_url=settings.get_rabbit_connection_string(),
    )
    await bot.bot.send_message(
        chat_id=settings.ADMIN_TELEGRAM_ID,
        text="Starting YouTube playlist bot...",
    )
    await bot.start_polling()


if __name__ == "__main__":
    setup_logging(LOG_LEVEL, JSON_LOGS)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
