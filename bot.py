import os
import asyncio
import logging
from math import ceil
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from db import QuoteController
from typing import Dict, List, Optional
import datetime
from utils import ItemStatus
from avito import AvitoCore

logging.basicConfig(level=logging.INFO)

load_dotenv()

bot = AsyncTeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
qc = QuoteController(os.getenv('DB_PATH'))
QUOTES_PER_PAGE = int(os.getenv("QUOTES_PER_PAGE"))

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

async def main_menu(message, page=1) -> None:
    await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)
    if message.chat.id in [int(x) for x in os.getenv("ADMIN_CHATIDS").replace("[", "").replace("]", "").replace(" ", "").split(",")]:
        all_ads = qc.get_all_ads()
        amount_of_pages = ceil(len(all_ads) / QUOTES_PER_PAGE)

        chunks = [all_ads[i:i + QUOTES_PER_PAGE] for i in range(0, len(all_ads), QUOTES_PER_PAGE)]
        data_to_display = chunks[page - 1] if page <= len(chunks) else []

        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for ad in data_to_display:
            keyboard.add(types.InlineKeyboardButton(text=ad[6], callback_data=f"quote_{ad[0]}"))
        
        if amount_of_pages != 1:
            back = types.InlineKeyboardButton(
                text="<", callback_data=f"main_menu#{page - 1 if page - 1 >= 1 else page}"
            )
            page_cntr = types.InlineKeyboardButton(
                text=f"{page}/{amount_of_pages}", callback_data="nullified_{}".format(page)
            )
            forward = types.InlineKeyboardButton(
                text=">", callback_data=f"main_menu#{page + 1 if page + 1 <= amount_of_pages else page}"
            )
            keyboard.add(back, page_cntr, forward)

        update_all_prices = types.InlineKeyboardButton(
            text='Обновить цену всем объявлениям', callback_data="update_all_prices"
        )
        keyboard.add(update_all_prices)

        garantex_url = types.InlineKeyboardButton(
            text="Garantex", url="https://garantex.org/"
        )
        keyboard.add(garantex_url)

        msg = await bot.send_message(
            message.chat.id,
            f'''
<i>Allowed for {message.chat.username if message.chat.username is not None else message.chat.id}!</i>
BTC price on {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}: {qc.get_current_btc_price()}₽
Последнее время обновления: {datetime.datetime.strptime(qc.get_last_time_update_for_all_quotes(), "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y %H:%М:%S")}
<b>Объявления:</b>
''',
            parse_mode="html",
            reply_markup=keyboard
        )
        message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.message_id)
    else:
        await bot.send_message(message.chat.id, '<b>Access denied</b>', parse_mode="html")

@bot.message_handler(commands=['start'])
async def start(message) -> None:
    await main_menu(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('main_menu'))
async def main_menu_inline(call) -> None:
    try:
        page = int(call.data.split('#')[1])
    except IndexError:
        page = 1
    await main_menu(call.message, page)

def prepare_quote_message(avito_id):
    quote = qc.get_ad_by_avito_id(avito_id=avito_id)
    message = f'''
Название объявления: {quote[6]}
Avito ID: {quote[0]}
Адрес: {quote[1]}
Категория: {quote[2]}
Цена RUB: {quote[3]} ₽
Цена BTC: {qc.get_current_btc_price()} ₿
Соотношение цен rub/btc: {round(quote[4], 5)}
Avito статус: {'✅ Active' if quote[5] == ItemStatus.ACTIVE.value else f'❌ {quote[5]}'}

Статус запросов: {'✅ Active' if quote[9] else f'❌ Disabled'}
Последнее время обновления: {datetime.datetime.strptime(quote[8], "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y %H:%М:%S")}
'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="🔗 Item URL", url=quote[7]),
        types.InlineKeyboardButton(text=f"Status: {'✅ Active' if quote[9] else f'❌ Disabled'}", callback_data=f"change_status_{avito_id}"),
        types.InlineKeyboardButton(text="🔄 Обновить цену", callback_data=f"updateprice_{avito_id}"),
        types.InlineKeyboardButton(text="🔙 Back", callback_data="main_menu#1")
    )
    return message, keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('quote_'))
async def callback_quote_inline(call):
    await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    avito_id = qc.get_ad_by_avito_id(avito_id=call.data.split('_')[1])[0]
    message, keyboard = prepare_quote_message(avito_id)
    msg = await bot.send_message(call.message.chat.id, message, reply_markup=keyboard)
    message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('nullified_'))
async def nullified(call):
    await bot.answer_callback_query(call.id, f"Current page: {call.data}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_status_'))
async def change_status(call):
    await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
    avito_id = call.data.split('_')[2]
    if qc.update_quotes_status(avito_id):
        await bot.answer_callback_query(call.id, "Status updated successfully!")
    else:
        await bot.answer_callback_query(call.id, "Failed to update status.")

    message, keyboard = prepare_quote_message(avito_id)

    msg = await bot.send_message(call.message.chat.id, message, reply_markup=keyboard)
    message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('updateprice_'))
async def change_status(call):
    avito = AvitoCore()
    await avito.authenticate()
    avito_id = call.data.split('_')[1]
    qc.update_prices()
    price = await avito.update_price(avito_id)
    if isinstance(price, int):
        await message_context_manager.delete_msgId_from_help_menu_dict(call.message.chat.id)
        await bot.answer_callback_query(call.id, "Status updated successfully!")
        message, keyboard = prepare_quote_message(avito_id)
        msg = await bot.send_message(call.message.chat.id, message, reply_markup=keyboard)
        message_context_manager.add_msgId_to_help_menu_dict(call.message.chat.id, msg.message_id)

    else:
        await bot.answer_callback_query(call.id, "Failed to update status.")

@bot.callback_query_handler(func=lambda call: call.data == 'update_all_prices')
async def update_all_prices(call):
    avito = AvitoCore()
    if await avito.update_items_price():
        qc.update_last_time_update_for_all_quotes()
        await bot.answer_callback_query(call.id, "Prices updated successfully!")
        await main_menu(call.message)
    else:
        await bot.answer_callback_query(call.id, "Failed to update prices.")
    
if __name__ == '__main__':
    qc.create_quote_table()
    asyncio.run(bot.polling())
