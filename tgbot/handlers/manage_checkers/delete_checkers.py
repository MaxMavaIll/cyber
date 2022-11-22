import logging, json

from aiogram import Bot
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

from api.functions import get_index_by_network

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




@checker_router.callback_query(text="delete")
async def create_checker(callback: CallbackQuery, state: FSMContext, storage: RedisStorage):
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    data = await state.get_data()
    validators = data.get('validators')   
         

    if checkers != {}:
        logging.info(f'{checkers}')
        copy_validators = get_index_by_network(checkers['validators'], callback.from_user.id)
        await state.update_data(copy_validators=copy_validators)
        
    
    if validators:
        await callback.message.edit_text(
                '<b>Network</b>\n',
                reply_markup=list_validators(list(copy_validators.keys()), "delete_network")
            )
    else:
        await callback.answer(
            'Sorry, but I didn\'t find any checker. \n'
            'First, create a checker',
            # show_alert=True
        )


@checker_router.callback_query(Text(text_startswith="delete_network&"))
async def chain(callback: CallbackQuery, state: FSMContext, storage: RedisStorage, bot: Bot):
    """Entry point for create checker conversation"""

    network = callback.data.split("&")[-1]
    await state.update_data(network=network)
    data = await state.get_data()



    await bot.edit_message_text(
        '<b>Node</b>',
        message_id=data['id_message'],
        chat_id=callback.from_user.id,
        reply_markup=list_validators(list(data['copy_validators'][network].keys()), "delete_chain")
    )

@checker_router.callback_query(Text(text_startswith="delete_chain&"))
async def create_checker(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Entry point for create checker conversation"""

    chain = callback.data.split("&")[-1]
    await state.update_data(chain=chain)
    data = await state.get_data()
    
    await bot.edit_message_text(
        'Let\'s see...\n'
        'What\'s your validator\'s name?',
        message_id=data['id_message'],
        chat_id=callback.from_user.id,
        reply_markup=list_validators(data['copy_validators'][data['network']][chain][str(callback.from_user.id)], "delete_moniker")
    )

@checker_router.callback_query(Text(text_startswith="delete_moniker&"))
async def enter_operator_address(callback: CallbackQuery, state: FSMContext,
                                 scheduler: AsyncIOScheduler, bot: Bot, storage: RedisStorage):
    """Enter validator's name"""

   
    moniker = callback.data.split("&")[-1]
    data = await state.get_data()
    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    name_node = data['chain']
    logging.debug(f"checkers {checkers} \ndata {data} \n{moniker} \n{name_node}")


    validators = data.get('validators', {})
    validator_to_delete = None

    for validator_id, validator in validators.items():
        if validator.get('chain') == name_node and validator.get('operator_address') == moniker:
            validator_to_delete = validator_id
            validators.pop(validator_to_delete)
            del checkers['validators'][data['network']][data['chain']][str(callback.from_user.id)][moniker]

            break

    
    
    validators = num_data(validators, validators.keys())
    

    await callback.message.edit_text(
        f'Okay, I deleted this checker : {moniker}',
        reply_markup=to_menu()
    )
    # scheduler.remove_job(
    #     job_id=f'{callback.from_user.id}:{name_node}:{moniker}'
    # )

    
    logging.debug(f"{checkers}\n{data}")
    await state.update_data(validators=validators)
    await state.set_state(None)
    await storage.redis.set('checkers', json.dumps(checkers))



