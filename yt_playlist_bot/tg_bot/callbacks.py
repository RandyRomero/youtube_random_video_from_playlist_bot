from aiogram.filters.callback_data import CallbackData


class OneMoreVideoCallback(CallbackData, prefix="my"):
    """DTO to transfer along with the response to the user with inline keyboard."""

    playlist_id: str
