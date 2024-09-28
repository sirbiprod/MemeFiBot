import os
import glob
import asyncio
import argparse
from itertools import cycle

import platform
import sys
#import distro

from pyrogram import Client
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions


start_text = """
                               
███╗   ███╗███████╗███╗   ███╗███████╗███████╗██╗██████╗  ██████╗ ████████╗
████╗ ████║██╔════╝████╗ ████║██╔════╝██╔════╝██║██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║█████╗  ██╔████╔██║█████╗  █████╗  ██║██████╔╝██║   ██║   ██║   
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══╝  ██║██╔══██╗██║   ██║   ██║   
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║███████╗██║     ██║██████╔╝╚██████╔╝   ██║   
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝╚═════╝  ╚═════╝    ╚═╝   
                                                                           
Select an action:

    1. Run bot
    2. Create session
"""


def get_session_names() -> list[str]:
    session_names = sorted(glob.glob('sessions/*.session'))
    session_names = [os.path.splitext(os.path.basename(file))[0] for file in session_names]

    return session_names


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file='bot/config/proxies.txt', encoding='utf-8-sig') as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_tg_clients() -> list[Client]:
    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [Client(
        name=session_name,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        workdir='sessions/',
        plugins=dict(root='bot/plugins')
    ) for session_name in session_names]

    return tg_clients


async def process() -> None:

    # Версия Python
    python_version = sys.version

    # Версия системы
    system = platform.system()
    release = platform.release()

    if system == "Windows":
        logger.debug(f"⚡️ Версия Python: {python_version}")
        logger.debug(f"⚡️ Операционная система: {system} {release}")
    elif system == "Linux":
        #distro_info = distro.linux_distribution()
        logger.debug(f"⚡️ Версия Python: {python_version}")
        logger.debug(f"⚡️ Операционная система: {system} {release}")
        #logger.debug(f"⚡️ Дистрибутив Linux: {distro_info[0]} {distro_info[1]}")
    else:
        logger.debug(f"⚡️ Версия Python: {python_version}")

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")
    logger.warning("⚠️ \n<e>en:</e> NOT FOR SALE\n<e>ru:</e> НЕ ДЛЯ ПРОДАЖИ\n<e>es:</e> NO VENTA\n<e>fr:</e> PAS À VENDRE\n<e>it:</e> NON PER VENDITA\n<e>gh:</e> YƐN TƆN")
    logger.info("<b>For updates and support visit:</b> <e>https://github.com/sirbiprod/MemeFiBot</e>")
    logger.info("Special for HiddenCode")

    action = parser.parse_args().action

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ['1', '2']:
                logger.warning("Action must be 1 or 2")
            else:
                action = int(action)
                break

    if action == 1:
        tg_clients = await get_tg_clients()
        await run_tasks(tg_clients=tg_clients)
    elif action == 2:
        await register_sessions()



async def run_tasks(tg_clients: list[Client]):
    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    tasks = [asyncio.create_task(run_tapper(tg_client=tg_client, proxy=next(proxies_cycle) if proxies_cycle else None))
             for tg_client in tg_clients]

    await asyncio.gather(*tasks)
