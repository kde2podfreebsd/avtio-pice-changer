from bot.config import bot
from bot.context import message_context_manager
from telebot import types
from avito.user import AvitoUser
from utils import AvitoProfile

@bot.message_handler(commands=['start', 'menu'])
async def start(message) -> None:

    avito_user = AvitoUser()
    await avito_user.authenticate()
    profile: AvitoProfile = await avito_user.get_profile()
    balance = await avito_user.get_balance()

    await message_context_manager.delete_msgId_from_help_menu_dict(message.chat.id)

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    profile_url = types.InlineKeyboardButton(
        text="Профиль", url=profile.profile_url
    )
    chats = types.InlineKeyboardButton(
        text="Чаты", callback_data="chats_menu"
    )
    items = types.InlineKeyboardButton(
        text="Объявления", callback_data="quotes_menu"
    )
    garantex_url = types.InlineKeyboardButton(
            text="Garantex", url="https://garantex.org/"
        )
    keyboard.add(profile_url)
    keyboard.add(chats)
    keyboard.add(items)
    keyboard.add(garantex_url)

    msg = await bot.send_message(
        message.chat.id,
        f'''
id: {profile.id}
name: {profile.name}
email: {profile.email}
phone: {profile.phone}
Баланс: {balance['real']}
Бонусный баланс {balance['bonus']}
''',
        reply_markup=keyboard,
        disable_web_page_preview=True
        )
    message_context_manager.add_msgId_to_help_menu_dict(message.chat.id, msg.message_id)