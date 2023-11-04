import concurrent.futures
import random
import time

import requests
from loguru import logger
from pysui import SuiConfig

from config import BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC, SUILETTE_COUNT_PER_SESSION, SHUFFLE_ACCOUNTS
from datatypes.sui import SuiletteColor
from utils.add_logger import add_logger
from utils.other import short_address, read_mnemonics
from utils.sui import merge_sui_coins, get_sui_balance, play_suilette_tx, get_list_of_sui_configs


def main_play_game(sui_config: SuiConfig):
    try:
        merge_sui_coins(sui_config=sui_config)
        balance = get_sui_balance(sui_config=sui_config)

        bet_amount = 1
        if balance.float > bet_amount:
            color_index = random.choice(list(SuiletteColor))

            while True:
                response = requests.get('https://www.suilette.com/api/sui-game')
                game_object_id = response.json()['result']['game_object_id']

                result = play_suilette_tx(sui_config=sui_config,
                                          color_index=color_index.value,
                                          game_object_id=game_object_id,
                                          bet_amount=bet_amount)
                if not result.digest:
                    time.sleep(3)
                    continue
                else:
                    sleep = 0
                    if result.reason:
                        if result.digest:
                            sleep = random.randint(BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[0],
                                                   BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
                            logger.error(
                                f'{short_address(result.address)} | {color_index.name} | digest: {result.digest} | '
                                f'reason: {result.reason} | sleep: {sleep}s.')
                        else:
                            logger.error(
                                f'{short_address(result.address)} | {color_index.name} | '
                                f'reason: {result.reason}.')
                    else:
                        sleep = random.randint(BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[0],
                                               BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
                        logger.info(f'{short_address(result.address)} | {color_index.name} | digest: {result.digest} | '
                                    f'sleep: {sleep}s.')

                time.sleep(sleep)
                break

        else:
            logger.warning(f'{short_address(str(sui_config.active_address))} | '
                           f'balance is not enough: {balance.float} $SUI. '
                           f'minimum required: {bet_amount} $SUI.')
            return 'zero_balance'
    except Exception as e:
        logger.exception(e)


def single_executor(sui_config: SuiConfig):
    try:
        unique_sleep = random.randint(BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[0], BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
        logger.info(f'{str(sui_config.active_address)} | SUILETTE | sleep: {unique_sleep} sec.')
        time.sleep(unique_sleep)

        flips_per_session = random.randint(SUILETTE_COUNT_PER_SESSION[0], SUILETTE_COUNT_PER_SESSION[1])
        broken = False
        for _ in range(flips_per_session):
            play_game_result = main_play_game(
                sui_config=sui_config
            )
            if play_game_result == 'zero_balance':
                broken = True
                break

        if not broken:
            logger.success(f'{str(sui_config.active_address)} | has suiletted {flips_per_session} games.')
    except Exception as e:
        logger.exception(e)


def run_suilette_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


if __name__ == '__main__':
    add_logger()
    try:
        mnemonics = read_mnemonics(path='data/mnemonic.txt')
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)
        if sui_configs:
            if SHUFFLE_ACCOUNTS:
                random.shuffle(sui_configs)
            run_suilette_executor(sui_configs=sui_configs)
        else:
            logger.info('all accounts meet the requirements.')
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
