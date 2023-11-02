import random
import time

import requests

from config import SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC


def random_sleep():
    time.sleep(random.randint(SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC[0], SMALL_SLEEP_BETWEEN_ACTIONS_IN_SEC[1]))


def short_address(address: str) -> str:
    return address[:6] + "..." + address[-4:]


def get_proxied_session(proxy: str):
    session = requests.Session()
    if proxy:
        session.proxies = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
    return session


def read_mnemonics(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line]
    return not_empty
