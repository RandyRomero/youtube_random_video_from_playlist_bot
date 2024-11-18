import structlog
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart

from yt_playlist_bot.tg_bot import handlers
from yt_playlist_bot.tg_bot import middleware

logger = structlog.getLogger(__name__)


class TelegramBot:
    """
    Bot entity

    Handles messages from Telegram.
    """

    def __init__(self, bot: Bot, dispatcher: Dispatcher) -> None:
        self.bot: Bot = bot
        self.dispatcher = dispatcher

    async def start_polling(self) -> None:
        """Function to start listening to messages from Telegram."""
        logger.info("Bot is waking up...")
        await self.dispatcher.start_polling(self.bot)

    def register_handlers(self) -> None:
        """Registers handlers that respond to user messages to the bot."""
        self.dispatcher.message(CommandStart())(handlers.reply_start_command_message_handler)
        self.dispatcher.message()(handlers.reply_message_handler)

    def register_middleware(self) -> None:
        # https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html
        self.dispatcher.update.outer_middleware()(middleware.request_id_insert_middleware)  # type: ignore


def get_new_bot(bot_token: str) -> TelegramBot:
    """Creates a new instance of a TelegramBot."""
    bot = Bot(token=bot_token)
    dispatcher = Dispatcher()

    bot = TelegramBot(bot, dispatcher)
    bot.register_handlers()
    bot.register_middleware()
    return bot
