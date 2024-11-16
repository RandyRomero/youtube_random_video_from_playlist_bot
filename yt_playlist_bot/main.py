import argparse
import random
import uuid

import structlog
from pytube import Playlist

logger = structlog.get_logger(__name__)

YOUTUBE_PLAYLIST_LINK_TEMPLATE = "https://www.youtube.com/playlist?list="


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
    logger.info(f"There are {len(playlist.video_urls)} videos in total.")
    logger.debug("Picking a random video from the playlist...")
    return random.choice(playlist.video_urls)


def main() -> None:
    # using global is a bad practice and I will appreciate if you can give me a hint
    # how do I attach request_id to every logging message in the module without
    # using globals
    global logger

    args = parse_args()

    logger = logger.bind(request_id=str(uuid.uuid4()))
    logger.info("Start working...")

    playlist_link = args.link
    logger.debug("Given link", playlist_list=playlist_link)

    validate_link(playlist_link)
    logger.debug("Link is valid.")

    random_link = get_random_link_from_youtube_playlist(playlist_link)
    logger.info(random_link)


if __name__ == "__main__":
    main()
