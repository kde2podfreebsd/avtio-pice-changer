from typing import Optional, Dict, List
from bot.config import bot

class MessageContextManager:
    _instance: Optional['MessageContextManager'] = None

    def __new__(cls, *args, **kwargs) -> 'MessageContextManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.help_menu_msgId_to_delete: Dict[int, List[int]] = {}

    def add_msgId_to_help_menu_dict(self, chat_id: int, msgId: int) -> None:
        self.help_menu_msgId_to_delete.setdefault(chat_id, []).append(msgId)

    async def delete_msgId_from_help_menu_dict(self, chat_id: int) -> None:
        try:
            msg_ids = self.help_menu_msgId_to_delete.pop(chat_id, [])
            for msg_id in msg_ids:
                await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            raise Exception(f"Не удалось удалить сообщения: {chat_id}, {msg_ids} | Exception: {e}")

message_context_manager: MessageContextManager = MessageContextManager()