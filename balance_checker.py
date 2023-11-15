import concurrent.futures
import os

from loguru import logger
from pysui import SuiConfig

from utils.add_logger import add_logger
from utils.other import read_mnemonics
from utils.sui import get_sui_balance, get_list_of_sui_configs


def single_executor(sui_config: SuiConfig):
    try:
        balance = get_sui_balance(sui_config=sui_config)
        logger.info(f'{str(sui_config.active_address)}: {balance.float} $SUI.')
        with open(output_path, 'a') as file:
            file.write(f'{str(sui_config.active_address)}:{balance.float}\n')
    except Exception as e:
        logger.exception(e)


def run_balance_executor(sui_configs: list[SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


if __name__ == '__main__':
    add_logger()
    try:
        output_path = 'data/balance.txt'
        if os.path.isfile(output_path):
            os.remove(output_path)

        mnemonics = read_mnemonics(path='data/mnemonic.txt')
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)
        if sui_configs:
            run_balance_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
