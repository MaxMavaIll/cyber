from cgitb import text
from aiogram import Router
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import menu

user_router = Router()


@user_router.message(commands=["start"])
async def user_start(message: Message):
    # await message.answer_sticker(sticker="sticker/cyberG.webp")
    await message.answer(f'Hello, {message.chat.first_name}! \n'
                        '\n'
                        'You can add validator checker through /create_checker command. \n'
                        ' - This will make me check this validator for missing blocks. \n'
                        'You can show your validator checker through /list_checker command.\n'
                        'You can delete your validator checker through /delete_checker command.\n'
                        '\n'
                        'Hey, if you like this bot, you can delegate funds to the web34ever validator.', reply_markup= menu())

@user_router.callback_query(text="menu")
async def Menu(callback: CallbackQuery):
    await callback.message.edit_text("<b>Menu</b>", reply_markup=menu())