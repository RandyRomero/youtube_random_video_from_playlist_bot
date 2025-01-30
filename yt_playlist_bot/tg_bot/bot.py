import asyncio

import structlog
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart

from yt_playlist_bot import settings
from yt_playlist_bot.rabbit.publisher import AsyncRabbitMQPublisher
from yt_playlist_bot.tg_bot import middleware
from yt_playlist_bot.tg_bot.callbacks import OneMoreVideoCallback
from yt_playlist_bot.tg_bot.controller import Controller
from yt_playlist_bot.tg_bot.handlers import TelegramBotHandlers

logger = structlog.getLogger(__name__)


class TelegramBot:
    """
    Bot entity

    Handles messages from Telegram.
    """

    def __init__(self, bot: Bot, dispatcher: Dispatcher, handlers: TelegramBotHandlers) -> None:
        self.bot: Bot = bot
        self.dispatcher = dispatcher
        self.handlers = handlers

    async def start_polling(self) -> None:
        """Function to start listening to messages from Telegram."""
        logger.info("Bot is waking up...")
        await self.dispatcher.start_polling(self.bot)

    def register_handlers(self) -> None:
        """Registers handlers that respond to user messages to the bot."""
        self.dispatcher.message(CommandStart())(self.handlers.reply_start_command_message_handler)
        self.dispatcher.message()(self.handlers.reply_message_handler)
        self.dispatcher.callback_query(OneMoreVideoCallback.filter())(
            self.handlers.reply_one_more_video_callback,
        )

    def register_middleware(self) -> None:
        # https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html
        self.dispatcher.update.outer_middleware()(middleware.request_id_insert_middleware)  # type: ignore

    async def close(self) -> None:
        """Gracefully closes the connection the bot is using."""
        await self.bot.session.close()
        await self.handlers.controller.rabbit_publisher.close()


async def get_new_bot(
    bot_token: str,
    event_loop: asyncio.AbstractEventLoop,
    rabbit_connect_url: str,
) -> TelegramBot:
    """Creates a new instance of a TelegramBot."""

    bot = Bot(token=bot_token)
    dispatcher = Dispatcher()
    rabbit_publisher = AsyncRabbitMQPublisher(exchange_mapping=settings.EXCHANGE_MAPPING)
    await rabbit_publisher.async_init(
        connect_url=rabbit_connect_url,
        event_loop=event_loop,
    )
    controller = Controller(rabbit_publisher=rabbit_publisher)
    handlers = TelegramBotHandlers(controller=controller)
    bot = TelegramBot(bot, dispatcher, handlers)
    bot.register_handlers()
    bot.register_middleware()
    return bot
