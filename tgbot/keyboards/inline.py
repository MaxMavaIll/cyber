from distutils.command.build import build
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="create checker", callback_data="create")
    builder.button(text="list", callback_data="list")
    builder.button(text="delete checker", callback_data="delete")
    builder.button(text="status", callback_data="status")
    builder.button(text="gov", callback_data="gov")
    builder.adjust(2)

    return builder.as_markup()

def validator_moniker(validator_moniker):

    builder = InlineKeyboardBuilder()
    for num in len(validator_moniker) :
        builder.add( text=validator_moniker[num], callback_data=num )

    return builder.as_markup()