import json, logging

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

from api.functions import get_index_by_network
from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.keyboards.inline import to_menu


@checker_router.callback_query(text="list")
async def list_my_validators(callback: CallbackQuery, state: FSMContext, storage: RedisStorage):
    """List all registered validators"""

    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)
    data = await state.get_data()
    validators = data.get('validators')

    logging.info(f'\n{validators}\n')

    if checkers != {}:
        mass = get_index_by_network(checkers['validators'], user_id=callback.from_user.id)
       

    if validators:
        output = ''
        for network in mass:
            output = output + f'\n\n{network}\n'


            for chain in mass[network].keys():
                output = output + f'    <b>{chain.title()}</b>\n'
                
                
                for index,  moniker in enumerate(mass[network][chain][str(callback.from_user.id)], 1):
                
                    output = output + f'        {index}. {moniker}\n'


        # for network in mass:
        #     for index, monikers in enumerate(mass[network].values(), 1):
        #         for chains in mass[network].keys():
        #             for moniker in monikers:
                    
        #                 Network = f'\n'.

        #                 validators_str = 'I\'m checking the following validators:\n\n'
        #                 validators_str = validators_str + '\n'.join([
        #                     f'{num}. {validator["chain"]} {validator["operator_address"]}\n'
        #                     for num, validator in enumerate(validators.values(), 1)
        #                 ]
        #                 )

        await callback.message.edit_text(output,
                                        reply_markup=to_menu())
    else:
        await callback.answer(
            'Sorry, but I didn\'t find any checker. \n'
            'First, create a checker',
            # show_alert=True
        )

    
