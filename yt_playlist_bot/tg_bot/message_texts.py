from enum import StrEnum


class MessageTexts(StrEnum):
    START_COMMAND_REPLY = "Sent me a link to a YouTube playlist (not a public one) and I will send you back to you a link to random video from this playlist."  # noqa: E501 message too long
    REQUEST_LINK_REPLY = (
        "You request is being processed and you will get the replied shortly in a few seconds."
    )
    INVALID_YOUTUBE_PLAYLIST_LINK = "The Invalid YouTube playlist link."
    GOT_EMPTY_MESSAGE = "I can't read your mind (yet)."
    SOMETHING_WRONG_WITH_THE_MESSAGE = "Something is wrong with your message."
