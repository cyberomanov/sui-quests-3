import concurrent.futures
import json
import random
import time

import requests
from loguru import logger
from pysui import SuiConfig

from config import SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC
from datatypes.leaderboard import LeaderboardResponse
from utils.add_logger import add_logger
from utils.other import read_mnemonics
from utils.sui import get_list_of_sui_configs


def run_leaderboard_executor(sui_configs: [SuiConfig]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(single_executor, sui_configs)


def single_executor(sui_config: SuiConfig):
    try:
        unique_sleep = random.randint(SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC[0], SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC[1])
        logger.info(f'{str(sui_config.active_address)} | LEADERBOARD | sleep: {unique_sleep} sec.')
        time.sleep(unique_sleep)

        session = requests.Session()
        session.params = {
            'batch': '1',
            'input': '{"0":{"address":"%s","questId":3}}' % str(sui_config.active_address),
        }

        response = session.get(url="https://quests.mystenlabs.com/api/trpc/user")
        leaderboard = LeaderboardResponse.parse_obj(json.loads(response.content)[0])
        data = leaderboard.result.data

        used_apps_log = ''
        ignore_list = ['FIRST_APPEARANCE_CHECKPOINT', 'HAS_SUINS',
                       'ENGAGEMENT_MULTIPLIER', 'IS_ELIGIBLE',
                       'RANK', 'appsUsed']

        for metadata in data.metadata:
            if metadata[1] and metadata[0] not in ignore_list:
                used_apps_log += f'{metadata[0]}={metadata[1]:.2f} '

        if data:
            if data.bot:
                logger.info(f"{str(sui_config.active_address)} | "
                            f"points_per_apps: {used_apps_log} | "
                            f"total: {data.score}, "
                            f"quest_rank: {data.rank}, "
                            f"rewards_status: {data.metadata.IS_ELIGIBLE}.")
            else:
                logger.warning(f"{str(sui_config.active_address)} | "
                             f"points_per_apps: {used_apps_log} | "
                             f"total: {data.score}, "
                             f"quest_rank: {data.rank}, "
                             f"rewards_status: {data.metadata.IS_ELIGIBLE} | BOT.")

            return leaderboard
        else:
            logger.info(f"{str(sui_config.active_address)} | empty.")
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    add_logger()
    try:
        mnemonics = read_mnemonics(path='data/mnemonic.txt')
        sui_configs = get_list_of_sui_configs(mnemonics=mnemonics)
        if sui_configs:
            run_leaderboard_executor(sui_configs=sui_configs)
    except Exception as e:
        logger.exception(e)
    except KeyboardInterrupt:
        exit()
