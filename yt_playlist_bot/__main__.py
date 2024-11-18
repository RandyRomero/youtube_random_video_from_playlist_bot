import asyncio

from yt_playlist_bot.logging_setup import setup_logging
from yt_playlist_bot.settings import BOT_TOKEN, JSON_LOGS, LOG_LEVEL
from yt_playlist_bot.tg_bot.main import get_new_bot


async def main() -> None:
    bot = get_new_bot(BOT_TOKEN)
    await bot.start_polling()


if __name__ == "__main__":
    setup_logging(LOG_LEVEL, JSON_LOGS)
    asyncio.run(main())
