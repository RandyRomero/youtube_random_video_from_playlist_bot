import argparse
import random

import structlog
from pytube import Playlist

from yt_playlist_bot.constants import YOUTUBE_PLAYLIST_LINK_TEMPLATE

logger = structlog.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--link",
    )
    return parser.parse_args()


def validate_link(link: str) -> None:
    if not link.startswith(YOUTUBE_PLAYLIST_LINK_TEMPLATE):
        raise ValueError("Invalid link. This is a not a link to a YouTube playlist.")


def get_random_link_from_youtube_playlist(link_to_playlist: str) -> str:
    playlist = Playlist(link_to_playlist)
    logger.debug("Getting total number of videos in the playlist...")
    total_videos_num = len(playlist.video_urls)
    if not total_videos_num:
        raise ValueError("Playlist is either empty or private.")
    logger.info("There are %d videos in total.", len(playlist.video_urls))
    logger.debug("Picking a random video from the playlist...")
    return random.choice(playlist.video_urls)


def process_link(playlist_link: str) -> str:
    """Does everything to get the link to the random video from the given playlist."""
    logger.debug("Given link", playlist_link=playlist_link)

    validate_link(playlist_link)
    logger.debug("Link is valid.")

    random_link = get_random_link_from_youtube_playlist(playlist_link)
    return random_link


def main(args: argparse.Namespace) -> str:
    logger.info("Start working...")

    playlist_link = args.link
    return process_link(playlist_link)


if __name__ == "__main__":
    args = parse_args()
    main(args)
