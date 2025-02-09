import asyncio
import typing
from functools import partial

import aiogram
import structlog
from aio_pika.abc import AbstractQueue

from yt_playlist_bot import settings
from yt_playlist_bot.event_processors.youtube_playlist_link_processor import (
    process_get_a_video_events,
)
from yt_playlist_bot.rabbit.consumer import consumer
from yt_playlist_bot.rabbit.misc import setup_rabbit_connection
from yt_playlist_bot.settings import EXCHANGE_MAPPING, YOUTUBE_PROCESSOR_EXCHANGE

logger = structlog.getLogger(__name__)


async def _process_message(
    event_loop: asyncio.AbstractEventLoop,
    message_id: str,
    message_body: dict[str, typing.Any],
    routing_key: str,
    bot: aiogram.Bot,
) -> None:
    """Check routing key and choose corresponding message processor."""
    if routing_key != settings.GET_VIDEO_FROM_PLAYLIST_EVENT:
        raise KeyError("Unknown routing key.")
    await process_get_a_video_events(event_loop, message_body, bot)


async def main(event_loop: asyncio.AbstractEventLoop) -> None:
    """Run rabbit consumer."""
    logger.info("Starting up the consumer...")

    channel, connection = await setup_rabbit_connection()

    exchange = await channel.declare_exchange(
        name=YOUTUBE_PROCESSOR_EXCHANGE,
        **EXCHANGE_MAPPING[YOUTUBE_PROCESSOR_EXCHANGE],  # type: ignore
    )

    queue: AbstractQueue = await channel.declare_queue(
        settings.PLAYLIST_QUEUE,
        durable=True,
        exclusive=False,
        auto_delete=False,
    )

    await queue.bind(
        exchange=exchange,
        routing_key=settings.GET_VIDEO_FROM_PLAYLIST_EVENT,
    )

    bot = aiogram.Bot(token=settings.BOT_TOKEN)

    try:
        await consumer(
            queue=queue,
            event_loop=event_loop,
            callback_func=partial(_process_message, bot=bot),
        )
    except Exception as exc:
        logger.error("Consumer closed unexpectedly.", exc=exc)
    finally:
        logger.info("Terminating consumer...")
        await channel.close()
        await connection.close()
        await bot.close()
