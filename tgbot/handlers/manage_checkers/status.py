import logging
from datetime import datetime
from socket import EAI_SERVICE
import asyncio
import json

from name_node import name
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from api.config import nodes
from api.functions import get_index_by_moniker
from api.requests import MintScanner
from schedulers.jobs import add_user_checker
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import Status
from tgbot.keyboards.inline import validator_moniker
from tgbot.keyboards.inline import menu

import os
from api.config import nodes
from api.functions import load_block





@checker_router.callback_query(text="status")
async def create_checker(callback: CallbackQuery, state: FSMContext):
    """Entry point for create checker conversation"""

    # data = await state.get_data()
    # validators = data.get('validators')

    # if validators:
    #     all_valid = [validator["operator_address"] 
    #                  for num, validator in validators.items()]
    #     logging.info(f"{all_valid}")
        # await message.answer("Вибири валідатора:", reply_markup=validator_moniker(all_valid).as_markup())
    await callback.message.edit_text(
    'Let\'s see...\n'
    "The status of which validator do you want to know?"
    )
    

    

    await state.set_state(Status.operator_address)


#
# @checker_router.message(state=CreateChecker.chain)
# async def enter_chain(message: Message, state: FSMContext):
#     """Enter chain name"""
#     data = await state.get_data()
#     if message.text in nodes.keys():
#         data['chain'] = message.text
#
#         await message.answer(
#             'Okay, now I need the name of this validator'
#         )
#         await state.set_state(CreateChecker.operator_address)
#         await state.update_data(data)
#     else:
#         await message.answer(
#             'Sorry, but we dont have this validator\'s network\n'
#             'Try again'
#         )


@checker_router.callback_query(state=Status.operator_address)
async def enter_operator_address(callback: CallbackQuery, state: FSMContext,
                                 scheduler: AsyncIOScheduler,
                                 mint_scanner: MintScanner):
    """Enter validator's name"""
    moniker = callback.text
    data = await state.get_data()
    name_node = name
    validators_data = data.get("validators")
    # validators = await mint_scanner.get_validator(name_node)
    validators = await mint_scanner.get_validators(name_node) # list validators
    logging.info(f'Got {validators} validators')
    
    all_valid_data = [validator["operator_address"] 
                for num, validator in validators_data.items()]
    
    logging.info(f"{all_valid_data}")

    if moniker in all_valid_data :
        validator = get_index_by_moniker(moniker, validators) # index validators
        logging.info(f'Got {validator} {validators[validator]} validators')
        validators = validators[validator]

        if validators["status"] == "BOND_STATUS_BONDED":
            status = "BONDED"
        else:
            status = "UNBONDED"



        await callback.message.edit_text(
            f'status:\n'
            f'    moniker: {validators["description"]["moniker"]}\n'
            f'    Yail: {validators["jailed"]}\n'
            f'    status_validators: {status}\n'
            f'    bot: 🟢 active ' 
        )

    else:
        await callback.message.edit_text('No checkers are currently running.\n'
                             'You can add a checker by selecting create checker in the menu',
        )
        await callback.message.edit_text("\t<b>MENU</b>", reply_markup=menu())
    #     data.setdefault('validators', {})
    #     i = str( len(data.get('validators')) )
    #     for validator_id, validator in data['validators'].items():
    #         if validator['operator_address'] == moniker:
    #             await state.set_state(None)

    #             return await message.answer(
    #                 'You already have this validator in your list'
    #             )
        
    #     logging.info(f'\n\n\n, {data}, \n\n\n')

    #     data['validators'][i] = {
    #         'chain': name_node,
    #         'operator_address': message.text
    #     }
    #     logging.info(f'"\n\n\n", {data}, "\n\n\n"')
    #     print("\n\n\n", data, "\n\n\n")
    #     await message.answer(
    #         'Nice! Now I\'ll be checking this validator all day👌'
    #         )
    #     # await message.send_stiker(message)

    #     await state.set_state(None)
    #     logging.info(f'"\n\n\n", {data}, "\n\n\n"')
    #     await state.update_data(data)

    #     scheduler.add_job(
    #         add_user_checker,
    #         IntervalTrigger(minutes=10),
    #         kwargs={
    #             'user_id': message.from_user.id,
    #             'platform': name_node,
    #             'moniker': moniker,
    #         },
    #         id=f'{message.from_user.id}:{name_node}:{moniker}',
    #         next_run_time=datetime.now()
    #     )

