import asyncio
import json
import typing
from abc import ABC, abstractmethod

import structlog
from aio_pika import connect_robust, DeliveryMode, Message
from aio_pika.abc import AbstractExchange, AbstractRobustChannel, AbstractRobustConnection

logger = structlog.getLogger(__name__)


class AbstractAsyncRabbitMQPublisher(ABC):

    @abstractmethod
    async def async_init(self, connect_url: str, event_loop: asyncio.AbstractEventLoop) -> None:
        pass

    @abstractmethod
    async def publish(
        self,
        message_id: str,
        message_body: dict[str, typing.Any],
        routing_key: str,
        exchange_name: str,
    ) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class AsyncRabbitMQPublisher(AbstractAsyncRabbitMQPublisher):
    def __init__(self, exchange_mapping: dict[str, dict[str, typing.Any]]) -> None:
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None
        self._exchanges: dict[str, AbstractExchange] = {}
        self._exchange_mapping: dict[str, dict[str, typing.Any]] = exchange_mapping

    @property
    def connection(self) -> AbstractRobustConnection:
        if not self._connection:
            raise AttributeError("Connection to RabbitMQ is not set.")
        return self._connection

    @property
    def channel(self) -> AbstractRobustChannel:
        if not self._channel:
            raise AttributeError("Channel is not set.")
        return self._channel

    async def _get_exchange(self, name: str) -> AbstractExchange:
        """Get exchange by name, init one if not yet."""
        if name not in self._exchange_mapping:
            raise ValueError(
                f"There is no exchange called {name} in the exchange mapping. Can't establish the exchange.",  # noqa: E501 line too long
            )
        if name not in self._exchanges:
            exchange = await self.channel.declare_exchange(
                name=name,
                **self._exchange_mapping[name],
            )
            self._exchanges[name] = exchange
        return self._exchanges[name]

    async def async_init(
        self,
        connect_url: str,
        event_loop: asyncio.AbstractEventLoop,
    ) -> None:
        """Establishes connection and channel."""
        self._connection = await connect_robust(
            url=connect_url,
            loop=event_loop,
        )
        self._channel = await self.connection.channel()  # type: ignore

    async def publish(
        self,
        message_id: str,
        message_body: dict[str, typing.Any],
        routing_key: str,
        exchange_name: str,
    ) -> None:
        """Publish message to RabbitMQ."""
        exchange = await self._get_exchange(exchange_name)
        logger.info(
            "Publishing a new message...",
            message_id=message_id,
            routing_key=routing_key,
            exchange_name=exchange_name,
        )

        await exchange.publish(
            Message(
                body=json.dumps(message_body).encode("utf-8"),
                message_id=message_id,
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        logger.info(
            "Message published",
            message_id=message_id,
            routing_key=routing_key,
            exchange_name=exchange_name,
        )

    async def close(self) -> None:
        """Clothes the connection and the channel."""
        if self.channel:
            await self.channel.close()

        if self.connection:
            await self.connection.close()
