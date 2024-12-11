import aio_pika
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection

from yt_playlist_bot import settings


async def setup_rabbit_connection() -> tuple[AbstractRobustChannel, AbstractRobustConnection]:
    """Init rabbit connection."""
    connection: AbstractRobustConnection = await aio_pika.connect_robust(
        settings.get_rabbit_connection_string(),
    )

    # Creating channel
    channel: AbstractRobustChannel = await connection.channel()  # type: ignore

    # Maximum message count which will be processing at the same time.
    await channel.set_qos(prefetch_count=100)
    return channel, connection
