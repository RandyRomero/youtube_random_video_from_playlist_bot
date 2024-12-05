import asyncio
import json
import typing
from asyncio import AbstractEventLoop

import structlog
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue

logger = structlog.getLogger(__name__)


PREFETCH_COUNT = 100


class CallbackType(typing.Protocol):
    def __call__(
        self,
        event_loop: AbstractEventLoop,
        message_id: str,
        message_body: dict[typing.Any, typing.Any],
        routing_key: str,
    ) -> typing.Awaitable[None]:
        """A signature of a function that will be called to process rabbit message."""
        pass


async def consumer(
    queue: AbstractQueue,
    event_loop: asyncio.AbstractEventLoop,
    callback_func: CallbackType,
) -> None:
    """Run consumer and get messages from queue."""
    async with queue.iterator() as queue_iter:
        message: AbstractIncomingMessage
        async for message in queue_iter:
            async with message.process(
                requeue=True,
                reject_on_redelivered=True,
                ignore_processed=True,
            ):
                try:
                    message_body = json.loads(message.body)
                except json.decoder.JSONDecodeError:
                    await message.nack()
                    continue

                logger.info("Got new message.", queue=queue.name, routing_key=message.routing_key)
                if not message.message_id:
                    await message.nack()
                    raise AttributeError("Message has no message_id.")

                if not message.routing_key:
                    await message.nack()
                    raise AttributeError("Message has no routing_key.")

                structlog.contextvars.clear_contextvars()
                structlog.contextvars.bind_contextvars(rabbit_message_id=message.message_id)

                try:
                    await callback_func(
                        event_loop=event_loop,
                        message_id=message.message_id,
                        message_body=message_body,
                        routing_key=message.routing_key,
                    )
                except Exception as exc:
                    logger.error("Couldn't process message", exc=exc)
                    await message.nack()
                    continue

                await message.ack()
