import logging
from datetime import datetime
from socket import EAI_SERVICE
import asyncio
import json

from aiogram import Bot
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from api.config import nodes
from api.functions import get_index_by_moniker, get_index_by_network
from api.requests import MintScanner
from schedulers.jobs import add_user_checker
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import Status
from tgbot.keyboards.inline import validator_moniker
from tgbot.keyboards.inline import *


import os
from api.config import nodes
from api.functions import load_block



    
    
@checker_router.callback_query(text="status")
async def create_checker(callback: CallbackQuery, state: FSMContext, storage: RedisStorage):
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    if checkers != {}:
        checkers = checkers['validators'] 

        copy_validators = get_index_by_network(checkers, callback.from_user.id)
        await state.update_data(copy_validators=copy_validators)
    else:
        copy_validators = {}

        
    if copy_validators != {} :
        
        await callback.message.edit_text(
                '<b>Network</b>\n',
                reply_markup=list_validators(list(copy_validators.keys()), "status_network")
            )
    else:
        await callback.answer(
            'Sorry, but I didn\'t find any checker. \n'
            'First, create a checker',
            # show_alert=True
        )

@checker_router.callback_query(Text(text_startswith="status_network&"))
async def chain(callback: CallbackQuery, state: FSMContext, storage: RedisStorage, bot: Bot):
    """Entry point for create checker conversation"""

    network = callback.data.split("&")[-1]
    await state.update_data(network=network)
    data = await state.get_data()
    data_cp = data['copy_validators']

    logging.info(f'data {data_cp}')
    logging.info(f'data {data_cp[network].keys()}')


    await bot.edit_message_text(
        '<b>Node</b>',
        message_id=data['id_message'],
        chat_id=callback.from_user.id,
        reply_markup=list_validators(list(data_cp[network].keys()), "status_chain" )
    )
    
@checker_router.callback_query(Text(text_startswith="status_chain&"))
async def monikers(callback: CallbackQuery, state: FSMContext, storage: RedisStorage, bot: Bot):
    chain = callback.data.split("&")[-1]
    await state.update_data(chain=chain)
    data = await state.get_data()

    await bot.edit_message_text(
        'Let\'s see...\n'
        "The status of which validator do you want to know?",
        message_id=data['id_message'],
        chat_id=callback.from_user.id,
        reply_markup=list_validators_back(data['copy_validators'][data['network']][chain][str(callback.from_user.id)], "status_moniker", "status_network", chain)
    )
    
    

    



@checker_router.callback_query(Text(text_startswith="status_moniker&"))
async def enter_operator_address(callback: CallbackQuery, state: FSMContext,
                                 scheduler: AsyncIOScheduler,
                                 mint_scanner: MintScanner):
    """Enter validator's name"""
    moniker = callback.data.split("&")[-1]
    data = await state.get_data()


    name_node = data['chain']
    
    
    
    # validators = await mint_scanner.get_validator(name_node)
    validators = await mint_scanner.get_validators(name_node) # list validators
    validator = get_index_by_moniker(moniker, validators) # index validators
    data_new = await mint_scanner.parse_application(name_node, moniker)
    logging.info(data_new['missed_blocks_counter'])
    missed_blocks_counter = int(data_new['missed_blocks_counter'])
    logging.info(f'Got {validator} {validators[validator]} validators')
    validators = validators[validator]

    if validators["jailed"]:
        validators["jailed"] = '🔴 true'
    else:
        validators["jailed"] = '🟢 false'

    if validators["status"] == "BOND_STATUS_BONDED":
        status = "🟢 BONDED"
    else:
        status = "🔴 UNBONDED"

    await callback.message.answer(
        f'status: '
        f'\n    moniker: {validators["description"]["moniker"]}'
        f'\n    voting power: {validators["tokens"]}'
        f'\n    Jailed:  {validators["jailed"]}'
        f'\n    validators status: {status}'
        f'\n    missed blocks: {missed_blocks_counter}',
        # show_alert=True, 
    )