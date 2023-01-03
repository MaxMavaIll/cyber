import asyncio
import logging, json
from datetime import datetime

from api.config import chains
from aiogram import Bot
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.dispatcher.fsm.storage.redis import RedisStorage


# from api.config import nodes
from api.functions import get_index_by_moniker
from api.requests import MintScanner
from schedulers.jobs import add_user_checker
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.misc.states import CreateChecker
from tgbot.keyboards.inline import menu, to_menu, list_validators, list_validators_back


@checker_router.callback_query(text="create")
async def change_network(callback : CallbackQuery, state: FSMContext):
    logging.info(f'Chains {chains.keys()}')
    
    await state.update_data(id_message=callback.message.message_id)
    await callback.message.edit_text("Please select a network",
                            reply_markup=list_validators(['Mainnet', 'Testnet'], 'network'))
        


@checker_router.callback_query(Text(text_startswith="network&"))
async def change_chain(callback : CallbackQuery, state: FSMContext, bot: Bot):
    
    logging.info(f'network {chains.keys()}')
    network = callback.data.split("&")[-1]
    logging.info(f'network {network}')
    data = await state.get_data()
    if network == 'back':
        network = data["network"]
    else:
        await state.update_data(network=network)
    n = chains[network].keys()
    logging.info(f'Chains {chains.keys()} {n}')
    
    if chains[network] != {}:
        await  bot.edit_message_text("Please select a chain",
                                chat_id=callback.from_user.id,
                                message_id=data['id_message'],
                                reply_markup=list_validators_back(list(chains[network].keys()), 'chain', 'create' )
                                #reply_markup=list_validators(list(chains[network].keys()), 'chain'))
                                )
    else:
        await  bot.edit_message_text(f"There are currently no <b>{network} networks</b> available",
                                chat_id=callback.from_user.id,
                                message_id=data['id_message'],
                                reply_markup=to_menu())

@checker_router.callback_query(Text(text_startswith="chain&"))
async def create_checker(callback : CallbackQuery, state: FSMContext, bot: Bot):
    """Entry point for create checker conversation"""
    
    chain = callback.data.split("&")[-1]
    data = await state.get_data()
    if chain == 'back':
        chain = data["chain"]
    else:
        await state.update_data(chain=chain)
    
    await bot.edit_message_text(
        'Let\'s see...\n'
        'What\'s your validator name?',
        chat_id=callback.from_user.id,
        message_id=data['id_message'],
        reply_markup=to_menu(back=True, text='Try another platform', back_to='network&back')
    )

    await state.set_state(CreateChecker.operator_address)



@checker_router.message(state=CreateChecker.operator_address)
async def enter_operator_address(message : Message, state: FSMContext,
                                 scheduler: AsyncIOScheduler,
                                 mint_scanner: MintScanner, bot : Bot, storage: RedisStorage):

    await asyncio.sleep(1)
    await message.delete()
    moniker = message.text

    
    data = await state.get_data()
    id_message=data["id_message"]
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    logging.info(f"\nchecker = {checkers} \nid_message = {id_message} \ndata {data}")
    
    del data["id_message"]

    
    validators = await mint_scanner.get_validators(data['chain'])
    logging.info(f'Got {len(validators)} validators')


    if get_index_by_moniker(moniker, validators) is None:
        await bot.edit_message_text(
            'Sorry, but I don\'t found this validator',
            chat_id=message.from_user.id,
            message_id=id_message,
            reply_markup=to_menu(back=True, text='Try again', back_to='chain&back')
        )
        await state.set_state(None)
    else: 
        
        data.setdefault('validators', {})
        for validator_id, validator in data['validators'].items():
            if validator['operator_address'] == moniker and validator['chain'] == data['chain']:
                

                await bot.edit_message_text(
                    'You already have this validator in your list', chat_id=message.from_user.id,
                    message_id=id_message,
                    reply_markup=to_menu(back=True, text='Try again', back_to='chain&back')
                )
                await state.set_state(None)
                return

        logging.debug(f'Start add')
        if 'all_missed' not in checkers and 'miss_all_blocks' not in checkers:
            checkers = {'all_missed' : None, "miss_all_blocks": None}
            logging.debug(f'all_missed {checkers}')
            

        if 'validators' not in checkers:
            checkers['validators'] = {}
            logging.debug(f'validators {checkers}')


        if data['network'] not in checkers['validators']:
            checkers['validators'][data['network']] = {}
            logging.debug(f'network {checkers}')

        if data['chain'] not in checkers['validators'][data['network']]:
            checkers['validators'][data['network']][data['chain']] = {}
            logging.debug(f'chain {checkers}')


        if str(message.from_user.id) not in checkers['validators'][data['network']][data['chain']]:
            checkers['validators'][data['network']][data['chain']][str(message.from_user.id)] = {}
            logging.debug(f'id {checkers}')


        # cons = {"@type": "/cosmos.crypto.ed25519.PubKey",
        # "key": validators[get_index_by_moniker(moniker, validators)].get("consensus_pubkey").get("key")
        # }

        if moniker not in checkers['validators'][data['network']][data['chain']][str(message.from_user.id)]:
            checkers['validators'][data['network']][data['chain']][str(message.from_user.id)][message.text] = {
                'last_check': 0, 'addr_cons': None
            }
            logging.debug(f'moniker {checkers}')

            


        i = str( len(data.get('validators')) )
        # if checkers.get() != {}:
        data['validators'][i] = {
            'chain': data['chain'],
            'operator_address': message.text
        }


        
        await bot.edit_message_text( 
            f'Nice! Now I\'ll be checking this validator all day : {moniker}👌', chat_id=message.from_user.id,
            message_id=id_message,
            reply_markup=to_menu(back=True, text='Try again', back_to='chain&back')
            )
        logging.debug(f'{checkers} {data}')
        await state.set_state(None)
        await state.update_data(data)
        await storage.redis.set('checkers', json.dumps(checkers))
        
        

        

