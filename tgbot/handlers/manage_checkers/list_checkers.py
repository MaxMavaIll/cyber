from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.handlers.manage_checkers.router import checker_router
from tgbot.keyboards.inline import menu, to_menu

@checker_router.callback_query(text="list")
async def list_my_validators(callback: CallbackQuery, state: FSMContext):
    """List all registered validators"""

    data = await state.get_data()
    validators = data.get('validators')

    if validators:
        validators_str = 'I\'m checking the following validators:\n\n'
        validators_str = validators_str + '\n'.join([
            f'{num}. {validator["chain"]} {validator["operator_address"]}\n'
            for num, validator in enumerate(validators.values(), 1)
        ]
        )
        await callback.message.edit_text(validators_str,
                                        reply_markup=to_menu())
    else:
        await callback.answer(
            'Sorry, but I didn\'t find any checker. \n'
            'First, create a checker',
            # show_alert=True
        )

    
