import os

from aio_pika import ExchangeType

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
JSON_LOGS = os.environ.get("JSON_LOGS", "False").lower() in ("true", "1", "t")

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_TELEGRAM_ID = os.environ["ADMIN_TELEGRAM_ID"]

# rabbit
RABBIT_HOST = os.environ["RABBIT_HOST"]
RABBIT_PORT = os.environ["RABBIT_PORT"]
RABBIT_USER = os.environ["RABBIT_USER"]
RABBIT_PASS = os.environ["RABBIT_PASS"]


def get_rabbit_connection_string() -> str:
    return "amqp://{user}:{password}@{host}:{port}/".format(
        user=RABBIT_USER,
        password=RABBIT_PASS,
        host=RABBIT_HOST,
        port=RABBIT_PORT,
    )


# rabbit
GET_VIDEO_FROM_PLAYLIST_EVENT = "GET_VIDEO_FROM_PLAYLIST_EVENT"
YOUTUBE_PROCESSOR_EXCHANGE = "YOUTUBE_PROCESSOR_EXCHANGE"
PLAYLIST_QUEUE = "PLAYLIST_QUEUE"


EXCHANGE_MAPPING = {  # exchange names to their settings
    YOUTUBE_PROCESSOR_EXCHANGE: {"type": ExchangeType.DIRECT, "durable": True},
}
