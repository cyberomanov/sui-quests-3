import concurrent.futures
import random
import time

from loguru import logger
from pysui import SuiConfig

from config import BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC, COINFLIP_COUNT_PER_SESSION, SHUFFLE_ACCOUNTS
from datatypes.sui import CoinflipSide
from utils.add_logger import add_logger
from utils.explorer import get_associated_kiosk, get_bullshark_id
from utils.other import short_address, read_mnemonics
from utils.sui import merge_sui_coins, get_sui_balance, play_coinflip_tx, get_list_of_sui_configs


def main_play_game(sui_config: SuiConfig, associated_kiosk_addr: str, bullshark_addr: str, bullshark: bool = True):
    try:
        merge_sui_coins(sui_config=sui_config)
        balance = get_sui_balance(sui_config=sui_config)

        bet_amount = 1
        if balance.float > bet_amount:
            coinflip_side = random.choice(list(CoinflipSide))

            result = play_coinflip_tx(sui_config=sui_config,
                                      associated_kiosk_addr=associated_kiosk_addr,
                                      bullshark_addr=bullshark_addr,
                                      coinflip_side=coinflip_side,
                                      bet_amount=bet_amount,
                                      bullshark=bullshark)
            sleep = 0
            if result.reason:
                if result.digest:
                    sleep = random.randint(BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[0],
                                           BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                        f'reason: {result.reason} | sleep: {sleep}s.')
                else:
                    logger.error(
                        f'{short_address(result.address)} | {coinflip_side.name} | '
                        f'reason: {result.reason}.')
            else:
                sleep = random.randint(BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[0],
                                       BIG_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
                logger.info(f'{short_address(result.address)} | {coinflip_side.name} | digest: {result.digest} | '
                            f'sleep: {sleep}s.')

            time.sleep(sleep)
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
        logger.info(f'{str(sui_config.active_address)} | COINFLIP | sleep: {unique_sleep} sec.')
        time.sleep(unique_sleep)

        associated_kiosk_addr = get_associated_kiosk(address=str(sui_config.active_address))
        kiosk_dynamic_fields = get_bullshark_id(kiosk_addr=associated_kiosk_addr).result.data

        capy_addr = None
        bullshark_addr = None
        for field in kiosk_dynamic_fields:
            if 'bullshark' in str(field.objectType).lower():
                bullshark_addr = field.objectId
            elif 'capy' in str(field.objectType).lower():
                capy_addr = field.objectId

        if bullshark_addr or capy_addr:
            flips_per_session = random.randint(COINFLIP_COUNT_PER_SESSION[0], COINFLIP_COUNT_PER_SESSION[1])
            broken = False
            for _ in range(flips_per_session):
                play_game_result = main_play_game(
                    sui_config=sui_config,
                    associated_kiosk_addr=associated_kiosk_addr,
                    bullshark_addr=capy_addr if capy_addr else bullshark_addr,
                    bullshark=False if capy_addr else True
                )
                if play_game_result == 'zero_balance':
                    broken = True
                    break

            if not broken:
                if capy_addr:
                    logger.success(f'{str(sui_config.active_address)} | '
                                   f'has coinflipped {flips_per_session} times with CAPY.')
                else:
                    logger.success(f'{str(sui_config.active_address)} | '
                                   f'has coinflipped {flips_per_session} times with BULLSHARK.')
        else:
            logger.error(f'{str(sui_config.active_address)} | does not have SuiFrens.')
    except Exception as e:
        logger.exception(e)


def run_coinflip_executor(sui_configs: list[SuiConfig]):
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
            run_coinflip_executor(sui_configs=sui_configs)
        else:
            logger.info('all accounts meet the requirements.')
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
