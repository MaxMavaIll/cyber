import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from api.requests import MintScanner
from schedulers.base import setup_scheduler
from tgbot.config import load_config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.manage_checkers import checker_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services import broadcaster


from schedulers.jobs import add_user_checker
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime


logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, 'I\'m running')


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage.from_url(config.redis_config.dsn(), key_builder=DefaultKeyBuilder(with_bot_id=True))

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    mint_scanner = MintScanner(base_api_uri=config.mint_scan_api.base_url, api_token=config.mint_scan_api.token)
    scheduler = setup_scheduler(bot, config, mint_scanner, storage)
    for router in [
        admin_router,
        checker_router,

        user_router,
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)
    bot.edit_message_text("sdfsdf", chat_id=None)
    dp['bot'] = bot
    dp['scheduler'] = scheduler
    dp['mint_scanner'] = mint_scanner
    dp['storage'] = storage

    
    


    await on_startup(bot, config.tg_bot.admin_ids)
    scheduler.start()
    
    scheduler.add_job(
            add_user_checker,
            IntervalTrigger(minutes=10),
            # kwargs={
            #     'user_id': message.from_user.id,
            #     'platform': name_node,
            #     'moniker': moniker,
            # },
            next_run_time=datetime.now(),
            replace_existing=True
        )

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('I was stopped')
