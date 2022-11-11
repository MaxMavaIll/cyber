import asyncio
import logging, json
from datetime import datetime

from name_node import name
from aiogram import Bot
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.dispatcher.fsm.storage.redis import RedisStorage


from api.config import nodes
from api.functions import get_index_by_moniker
from api.requests import MintScanner
from schedulers.jobs import add_user_checker
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import CreateChecker
from tgbot.keyboards.inline import menu, to_menu


@checker_router.callback_query(text="create")
async def create_checker(callback : CallbackQuery, state: FSMContext):
    """Entry point for create checker conversation"""
    
    await state.update_data(id_message=callback.message.message_id)
    

    await callback.message.edit_text(
        'Let\'s see...\n'
        'What\'s your validator name?'
    )

    await state.set_state(CreateChecker.operator_address)


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


@checker_router.message(state=CreateChecker.operator_address)
async def enter_operator_address(message : Message, state: FSMContext,
                                 scheduler: AsyncIOScheduler,
                                 mint_scanner: MintScanner, bot : Bot, storage: RedisStorage):
    """Enter validator's name"""
    await asyncio.sleep(1)
    await message.delete()
    moniker = message.text

    
    data = await state.get_data()
    id_message=data["id_message"]
    del data["id_message"]
    
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    logging.info(f"\nchecker = {checkers}\n id_message = {id_message}\n")
    

    name_node = name
    validators = await mint_scanner.get_validators(name_node)
    logging.info(f'Got {len(validators)} validators')


    if get_index_by_moniker(moniker, validators) is None:
        await bot.edit_message_text(
            'Sorry, but I don\'t found this validator', chat_id=message.from_user.id,
            message_id=id_message,
            reply_markup=to_menu()
        )
        await state.set_state(None)
    else: 
        
        data.setdefault('validators', {})
        for validator_id, validator in data['validators'].items():
            if validator['operator_address'] == moniker:
                

                await bot.edit_message_text(
                    'You already have this validator in your list', chat_id=message.from_user.id,
                    message_id=id_message,
                    reply_markup=to_menu()
                )
                
                return
        if 'all_missed' not in checkers and 'miss_all_blocks' not in checkers:
            checkers = {'all_missed' : None, "miss_all_blocks": None}
            logging.debug(checkers)
            

        if 'validators' not in checkers:
            checkers['validators'] = {}
            logging.debug(checkers)


        if str(message.from_user.id) not in checkers['validators']:
            checkers['validators'][str(message.from_user.id)] = {}
            logging.debug(checkers)


        # cons = {"@type": "/cosmos.crypto.ed25519.PubKey",
        # "key": validators[get_index_by_moniker(moniker, validators)].get("consensus_pubkey").get("key")
        # }

        if moniker not in checkers['validators'][str(message.from_user.id)]:
            checkers['validators'][str(message.from_user.id)][message.text] = {
                'last_check': 0, 'addr_cons': None
            }
            logging.debug(checkers)
            


        i = str( len(data.get('validators')) )
        # if checkers.get() != {}:
        data['validators'][i] = {
            'chain': name_node,
            'operator_address': message.text
        }
        # else:
        #     data['validators'][i] = {
        #         'chain': name_node,
        #         'operator_address': message.text,
        #         'last_time': ""
        #     }
        
        
        # with open("cache/data.json", "r") as file:
        #     data_send = json.load(file)

        # if str(message.from_user.id) not in data_send.keys():
        #     data_send[str(message.from_user.id)]=[]

        # data_send[str(message.from_user.id)].append(moniker)
        
        # with open("cache/data.json", "w") as file:
        #     json.dump( data_send, file)

        
        await bot.edit_message_text( 
            f'Nice! Now I\'ll be checking this validator all day : {moniker}👌', chat_id=message.from_user.id,
            message_id=id_message,
            reply_markup=to_menu()
            )
        logging.info(f'{checkers} {data}')
        await state.set_state(None)
        await state.update_data(data)
        await storage.redis.set('checkers', json.dumps(checkers))
        
        

        

