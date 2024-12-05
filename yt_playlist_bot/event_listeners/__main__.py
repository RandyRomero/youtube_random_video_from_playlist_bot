import asyncio

from yt_playlist_bot.event_listeners.link_event_listener import main
from yt_playlist_bot.logging_setup import setup_logging
from yt_playlist_bot.settings import JSON_LOGS, LOG_LEVEL

if __name__ == "__main__":
    setup_logging(LOG_LEVEL, JSON_LOGS)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
