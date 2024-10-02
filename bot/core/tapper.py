import asyncio
import random
from time import time
from random import randint
from urllib.parse import unquote
import json

import os
import aiohttp
import aiocfscrape
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw import types
from datetime import datetime, timedelta, timezone
from dateutil import parser

from bot.config import settings
from bot.utils import logger
from bot.utils.graphql import Query, OperationName
from bot.utils.boosts import FreeBoostType, UpgradableBoostType
from .headers import headers
from .agents import generate_random_user_agent

from .TLS import TLSv1_3_BYPASS
from bot.exceptions import InvalidSession, InvalidProtocol



class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

        self.GRAPHQL_URL = 'https://api-gw-tg.memefi.club/graphql'

        self.session_ug_dict = self.load_user_agents() or []
        headers['User-Agent'] = self.check_user_agent()

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | User agent saved successfully")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("User agents file not found, creating...")

        except json.JSONDecodeError:
            logger.warning("User agents file is empty or corrupted.")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    async def get_tg_web_data(self, proxy: str | None):
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        first_run_file = 'referral.txt'

        def is_first_run():
            return not os.path.exists(first_run_file)

        def set_first_run():
            with open(first_run_file, 'w') as file:
                file.write('https://youtu.be/dQw4w9WgXcQ')


        # pupa = '/start '
        # i = 'r_bc7a351b1a'
        # lupa = f"'{settings.REF_ID}'"
        # str(lupazapupu) = pupa + i
        # str(pupazalupu) = pupa + lupa

        pupa = '/start r_bc7a351b1a'
        lupa = f'/start {settings.REF_ID}'

        my_friends = [pupa, lupa]

        random_friends = random.choice(my_friends)

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                    if is_first_run() and settings.REF and settings.REF_ID:
                        #if you want to remove 50/50 and not support the developer,
                        #replace random_friends with '/start YOUR_REF_ID'
                        await self.tg_client.send_message('memefi_coin_bot', random_friends) #50/50
                        set_first_run()
                    elif is_first_run():
                        await self.tg_client.send_message('memefi_coin_bot', pupa)
                        set_first_run()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('memefi_coin_bot'),
                bot=await self.tg_client.resolve_peer('memefi_coin_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://tg-app.memefi.club/game'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
            user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
            auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
            hash_ = tg_web_data.split('hash=', maxsplit=1)[1]

            me = await self.tg_client.get_me()

            json_data = {
                'operationName': OperationName.MutationTelegramUserLogin,
                'variables': {
                    'webAppData': {
                        'auth_date': int(auth_date),
                        'hash': hash_,
                        'query_id': query_id,
                        'checkDataString': f'auth_date={auth_date}\nquery_id={query_id}\nuser={user_data}',
                        'user': {
                            'id': me.id,
                            'allows_write_to_pm': True,
                            'first_name': me.first_name,
                            'last_name': me.last_name if me.last_name else '',
                            'username': me.username if me.username else '',
                            'language_code': me.language_code if me.language_code else 'en',
                        },
                    },
                },
                'query': Query.MutationTelegramUserLogin,
            }

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return json_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=5)

    async def get_access_token(self, http_client: aiohttp.ClientSession, tg_web_data: dict[str]):
        for _ in range(2):
            try:
                response = await http_client.post(url=self.GRAPHQL_URL, json=tg_web_data)
                response.raise_for_status()

                response_json = await response.json()

                if 'errors' in response_json:
                    raise InvalidProtocol(f'get_access_token msg: {response_json["errors"][0]["message"]}')

                access_token = response_json.get('data', {}).get('telegramUserLogin', {}).get('access_token', '')

                if not access_token:
                    await asyncio.sleep(delay=5)
                    continue

                return access_token
            except Exception as error:
                logger.error(f"{self.session_name} | ❗️ Unknown error while getting Access Token: {error}")
                await asyncio.sleep(delay=15)

        return ""

    async def get_telegram_me(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.QueryTelegramUserMe,
                'query': Query.QueryTelegramUserMe,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'get_telegram_me msg: {response_json["errors"][0]["message"]}')

            me = response_json['data']['telegramUserMe']

            return me
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while getting Telegram Me: {error}")
            await asyncio.sleep(delay=3)

            return {}

    async def get_profile_data(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.QUERY_GAME_CONFIG,
                'query': Query.QUERY_GAME_CONFIG,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'get_profile_data msg: {response_json["errors"][0]["message"]}')

            profile_data = response_json['data']['telegramGameGetConfig']

            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while getting Profile Data: {error}")
            await asyncio.sleep(delay=9)

    async def set_next_boss(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.telegramGameSetNextBoss,
                'query': Query.telegramGameSetNextBoss,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while Setting Next Boss: {error}")
            await asyncio.sleep(delay=9)

            return False

    async def get_clan(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.ClanMy,
                'query': Query.ClanMy,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            data = response_json['data']['clanMy']
            if data and data['id']:
                return data['id']
            else:
                return False

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while get clan: {error}")
            await asyncio.sleep(delay=9)
            return False

    async def leave_clan(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Leave,
                'query': Query.Leave,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            if response_json['data']:
                if response_json['data']['clanActionLeaveClan']:
                    return True

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while clan leave: {error}")
            await asyncio.sleep(delay=9)
            return False

    async def join_clan(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Join,
                'query': Query.Join,
                'variables': {
                    'clanId': '71886d3b-1186-452d-8ac6-dcc5081ab204'
                }
            }

            while True:
                response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
                response.raise_for_status()
                response_json = await response.json()
                if response_json['data']:
                    if response_json['data']['clanActionJoinClan']:
                        return True
                elif response_json['errors']:
                    await asyncio.sleep(2)
                    return False
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while clan join: {error}")
            await asyncio.sleep(delay=9)
            return False

    async def get_bot_config(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TapbotConfig,
                'query': Query.TapbotConfig,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()
            bot_config = response_json['data']['telegramGameTapbotGetConfig']

            return bot_config
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while getting Bot Config: {error}")
            await asyncio.sleep(delay=9)

    async def start_bot(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TapbotStart,
                'query': Query.TapbotStart,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Starting Bot: {error}")
            await asyncio.sleep(delay=9)

            return False

    async def claim_bot(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TapbotClaim,
                'query': Query.TapbotClaim,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            data = response_json['data']["telegramGameTapbotClaim"]
            return {"isClaimed": False, "data": data}
        except Exception as error:
            return {"isClaimed": True, "data": None}

    async def claim_referral_bonus(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.Mutation,
                'query': Query.Mutation,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Claiming Referral Bonus: {error}")
            await asyncio.sleep(delay=9)

            return False

    async def apply_boost(self, http_client: aiohttp.ClientSession, boost_type: FreeBoostType):
        try:
            json_data = {
                'operationName': OperationName.telegramGameActivateBooster,
                'query': Query.telegramGameActivateBooster,
                'variables': {
                    'boosterType': boost_type
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error while Apply {boost_type} Boost: {error}")
            await asyncio.sleep(delay=9)

            return False

    async def upgrade_boost(self, http_client: aiohttp.ClientSession, boost_type: UpgradableBoostType):
        try:
            json_data = {
                'operationName': OperationName.telegramGamePurchaseUpgrade,
                'query': Query.telegramGamePurchaseUpgrade,
                'variables': {
                    'upgradeType': boost_type
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if 'errors' in response_json:
                raise InvalidProtocol(f'upgrade_boost msg: {response_json["errors"][0]["message"]}')

            return True
        except Exception:
            return False

    async def send_taps(self, http_client: aiohttp.ClientSession, nonce: str, taps: int):
        try:
            vectorArray = []
            for tap in range(taps):
                """ check if tap is greater than 4 or less than 1 and set tap to random number between 1 and 4"""
                if tap > 4 or tap < 1:
                    tap = randint(1, 4)
                vectorArray.append(tap)

            vector = ",".join(str(x) for x in vectorArray)
            json_data = {
                'operationName': OperationName.MutationGameProcessTapsBatch,
                'query': Query.MutationGameProcessTapsBatch,
                'variables': {
                    'payload': {
                        'nonce': nonce,
                        'tapsCount': taps,
                        'vector': vector
                    },
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()

            if response.status != 200:
                status500 = response.status
                return status500

            if 'errors' in response_json:
                raise InvalidProtocol(f'send_taps msg: {response_json["errors"][0]["message"]}')

            profile_data = response_json['data']['telegramGameProcessTapsBatch']
            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error when Tapping: {error}")
            await asyncio.sleep(delay=9)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://api.ipify.org?format=json', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('ip')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def play_slotmachine(self, http_client: aiohttp.ClientSession):
        spin_value = settings.VALUE_SPIN
        try:
            json_data = {
                'operationName': OperationName.SpinSlotMachine,
                'query': Query.SpinSlotMachine,
                'variables': {
                    'payload': {
                        'spinsCount': spin_value
                    }
                }
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response_json = await response.json()
            play_data = response_json.get('data', {}).get('slotMachineSpinV2', {})

            return play_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️ Unknown error when Play Casino: {error}")
            return {}

    async def wallet_check(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.TelegramMemefiWallet,
                'query': Query.TelegramMemefiWallet,
                'variables': {}
            }
            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response_json = await response.json()
            no_wallet_response = {'data': {'telegramMemefiWallet': None}}
            if response_json == no_wallet_response:
                none_wallet = "-"
                linea_wallet = none_wallet
                return linea_wallet
            else:
                linea_wallet = response_json.get('data', {}).get('telegramMemefiWallet', {}).get('walletAddress', {})
                return linea_wallet
        except Exception as error:
                logger.error(f"{self.session_name} | ❗️ Unknown error when Get Wallet: {error}")
                return None

    async def get_linea_wallet_balance(self, http_client: aiohttp.ClientSession, linea_wallet: str):
        try:
            api_key = settings.LINEA_API
            api_url = (f"https://api.lineascan.build/api?module=account&action=balance&address="
                       f"{linea_wallet}&tag=latest&apikey={api_key}")

            async with http_client.get(api_url) as response:
                data = await response.json()
                if data['status'] == '1' and data['message'] == 'OK':
                    balance_wei = int(data['result'])
                    balance_eth = float((balance_wei / 1e18))
                    return balance_eth
                else:
                    if linea_wallet == '-':
                        balance_eth = '-'
                        return balance_eth
                    else:
                        logger.warning(f"{self.session_name} | Failed to retrieve Linea wallet balance: "
                                       f"{data['message']}")
                        return None
        except Exception as error:
            logger.error(f"{self.session_name} | Error getting Linea wallet balance: {error}")
            return None

    async def get_eth_price(self, http_client: aiohttp.ClientSession, balance_eth: str):
        try:
            if balance_eth == '-':
                return balance_eth
            else:
                api_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=ethereum"

                async with http_client.get(api_url) as response:
                    data = await response.json()
                    if response.status == 200:
                        eth_current_price = int(float(data[0]['current_price']) // 1)
                        eth_price = round((eth_current_price * float(balance_eth)), 2)
                        return eth_price
                    else:
                        logger.warning(f"{self.session_name} | Failed to retrieve ETH price: {response.status} code")
                        return None
        except Exception as error:
            logger.error(f"{self.session_name} | Error getting ETH price: {error}")
            return None

    async def get_campaigns(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': "CampaignLists",
                'query': Query.CampaignLists,
                'variables': {}
            }
            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while getting campaigns: {data['errors'][0]['message']}")
                return None

            campaigns = data.get('data', {}).get('campaignLists', {}).get('normal', [])
            return [campaign for campaign in campaigns if 'youtube' in campaign.get('description', '').lower()]

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting campaigns: {str(e)}")
            return {}

    async def get_tasks_list(self, http_client: aiohttp.ClientSession, campaigns_id: str):
        try:
            json_data = {
                'operationName': "GetTasksList",
                'query': Query.GetTasksList,
                'variables': {'campaignId': campaigns_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while getting tasks: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTasks', [])

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting tasks: {str(e)}")
            return None

    async def verify_campaign(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            json_data = {
                'operationName': "CampaignTaskToVerification",
                'query': Query.CampaignTaskToVerification,
                'variables': {'taskConfigId': task_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while verifying task: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskMoveToVerificationV2')
        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while verifying task: {str(e)}")
            return None

    async def get_task_by_id(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            json_data = {
                'operationName': "GetTaskById",
                'query': Query.GetTaskById,
                'variables': {'taskId': task_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            data = await response.json()

            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while getting task by id: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskGetConfig')
        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while getting task by id: {str(e)}")
            return None

    async def complete_task(self, http_client: aiohttp.ClientSession, user_task_id: str):
        try:
            json_data = {
                'operationName': "CampaignTaskMarkAsCompleted",
                'query': Query.CampaignTaskMarkAsCompleted,
                'variables': {'userTaskId': user_task_id}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)

            response.raise_for_status()

            data = await response.json()


            if 'errors' in data:
                logger.error(f"{self.session_name} | Error while completing task: {data['errors'][0]['message']}")
                return None

            return data.get('data', {}).get('campaignTaskMarkAsCompleted')

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while completing task: {str(e)}")
            return None

    async def run(self, proxy: str | None):
        access_token_created_time = 0
        turbo_time = 0
        active_turbo = False

        ssl_context = TLSv1_3_BYPASS.create_ssl_context()
        conn = ProxyConnector().from_url(url=proxy, rdns=True, ssl=ssl_context) if proxy \
            else aiohttp.TCPConnector(ssl=ssl_context)

        async with aiocfscrape.CloudflareScraper(headers=headers, connector=conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)


            while True:
                noBalance = False
                try:
                    if time() - access_token_created_time >= 5400:
                        http_client.headers.pop("Authorization", None)

                        tg_web_data = await self.get_tg_web_data(proxy=proxy)

                        if not tg_web_data:
                            logger.info(f"{self.session_name} | Log out!")
                            return

                        access_token = await self.get_access_token(http_client=http_client, tg_web_data=tg_web_data)

                        if not access_token:
                            await asyncio.sleep(delay=5)
                            continue

                        http_client.headers["Authorization"] = f"Bearer {access_token}"

                        access_token_created_time = time()

                        await self.get_telegram_me(http_client=http_client)

                        profile_data = await self.get_profile_data(http_client=http_client)

                        if not profile_data:
                            continue

                        balance = profile_data.get('coinsAmount', 0)

                        nonce = profile_data.get('nonce', '')

                        current_boss = profile_data['currentBoss']
                        current_boss_level = current_boss['level']
                        boss_max_health = current_boss['maxHealth']
                        boss_current_health = current_boss['currentHealth']

                        spins = profile_data.get('spinEnergyTotal', 0)

                        logger.info(f"{self.session_name} | Current boss level: <m>{current_boss_level}</m> | "
                                    f"Boss health: <e>{boss_current_health}</e> out of <r>{boss_max_health}</r> | "
                                    f"Balance: <c>{balance}</c> | Spins: <le>{spins}</le>")

                        if settings.USE_RANDOM_DELAY_IN_RUN:
                            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0],
                                                          settings.RANDOM_DELAY_IN_RUN[1])
                            logger.info(f"{self.session_name} | Bot will start in <y>{random_delay}s</y>")
                            await asyncio.sleep(random_delay)

                            if settings.LINEA_WALLET is True:
                                linea_wallet = await self.wallet_check(http_client=http_client)
                                logger.info(f"{self.session_name} | 💳 Linea wallet address: <y>{linea_wallet}</y>")
                                if settings.LINEA_SHOW_BALANCE:
                                    if settings.LINEA_API != '':
                                        balance_eth = await self.get_linea_wallet_balance(http_client=http_client,
                                                                                          linea_wallet=linea_wallet)
                                        eth_price = await self.get_eth_price(http_client=http_client,
                                                                             balance_eth=balance_eth)
                                        logger.info(f"{self.session_name} | ETH Balance: <g>{balance_eth}</g> | "
                                                    f"USD Balance: <e>{eth_price}</e>")
                                    elif settings.LINEA_API == '':
                                        logger.info(f"{self.session_name} | "
                                                    f"💵 LINEA_API must be specified to show the balance")
                                        await asyncio.sleep(delay=3)

                        if boss_current_health == 0:
                            logger.info(
                                f"{self.session_name} | 👉 Setting next boss: <m>{current_boss_level + 1}</m> lvl")
                            logger.info(f"{self.session_name} | 😴 Sleep 10s")
                            await asyncio.sleep(delay=10)

                            status = await self.set_next_boss(http_client=http_client)
                            if status is True:
                                logger.success(f"{self.session_name} | ✅ Successful setting next boss: "
                                               f"<m>{current_boss_level + 1}</m>")

                        if settings.WATCH_VIDEO:
                            task_json = await self.get_campaigns(http_client=http_client)
                            n = 0
                            while n < 197:
                                campaigns_id = task_json[n]['id']
                                if task_json is not None:
                                    tasks_list = await self.get_tasks_list(http_client=http_client,
                                                                           campaigns_id=campaigns_id)
                                    name = tasks_list[0]['name']
                                    status = tasks_list[0]['status']
                                    logger.info(f"{self.session_name} "
                                                f"| Video: <r>{name}</r> | Status: <y>{status}</y>")
                                    task_id = tasks_list[0]['id']
                                    await asyncio.sleep(delay=1)
                                    if status == 'Verification':
                                        logger.info(f"{self.session_name} "
                                                    f"| Unable to complete a task, it is already in progress")
                                        logger.info(f"{self.session_name} | <r>Skip video</r>")
                                        n += 1
                                        continue
                                    if tasks_list is not None and status != 'Verification':
                                        await asyncio.sleep(delay=2)
                                        verify_campaign = await self.verify_campaign(http_client=http_client,
                                                                                     task_id=task_id)
                                        status = verify_campaign['status']
                                        logger.info(f"{self.session_name} "
                                                    f"| Video: <r>{name}</r> | Status: <y>{status}</y>")
                                        logger.info(f"{self.session_name} | Waiting 5s")
                                        await asyncio.sleep(delay=5)
                                        if verify_campaign is not None:
                                            get_task_by_id = await self.get_task_by_id(http_client=http_client,
                                                                                       task_id=task_id)
                                            user_task_id = get_task_by_id['userTaskId']
                                            status = get_task_by_id['status']

                                            sleep_time_task = max((parser.isoparse(
                                                get_task_by_id.get('verificationAvailableAt')) - datetime.now(
                                                timezone.utc)).total_seconds() + 5, randint(5, 15))

                                            logger.info(f"{self.session_name} "
                                                        f"| Video: <r>{name}</r> | Status: <y>{status}</y>")
                                            logger.info(f"{self.session_name} | Waiting {sleep_time_task}s")
                                            await asyncio.sleep(delay=sleep_time_task)
                                            if get_task_by_id is not None:
                                                complete_task = await self.complete_task(http_client=http_client,
                                                                                         user_task_id=user_task_id)
                                                status = complete_task['status']
                                                logger.info(f"{self.session_name} "
                                                            f"| Video: <r>{name}</r> | Status: <g>{status}</g>")
                                                await asyncio.sleep(delay=3)
                                                n += 1

                    spins = profile_data.get('spinEnergyTotal', 0)
                    if settings.ROLL_CASINO:
                        while spins > settings.VALUE_SPIN:
                            await asyncio.sleep(delay=2)
                            play_data = await self.play_slotmachine(http_client=http_client)
                            reward_amount = play_data.get('spinResults', [{}])[0].get('rewardAmount', 0)
                            reward_type = play_data.get('spinResults', [{}])[0].get('rewardType', 'NO')
                            spins = play_data.get('gameConfig', {}).get('spinEnergyTotal', 0)
                            balance = play_data.get('gameConfig', {}).get('coinsAmount', 0)
                            if play_data.get('ethLotteryConfig', {}) is None:
                                eth_lottery_status = '-'
                                eth_lottery_ticket = '-'
                            else:
                                eth_lottery_status = play_data.get('ethLotteryConfig', {}).get('isCompleted', 0)
                                eth_lottery_ticket = play_data.get('ethLotteryConfig', {}).get('ticketNumber', 0)
                            logger.info(f"{self.session_name} | 🎰 Casino game | "
                                        f"Balance: <lc>{balance:,}</lc> (<lg>+{reward_amount:,}</lg> "
                                        f"<lm>{reward_type}</lm>) "
                                        f"| Spins: <le>{spins:,}</le> ")
                            if settings.LOTTERY_INFO:
                                logger.info(f"{self.session_name} | 🎟 ETH Lottery status: {eth_lottery_status} |"
                                            f" 🎫 Ticket number: <yellow>{eth_lottery_ticket}</yellow>")
                            await asyncio.sleep(delay=5)

                    taps = randint(a=settings.RANDOM_TAPS_COUNT[0], b=settings.RANDOM_TAPS_COUNT[1])
                    if taps > boss_current_health:
                        taps = boss_max_health - boss_current_health - 10
                        return taps
                    bot_config = await self.get_bot_config(http_client=http_client)
                    telegramMe = await self.get_telegram_me(http_client=http_client)

                    available_energy = profile_data['currentEnergy']
                    need_energy = taps * profile_data['weaponLevel']

                    clancheck_file = 'clancheck.txt'

                    def first_check_clan():
                        return not os.path.exists(clancheck_file)

                    def set_first_run_check_clan():
                        with open(clancheck_file, 'w') as file:
                            file.write('This file indicates that the script has already run once.')

                    if first_check_clan():
                        clan = await self.get_clan(http_client=http_client)
                        set_first_run_check_clan()
                        await asyncio.sleep(1)
                        if clan is not False and clan != '71886d3b-1186-452d-8ac6-dcc5081ab204':
                            await asyncio.sleep(1)
                            clan_leave = await self.leave_clan(http_client=http_client)
                            if clan_leave is True:
                                await asyncio.sleep(1)
                                clan_join = await self.join_clan(http_client=http_client)
                                if clan_join is True:
                                    continue
                                elif clan_join is False:
                                    await asyncio.sleep(1)
                                    continue
                            elif clan_leave is False:
                                continue
                        elif clan == '71886d3b-1186-452d-8ac6-dcc5081ab204':
                            continue
                        else:
                            clan_join = await self.join_clan(http_client=http_client)
                            if clan_join is True:
                                continue
                            elif clan_join is False:
                                await asyncio.sleep(1)
                                continue

                    if telegramMe['isReferralInitialJoinBonusAvailable'] is True:
                        await self.claim_referral_bonus(http_client=http_client)
                        logger.info(f"{self.session_name} | 🔥Referral bonus was claimed")

                    if bot_config['isPurchased'] is False and settings.AUTO_BUY_TAPBOT is True:
                        await self.upgrade_boost(http_client=http_client, boost_type=UpgradableBoostType.TAPBOT)
                        logger.info(f"{self.session_name} | 👉 Tapbot was purchased - 😴 Sleep 7s")
                        await asyncio.sleep(delay=9)
                        bot_config = await self.get_bot_config(http_client=http_client)

                    if bot_config['isPurchased'] is True:
                        if bot_config['usedAttempts'] < bot_config['totalAttempts'] and not bot_config['endsAt']:
                            await self.start_bot(http_client=http_client)
                            bot_config = await self.get_bot_config(http_client=http_client)
                            logger.info(f"{self.session_name} | 👉 Tapbot is started")

                        else:
                            tapbotClaim = await self.claim_bot(http_client=http_client)
                            if tapbotClaim['isClaimed'] == False and tapbotClaim['data']:
                                logger.info(
                                    f"{self.session_name} | 👉 Tapbot was claimed - 😴 Sleep 7s before starting again")
                                await asyncio.sleep(delay=9)
                                bot_config = tapbotClaim['data']
                                await asyncio.sleep(delay=5)

                                if bot_config['usedAttempts'] < bot_config['totalAttempts']:
                                    await self.start_bot(http_client=http_client)
                                    logger.info(f"{self.session_name} | 👉 Tapbot is started - 😴 Sleep 7s")
                                    await asyncio.sleep(delay=9)
                                    bot_config = await self.get_bot_config(http_client=http_client)

                    if active_turbo:
                        taps += randint(a=settings.ADD_TAPS_ON_TURBO[0], b=settings.ADD_TAPS_ON_TURBO[1])
                        if taps > boss_current_health:
                            taps = boss_max_health - boss_current_health - 10
                            return taps

                        need_energy = 0

                        if time() - turbo_time > 10:
                            active_turbo = False
                            turbo_time = 0

                    if need_energy > available_energy or available_energy - need_energy < settings.MIN_AVAILABLE_ENERGY:
                        logger.warning(f"{self.session_name} | Need more energy ({available_energy}/{need_energy}, min:"
                                       f" {settings.MIN_AVAILABLE_ENERGY}) for {taps} taps")

                        sleep_between_clicks = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])
                        logger.info(f"Sleep {sleep_between_clicks}s")
                        await asyncio.sleep(delay=sleep_between_clicks)
                        # update profile data
                        profile_data = await self.get_profile_data(http_client=http_client)
                        continue

                    profile_data = await self.send_taps(http_client=http_client, nonce=nonce, taps=taps)

                    if not profile_data:
                        continue

                    available_energy = profile_data['currentEnergy']
                    new_balance = profile_data['coinsAmount']

                    free_boosts = profile_data['freeBoosts']
                    turbo_boost_count = free_boosts['currentTurboAmount']
                    energy_boost_count = free_boosts['currentRefillEnergyAmount']

                    next_tap_level = profile_data['weaponLevel'] + 1
                    next_energy_level = profile_data['energyLimitLevel'] + 1
                    next_charge_level = profile_data['energyRechargeLevel'] + 1

                    nonce = profile_data['nonce']

                    current_boss = profile_data['currentBoss']
                    current_boss_level = current_boss['level']
                    boss_current_health = current_boss['currentHealth']

                    if boss_current_health <= 0:
                        logger.info(f"{self.session_name} | 👉 Setting next boss: <m>{current_boss_level + 1}</m> lvl")
                        logger.info(f"{self.session_name} | 😴 Sleep 10s")
                        await asyncio.sleep(delay=10)

                        status = await self.set_next_boss(http_client=http_client)
                        if status is True:
                            logger.success(f"{self.session_name} | ✅ Successful setting next boss: "
                                           f"<m>{current_boss_level + 1}</m>")

                    taps_status = await self.send_taps(http_client=http_client, nonce=nonce, taps=taps)
                    taps_new_balance = taps_status['coinsAmount']
                    calc_taps = taps_new_balance - balance
                    if calc_taps > 0:
                        logger.success(
                            f"{self.session_name} | ✅ Successful tapped! 🔨 | 👉 Current energy: {available_energy} "
                            f"| ⚡️ Minimum energy limit: {settings.MIN_AVAILABLE_ENERGY} | "
                            f"Balance: <c>{taps_new_balance}</c> (<g>+{calc_taps} 😊</g>) | "
                            f"Boss health: <e>{boss_current_health}</e>")
                        balance = new_balance
                    else:
                        logger.info(
                            f"{self.session_name} | ❌ Failed tapped! 🔨 | Balance: <c>{taps_new_balance}</c> "
                            f"(<g>No coin added 😥</g>) | 👉 Current energy: {available_energy} | "
                            f"⚡️ Minimum energy limit: {settings.MIN_AVAILABLE_ENERGY} | "
                            f"Boss health: <e>{boss_current_health}</e>")
                        balance = new_balance
                        taps_status_json = json.dumps(taps_status)
                        logger.warning(
                            f"{self.session_name} | ❌ MemeFi server error 500"
                        )
                        #print(f"{self.session_name} | ", json.dumps(taps_status))
                        logger.info(f"{self.session_name} | 😴 Sleep 10m")
                        await asyncio.sleep(delay=600)
                        noBalance = True

                    if active_turbo is False:
                        if (energy_boost_count > 0
                                and available_energy < settings.MIN_AVAILABLE_ENERGY
                                and settings.APPLY_DAILY_ENERGY is True
                                and available_energy - need_energy < settings.MIN_AVAILABLE_ENERGY):
                            logger.info(f"{self.session_name} | 😴 Sleep 7s before activating the daily energy boost")
                            #await asyncio.sleep(delay=9)

                            status = await self.apply_boost(http_client=http_client, boost_type=FreeBoostType.ENERGY)
                            if status is True:
                                logger.success(f"{self.session_name} | 👉 Energy boost applied")

                                await asyncio.sleep(delay=3)

                            continue

                        if turbo_boost_count > 0 and settings.APPLY_DAILY_TURBO is True:
                            logger.info(f"{self.session_name} | 😴 Sleep 10s before activating the daily turbo boost")
                            await asyncio.sleep(delay=10)

                            status = await self.apply_boost(http_client=http_client, boost_type=FreeBoostType.TURBO)
                            if status is True:
                                logger.success(f"{self.session_name} | 👉 Turbo boost applied")

                                await asyncio.sleep(delay=9)

                                active_turbo = True
                                turbo_time = time()

                            continue

                        if settings.AUTO_UPGRADE_TAP is True and next_tap_level <= settings.MAX_TAP_LEVEL:
                            need_balance = 1000 * (2 ** (next_tap_level - 1))
                            if balance > need_balance:
                                status = await self.upgrade_boost(http_client=http_client,
                                                                  boost_type=UpgradableBoostType.TAP)
                                if status is True:
                                    logger.success(f"{self.session_name} | Tap upgraded to {next_tap_level} lvl")

                                    await asyncio.sleep(delay=1)
                            else:
                                logger.info(f"{self.session_name} | Need more gold for upgrade tap to {next_tap_level}"
                                            f" lvl ({balance}/{need_balance})")

                        if settings.AUTO_UPGRADE_ENERGY is True and next_energy_level <= settings.MAX_ENERGY_LEVEL:
                            need_balance = 1000 * (2 ** (next_energy_level - 1))
                            if balance > need_balance:
                                status = await self.upgrade_boost(http_client=http_client,
                                                                  boost_type=UpgradableBoostType.ENERGY)
                                if status is True:
                                    logger.success(f"{self.session_name} | Energy upgraded to {next_energy_level} lvl")

                                    await asyncio.sleep(delay=1)
                            else:
                                logger.warning(
                                    f"{self.session_name} | Need more gold for upgrade energy to {next_energy_level} "
                                    f"lvl ({balance}/{need_balance})")


                        if settings.AUTO_UPGRADE_CHARGE is True and next_charge_level <= settings.MAX_CHARGE_LEVEL:
                            need_balance = 1000 * (2 ** (next_charge_level - 1))

                            if balance > need_balance:
                                status = await self.upgrade_boost(http_client=http_client,
                                                                  boost_type=UpgradableBoostType.CHARGE)
                                if status is True:
                                    logger.success(f"{self.session_name} | Charge upgraded to {next_charge_level} lvl")

                                    await asyncio.sleep(delay=1)
                            else:
                                logger.warning(
                                    f"{self.session_name} | Need more gold for upgrade charge to {next_energy_level} "
                                    f"lvl ({balance}/{need_balance})")


                        if available_energy < settings.MIN_AVAILABLE_ENERGY:
                            logger.info(f"{self.session_name} | 👉 Minimum energy reached: {available_energy}")
                            logger.info(f"{self.session_name} | 😴 Sleep {settings.SLEEP_BY_MIN_ENERGY}s")

                            await asyncio.sleep(delay=settings.SLEEP_BY_MIN_ENERGY)

                            continue

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | ❗️Unknown error: {error}")
                    logger.info(f"{self.session_name} | 😴 Wait 1h")
                    await asyncio.sleep(delay=3600)

                else:
                    sleep_between_clicks = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])

                    if active_turbo is True:
                        sleep_between_clicks = 50
                    elif noBalance is True:
                        sleep_between_clicks = 700

                    logger.info(f"{self.session_name} | 😴 Sleep {sleep_between_clicks}s")
                    await asyncio.sleep(delay=sleep_between_clicks)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | ❗️Invalid Session")
    except InvalidProtocol as error:
        logger.error(f"{tg_client.name} | ❗️Invalid protocol detected at {error}")
