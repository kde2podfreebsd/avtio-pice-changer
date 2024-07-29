from bot.config import bot
import os
from dotenv import load_dotenv
from telebot import types
from math import ceil
from avito.chats import AvitoChats
from bot.context import message_context_manager

load_dotenv()

CHATS_PER_PAGE = int(os.getenv("CHATS_PER_PAGE"))

async def chats_menu(message, page=1) -> None:
    await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
    avtio_chats = AvitoChats()
    await avtio_chats.authenticate()
    await avtio_chats.get_chats()
    chats = avtio_chats.chat_ids

    amount_of_pages = ceil(len(chats) / CHATS_PER_PAGE)
    chunks = [chats[i:i + CHATS_PER_PAGE] for i in range(0, len(chats), CHATS_PER_PAGE)]
    data_to_display = chunks[page - 1] if page <= len(chunks) else []

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for chat in data_to_display:
        for chat_id, chat_name in chat.items():
            keyboard.add(types.InlineKeyboardButton(text=chat_name, callback_data=f"chat_{chat_id}"))

    if amount_of_pages != 1:
        back = types.InlineKeyboardButton(
            text="<", callback_data=f"chats_menu#{page - 1 if page - 1 >= 1 else page}"
        )
        page_cntr = types.InlineKeyboardButton(
            text=f"{page}/{amount_of_pages}", callback_data="nullified_{}".format(page)
        )
        forward = types.InlineKeyboardButton(
            text=">", callback_data=f"chats_menu#{page + 1 if page + 1 <= amount_of_pages else page}"
        )
        keyboard.add(back, page_cntr, forward)

    msg = await bot.send_message(
        message.chat.id,
        f'''
<i>Чаты для {message.chat.username if message.chat.username is not None else message.chat.id}!</i>
Список чатов:
''',
        parse_mode="html",
        reply_markup=keyboard
    )

    message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.message_id)

@bot.message_handler(commands=['chats'])
async def chats_menu_handler(message) -> None:
    await chats_menu(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chats_menu'))
async def chats_menu_inline(call) -> None:
    try:
        page = int(call.data.split('#')[1])
    except IndexError:
        page = 1
    await chats_menu(call.message, page)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_'))
async def chat_selected(call):
    chat_id = call.data.split('_')[1]
    await bot.send_message(call.message.chat.id, f"Вы выбрали чат: {chat_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('nullified_'))
async def nullified(call):
    await bot.answer_callback_query(call.id, f"Current page: {call.data}")
