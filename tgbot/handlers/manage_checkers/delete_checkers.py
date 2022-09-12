import logging
from name_node import name
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.config import nodes
from api.requests import MintScanner
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import DeleteChecker
from tgbot.keyboards.inline import menu, to_menu

def num_data(data, keys_data):
    new_data = dict()
    j =  0 
    logging.info(f"{keys_data}")
    for i in keys_data:
        new_data[str( j )] = data[i]
        j += 1
    return new_data


@checker_router.callback_query(text="delete")
async def create_checker(callback: CallbackQuery, state: FSMContext):
    """Entry point for create checker conversation"""

    await callback.message.edit_text(
        'Let\'s see...\n'
        'What\'s your validator\'s name?'
    )

    await state.set_state(DeleteChecker.operator_address)


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


@checker_router.message(state=DeleteChecker.operator_address)
async def enter_operator_address(callback: CallbackQuery, state: FSMContext,
                                 scheduler: AsyncIOScheduler):
    """Enter validator's name"""
    moniker = callback.text
    data = await state.get_data()
    name_node = name

    validators = data.get('validators', {})
    validator_to_delete = None

    for validator_id, validator in validators.items():
        if validator.get('chain') == name_node and validator.get('operator_address') == moniker:
            validator_to_delete = validator_id
            break

    if validator_to_delete:
        validators.pop(validator_to_delete)
        logging.info(f"{data}")
        validators = num_data(validators, validators.keys())
        logging.info(f"{data}")
        await state.update_data(validators=validators)

        await callback.message.edit_text(
            'Okay, I deleted this checker',
            reply_markup=to_menu()
        )
        scheduler.remove_job(
            job_id=f'{callback.from_user.id}:{name_node}:{moniker}'
        )

    else:
        await callback.message.edit_text(
            'Sorry, but we didn\'t find this validator\n',
            reply_markup=to_menu()
        )

    await state.set_state(None)
