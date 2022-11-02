import asyncio
import json
import logging
import environs
import math

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import RedisStorage


from api.requests import MintScanner
from schedulers.exceptions import NoSlashingInfo, raise_error
from schedulers.exceptions import raise_error


from name_node import skipped_blocks_allowed, time_jail, name

env = environs.Env()
env.read_env()
ADMIN_ID = env.str("ADMINS")


def two_zero(integer):
    if integer < 10:
        return "0" + str(integer)

    else:
        return integer


# async def add_user_checker(bot: Bot, mint_scanner: MintScanner, #user_id: int, platform: str, moniker: str,
#                            storage: RedisStorage):

#     async def check_block(old_new, new):
#         if old_new >= 29:
#             return 1
#         else:
#             #checkers[str(user_id)][platform][moniker]['last_check'] = new
#             return 0

#     async def check(old, new):
#         right_blocks = await check_block(new - old, new)
#         if right_blocks:
#             old = checkers[str(user_id)][platform][moniker]['last_check']
#             rizn = new - old
#             vidsot_skip_blok = (100 * new) / skipped_blocks_allowed
#             vidsot_time_to_jail = (
#                 ((100 - vidsot_skip_blok) * time_jail) / 100) / 60
#             # return right_blocks, round(vidsot_skip_blok, 2), round(vidsot_time_to_jail)
#             return right_blocks, new, round(vidsot_time_to_jail)
#         else:
#             return 0, 0, 0

    


#     checkers = await storage.redis.get('checkers') or '{}'
#     checkers = json.loads(checkers)
#     logging.info(f"\n\n{checkers}\n\n")
#     if str(user_id) not in checkers:
#         checkers[str(user_id)] = {}

#     # if platform not in checkers[str(user_id)]:
#     #     checkers[str(user_id)][platform] = {}

#     if moniker not in checkers[str(user_id)]:
#         checkers[str(user_id)][moniker] = {
#             'last_check': 0,
#         }

#     last_check = checkers[str(user_id)].get(moniker, {}).get('last_check', 0)

#     data = await mint_scanner.parse_application(platform, moniker)

#     if not data['ok']:
#         await bot.send_message(ADMIN_ID, "Error happened: " + data['error'] + "\n\n" + f'{moniker=}, {platform=}')
#         raise raise_error(data['error'])

#     missed_blocks_counter = data['missed_blocks_counter']
#     consensus_pubkey = data['data']['consensus_pubkey']

#     logging.info(f"Missed blocks counter: {missed_blocks_counter}")
#     logging.info('Sleeping for 180 seconds')

#     await asyncio.sleep(180)
#     data_new = await mint_scanner.get_repeated_missing_blocks(platform, consensus_pubkey)

#     missed_blocks_counter_new = data_new['missed_blocks_counter']
#     logging.info(f"Second missed blocks counter: {missed_blocks_counter_new}")

#     missed_blocks_counter_new, percentages, time_to_jail = await check(missed_blocks_counter, missed_blocks_counter_new)

#     if not missed_blocks_counter_new:
#         await storage.redis.set('checkers', json.dumps(checkers))
#         return

#     elif percentages > (skipped_blocks_allowed * 0.7):
#         await bot.send_message(user_id, f"<b>Moniker: {moniker}.</b>"
#                                f"\nbot: <b>If you don't fix it, your validator will go to jail.</b>"
#                                f"\n    missed_blocks: {percentages}/{skipped_blocks_allowed}"
#                                f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }"
#                                )

#         await storage.redis.set('checkers', json.dumps(checkers))

#     else:
#         await bot.send_message(user_id, f"<b>Moniker: {moniker}.</b>"
#                                f"\nbot: "
#                                f"\n.   missed_blocks: {percentages}/{skipped_blocks_allowed}"
#                                f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }")

#         await storage.redis.set('checkers', json.dumps(checkers))

    #checkers[str(user_id)][platform][moniker]['last_check'] = missed_blocks_counter_new
    # await storage.redis.set('checkers', json.dumps(checkers))


async def add_user_checker(bot: Bot, mint_scanner: MintScanner, #user_id: int, platform: str, moniker: str,
                           storage: RedisStorage):

    logging.info('Я почав розсилку')

    async def check_block(old_new, new):
        if old_new >= 29:
            return 1
        else:
            #checkers[str(user_id)][platform][moniker]['last_check'] = new
            return 0

    async def check(old, new):
        right_blocks = await check_block(new - old, new)
        if right_blocks:
            old = checkers[str(user_id)][moniker]['last_check']
            rizn = new - old
            vidsot_skip_blok = (100 * new) / skipped_blocks_allowed
            vidsot_time_to_jail = (
                ((100 - vidsot_skip_blok) * time_jail) / 100) / 60
            # return right_blocks, round(vidsot_skip_blok, 2), round(vidsot_time_to_jail)
            return right_blocks, new, round(vidsot_time_to_jail)
        else:
            return 0, 0, 0


    checkers = await storage.redis.get('checkers') or '{}'
    checkers = json.loads(checkers)

    if checkers == {}: 
        logging.info("Масив пустий {}")
        logging.info("Я закінчив роз силку")
        return

    else:
        for user_id in checkers:
            for moniker in checkers[str(user_id)]:
                logging.info(f'Оброблюється {user_id} {moniker}')

                last_check = checkers[str(user_id)].get(moniker, {}).get('last_check', 0)

                data = await mint_scanner.parse_application(name, moniker)

                if not data['ok']:
                    await bot.send_message(ADMIN_ID, "Error happened: " + data['error'] + "\n\n" + f'{moniker=}, {name=}')
                    raise raise_error(data['error'])

                missed_blocks_counter = data['missed_blocks_counter']
                consensus_pubkey = data['data']['consensus_pubkey']

                logging.info(f"Missed blocks counter: {missed_blocks_counter}")
                logging.info('Sleeping for 180 seconds')

                await asyncio.sleep(180)
                data_new = await mint_scanner.get_repeated_missing_blocks(name, consensus_pubkey)

                missed_blocks_counter_new = data_new['missed_blocks_counter']
                logging.info(f"Second missed blocks counter: {missed_blocks_counter_new}")

                missed_blocks_counter_new, percentages, time_to_jail = await check(missed_blocks_counter, missed_blocks_counter_new)

                if not missed_blocks_counter_new:
                    await storage.redis.set('checkers', json.dumps(checkers))
                    logging.info("Я закінчив роз силку miss")
                    return

                elif percentages > (skipped_blocks_allowed * 0.7):
                    await bot.send_message(user_id, f"<b>Moniker: {moniker}.</b>"
                                        f"\nbot: <b>If you don't fix it, your validator will go to jail.</b>"
                                        f"\n    missed_blocks: {percentages}/{skipped_blocks_allowed}"
                                        f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }"
                                        )

                    await storage.redis.set('checkers', json.dumps(checkers))

                else:
                    await bot.send_message(user_id, f"<b>Moniker: {moniker}.</b>"
                                        f"\nbot: "
                                        f"\n.   missed_blocks: {percentages}/{skipped_blocks_allowed}"
                                        f"\n    time_before_jail: { two_zero( math.floor(time_to_jail / 60) ) }:{ two_zero( time_to_jail % 60 ) }")

                    await storage.redis.set('checkers', json.dumps(checkers))
                
                logging.info("Я закінчив роз силку full")