import asyncio
import json
import typing as tp
from asyncio import AbstractEventLoop

import structlog
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue

logger = structlog.getLogger(__name__)


PREFETCH_COUNT = 100


class CallbackType(tp.Protocol):
    def __call__(
        self,
        event_loop: AbstractEventLoop,
        message_id: str,
        message_body: dict[tp.Any, tp.Any],
        routing_key: str,
        **kwargs: tp.Any,
    ) -> tp.Awaitable[None]:
        """A signature of a function that will be called to process a rabbit message."""
        pass


async def consumer(
    queue: AbstractQueue,
    event_loop: asyncio.AbstractEventLoop,
    callback_func: CallbackType,
) -> None:
    """Get messages from the queue and send them to message processor."""
    async with queue.iterator() as queue_iter:
        message: AbstractIncomingMessage
        async for message in queue_iter:
            async with message.process(
                requeue=True,
                reject_on_redelivered=True,
                ignore_processed=True,
            ):
                logger.info("Got new message.", queue=queue.name)

                if not message.message_id:
                    await message.nack()
                    raise AttributeError("Message has no message_id.")

                if not message.routing_key:
                    await message.nack()
                    raise AttributeError("Message has no routing_key.")

                structlog.contextvars.clear_contextvars()
                structlog.contextvars.bind_contextvars(
                    request_uuid=message.correlation_id,
                    rabbit_message_id=message.message_id,
                    routing_key=message.routing_key,
                )

                try:
                    message_body = json.loads(message.body)
                except json.decoder.JSONDecodeError:
                    logger.error("Couldn't deserialize the message")
                    await message.nack(requeue=False)
                    continue

                try:
                    logger.info("Calling callback function")
                    await callback_func(
                        event_loop=event_loop,
                        message_id=message.message_id,
                        message_body=message_body,
                        routing_key=message.routing_key,
                    )
                except Exception as exc:
                    logger.error(
                        "An error occurred while processing the message.",
                        request_uuid=message.correlation_id,
                        exc_info=True,
                    )
                    await message.nack(requeue=False)
                    continue

                await message.ack()
