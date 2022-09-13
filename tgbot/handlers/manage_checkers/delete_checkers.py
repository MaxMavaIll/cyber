import logging
from name_node import name
from aiogram import Bot
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.config import nodes
from api.requests import MintScanner
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import DeleteChecker
from tgbot.keyboards.inline import menu, to_menu, list_validators

def num_data(data, keys_data):
    new_data = dict()
    j =  0 
    logging.info(f"{keys_data}")
    for i in keys_data:
        new_data[str( j )] = data[i]
        j += 1
    return new_data

id_message = {}

# @checker_router.callback_query(text="delete")
# async def create_checker(callback: CallbackQuery, state: FSMContext):
#     """Entry point for create checker conversation"""

#     id_message[callback.from_user.id] = callback.message.message_id


#     await callback.message.edit_text(
#         'Let\'s see...\n'
#         'What\'s your validator\'s name?'
#     )

#      await state.set_state(DeleteChecker.operator_address)


@checker_router.callback_query(text="delete")
async def create_checker(callback: CallbackQuery, state: FSMContext):
    """Entry point for create checker conversation"""

    data = await state.get_data()
    name_node = name

    validators = data.get('validators', {})
    validators = [f'{validator["operator_address"]}'
            for num, validator in enumerate(validators.values(), 1)]

    if validators:
        await callback.message.edit_text(
            'Let\'s see...\n'
            'What\'s your validator\'s name?',
            reply_markup=list_validators(validators, "delete")
        )
    
    else:
        await callback.answer(
            'Sorry, but I didn\'t find any checker. \n'
            'First, create a checker',
            # show_alert=True
        )
    # await state.set_state(DeleteChecker.operator_address)


#
#
# @checker_router.message(state=DeleteChecker.chain)
# async def enter_chain(message: Message, state: FSMContext):
#     """Enter chain name"""
#     data = await state.get_data()
#     if message.text in nodes.keys():
#         data['chain'] = message.text
#
#         await message.answer(
#             'Okay, now I need the name of this validator'
#         )
#         await state.set_state(DeleteChecker.operator_address)
#         await state.update_data(data)
#     else:
#         await message.answer(
#             'Sorry, but we dont have this validator\'s network\n'
#             'Try again'
#         )

@checker_router.callback_query(Text(text_startswith="delete_"))
async def enter_operator_address(callback: CallbackQuery, state: FSMContext,
                                 scheduler: AsyncIOScheduler, bot: Bot):
    """Enter validator's name"""
    moniker = callback.data.split("_")[-1]
    data = await state.get_data()
    name_node = name

    validators = data.get('validators', {})
    validator_to_delete = None

    for validator_id, validator in validators.items():
        if validator.get('chain') == name_node and validator.get('operator_address') == moniker:
            validator_to_delete = validator_id
            break

    
    validators.pop(validator_to_delete)
    validators = num_data(validators, validators.keys())
    await state.update_data(validators=validators)

    await callback.message.edit_text(
        f'Okay, I deleted this checker : {moniker}',
        reply_markup=to_menu()
    )
    scheduler.remove_job(
        job_id=f'{callback.from_user.id}:{name_node}:{moniker}'
    )

    

    await state.set_state(None)


# @checker_router.message(state=DeleteChecker.operator_address)
# async def enter_operator_address(message: Message, state: FSMContext,
#                                  scheduler: AsyncIOScheduler, bot: Bot):
#     """Enter validator's name"""
#     moniker = message.text
#     data = await state.get_data()
#     name_node = name

#     validators = data.get('validators', {})
#     validator_to_delete = None

#     for validator_id, validator in validators.items():
#         if validator.get('chain') == name_node and validator.get('operator_address') == moniker:
#             validator_to_delete = validator_id
#             break

#     if validator_to_delete:
#         validators.pop(validator_to_delete)
#         logging.info(f"{data}")
#         validators = num_data(validators, validators.keys())
#         logging.info(f"{data}")
#         await state.update_data(validators=validators)

#         await bot.edit_message_text(
#             'Sorry, but I don\'t found this validator', chat_id=message.from_user.id,
#             message_id=id_message[message.from_user.id],
#             reply_markup=to_menu()
#         )

#         await bot.edit_message_text(
#             'Okay, I deleted this checker', chat_id=message.from_user.id,
#             message_id=id_message[message.from_user.id],
#             reply_markup=to_menu()
#         )
#         scheduler.remove_job(
#             job_id=f'{message.from_user.id}:{name_node}:{moniker}'
#         )

#     else:
#         await bot.edit_message_text(
#             'Sorry, but we didn\'t find this validator\n',
#             reply_markup=to_menu()
#         )

#     await state.set_state(None)
