from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def validator_moniker(validator_moniker):

    builder = InlineKeyboardButton()
    for num in range(len(validator_moniker)+1) :
        builder.add( text="mama", callback_data="de2" )

    return builder