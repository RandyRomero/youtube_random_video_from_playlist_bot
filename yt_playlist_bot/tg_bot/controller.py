import uuid

import structlog

from yt_playlist_bot import settings
from yt_playlist_bot.rabbit.publisher import AbstractAsyncRabbitMQPublisher

logger = structlog.getLogger(__name__)


class Controller:
    """Contains logic for telegram bot handlers."""

    def __init__(self, rabbit_publisher: AbstractAsyncRabbitMQPublisher) -> None:
        self.rabbit_publisher = rabbit_publisher

    async def request_link(
        self,
        playlist_link: str,
        telegram_message_id: int,
        requester_telegram_id: int,
        request_uuid: str,
    ) -> None:
        """
        Publish a request to a specific queue.

        So the link processor will process it eventually.
        """
        message_id = str(uuid.uuid4())
        message_body = {
            "playlist_link": playlist_link,
            "requester_telegram_id": requester_telegram_id,
            "telegram_message_id": telegram_message_id,
        }

        logger.info(
            "Making a request to get a random video from a link to a playlist is made.",
            message_id=message_id,
        )

        await self.rabbit_publisher.publish(
            request_uuid=request_uuid,
            message_id=message_id,
            message_body=message_body,
            routing_key=settings.GET_VIDEO_FROM_PLAYLIST_EVENT,
            exchange_name=settings.YOUTUBE_PROCESSOR_EXCHANGE,
        )
        logger.info(
            "Request to get a random video from a link to a playlist is made.",
            message_id=message_id,
        )
