import logging

from yt_playlist_bot.main import main

import structlog

from yt_playlist_bot.settings import LOG_LEVEL
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(LOG_LEVEL)))

main()