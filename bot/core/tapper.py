import asyncio
import random
from time import time
from random import randint
from urllib.parse import unquote
import sys

import os
import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.utils.graphql import Query, OperationName
from bot.utils.boosts import FreeBoostType, UpgradableBoostType
from bot.exceptions import InvalidSession
from .headers import headers


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

        self.GRAPHQL_URL = 'https://api-gw-tg.memefi.club/graphql'

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

        first_run_file = 'runpoint.txt'

        def is_first_run():
            return not os.path.exists(first_run_file)

        def set_first_run():
            with open(first_run_file, 'w') as file:
                file.write('This file indicates that the script has already run once.')

        possible_refs = ['/start r_bc7a351b1a', '/start r_e3cd7cd18e']

        random_ref = random.choice(possible_refs)

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                    if is_first_run() and settings.REF:
                        await self.tg_client.send_message('memefi_coin_bot', random_ref)
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
                'query': Query.MutationTelegramUserLogin,
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
                            'platform': 'ios',
                            'version': '7.2'
                        },
                    },
                }
            }

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return json_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=9)

    async def get_access_token(self, http_client: aiohttp.ClientSession, tg_web_data: dict[str]):
        try:
            response = await http_client.post(url=self.GRAPHQL_URL, json=tg_web_data)
            response.raise_for_status()

            response_json = await response.json()
            access_token = response_json['data']['telegramUserLogin']['access_token']

            return access_token
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while getting Access Token: {error}")
            await asyncio.sleep(delay=9)

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
            profile_data = response_json['data']['telegramGameGetConfig']

            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while getting Profile Data: {error}")
            await asyncio.sleep(delay=9)

    async def get_user_data(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                'operationName': OperationName.QueryTelegramUserMe,
                'query': Query.QueryTelegramUserMe,
                'variables': {}
            }

            response = await http_client.post(url=self.GRAPHQL_URL, json=json_data)
            response.raise_for_status()

            response_json = await response.json()
            user_data = response_json['data']['telegramUserMe']

            return user_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error while getting User Data: {error}")
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
                'variables': {'clanId': '71886d3b-1186-452d-8ac6-dcc5081ab204'}
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
            logger.error(f"{self.session_name} | ❗️Unknown error while clan join: {error}")
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
            logger.error(f"{self.session_name} | ❗️Unknown error while getting Bot Config: {error}")
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
            logger.error(f"{self.session_name} | ❗️Unknown error while Starting Bot: {error}")
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
            logger.error(f"{self.session_name} | ❗️Unknown error while Claiming Referral Bonus: {error}")
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
            logger.error(f"{self.session_name} | ❗️Unknown error while Apply {boost_type} Boost: {error}")
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
            profile_data = response_json['data']['telegramGameProcessTapsBatch']
            return profile_data
        except Exception as error:
            logger.error(f"{self.session_name} | ❗️Unknown error when Tapping: {error}")
            await asyncio.sleep(delay=9)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None):
        access_token_created_time = 0
        turbo_time = 0
        active_turbo = False
        noBalance = False

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                noBalance = False
                try:
                    if time() - access_token_created_time >= 3600:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        access_token = await self.get_access_token(http_client=http_client, tg_web_data=tg_web_data)

                        http_client.headers["Authorization"] = f"Bearer {access_token}"
                        headers["Authorization"] = f"Bearer {access_token}"

                        access_token_created_time = time()

                        profile_data = await self.get_profile_data(http_client=http_client)

                        balance = profile_data['coinsAmount']

                        nonce = profile_data['nonce']

                        current_boss = profile_data['currentBoss']
                        current_boss_level = current_boss['level']
                        boss_max_health = current_boss['maxHealth']
                        boss_current_health = current_boss['currentHealth']

                        logger.info(f"{self.session_name} | Current boss level: <m>{current_boss_level}</m> | "
                                    f"Boss health: <e>{boss_current_health}</e> out of <r>{boss_max_health}</r>")

                        await asyncio.sleep(delay=15)

                    taps = randint(a=settings.RANDOM_TAPS_COUNT[0], b=settings.RANDOM_TAPS_COUNT[1])
                    bot_config = await self.get_bot_config(http_client=http_client)
                    telegramMe = await self.get_user_data(http_client=http_client)

                    clan = await self.get_clan(http_client=http_client)
                    await asyncio.sleep(3)
                    if clan is not False and clan != '71886d3b-1186-452d-8ac6-dcc5081ab204':
                        await asyncio.sleep(3)
                        clan_leave = await self.leave_clan(http_client=http_client)
                        if clan_leave is True:
                            await asyncio.sleep(3)
                            clan_join = await self.join_clan(http_client=http_client)
                            if clan_join is True:
                                logger.info(f'{self.session_name} | Joined our clan')
                            elif clan_join is False:
                                await asyncio.sleep(3)
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
                        if time() - turbo_time > 10:
                            active_turbo = False
                            turbo_time = 0

                    profile_data = await self.send_taps(http_client=http_client, nonce=nonce, taps=taps)

                    if not profile_data:
                        continue

                    available_energy = profile_data['currentEnergy']
                    new_balance = profile_data['coinsAmount']
                    calc_taps = new_balance - balance
                    balance = new_balance

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

                #thx Freddywhest
                if profile_data['currentBoss']['level'] == 13 and profile_data['currentBoss']['currentHealth'] == 0:
                    logger.info(f"{self.session_name} | 👉 <e>Finished defeating all bosses. No bosses left to fight.</e> | "
                                    f"| Balance: <c>{balance}</c> (<g>No coin added 😥</g>)")
                else:
                    if calc_taps > 0:
                        logger.success(
                            f"{self.session_name} | ✅ Successful tapped! 🔨 | 👉 Current energy: {available_energy} | ⚡️ Minimum energy limit: {settings.MIN_AVAILABLE_ENERGY} | "
                            f"Balance: <c>{balance}</c> (<g>+{calc_taps} 😊</g>) | "
                            f"Boss health: <e>{boss_current_health}</e>")
                    else:
                        logger.info(f"{self.session_name} | 🚫 Faild tapped! 🔨 | "
                                    f"Balance: <c>{balance}</c> (<g>No coin added 😥</g>) | 👉 Current energy: {available_energy} | ⚡️ Minimum energy limit: {settings.MIN_AVAILABLE_ENERGY} |"
                                    f"Boss health: <e>{boss_current_health}</e>")
                        logger.info(f"{self.session_name} | 😴 Sleep 10m")
                        await asyncio.sleep(delay=600)
                        noBalance = True

                    if boss_current_health <= 0:
                        logger.info(f"{self.session_name} | 👉 Setting next boss: <m>{current_boss_level + 1}</m> lvl")
                        logger.info(f"{self.session_name} | 😴 Sleep 15m")
                        await asyncio.sleep(delay=900)

                        status = await self.set_next_boss(http_client=http_client)
                        if status is True:
                            logger.success(f"{self.session_name} | ✅ Successful setting next boss: "
                                           f"<m>{current_boss_level + 1}</m>")

                    if active_turbo is False:
                        if (energy_boost_count > 0
                                and available_energy < settings.MIN_AVAILABLE_ENERGY
                                and settings.APPLY_DAILY_ENERGY is True):
                            logger.info(f"{self.session_name} | 😴 Sleep 7s before activating the daily energy boost")
                            await asyncio.sleep(delay=9)

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
                            status = await self.upgrade_boost(http_client=http_client,
                                                              boost_type=UpgradableBoostType.TAP)
                            if status is True:
                                logger.success(f"{self.session_name} | 👉 Tap upgraded to {next_tap_level} lvl")

                                await asyncio.sleep(delay=6)

                        if settings.AUTO_UPGRADE_ENERGY is True and next_energy_level <= settings.MAX_ENERGY_LEVEL:
                            status = await self.upgrade_boost(http_client=http_client,
                                                              boost_type=UpgradableBoostType.ENERGY)
                            if status is True:
                                logger.success(f"{self.session_name} | 👉 Energy upgraded to {next_energy_level} lvl")

                                await asyncio.sleep(delay=6)

                        if settings.AUTO_UPGRADE_CHARGE is True and next_charge_level <= settings.MAX_CHARGE_LEVEL:
                            status = await self.upgrade_boost(http_client=http_client,
                                                              boost_type=UpgradableBoostType.CHARGE)
                            if status is True:
                                logger.success(f"{self.session_name} | 👉 Charge upgraded to {next_charge_level} lvl")

                                await asyncio.sleep(delay=6)

                        if available_energy < settings.MIN_AVAILABLE_ENERGY:
                            logger.info(f"{self.session_name} | 👉 Minimum energy reached: {available_energy}")
                            logger.info(f"{self.session_name} | 😴 Sleep {settings.SLEEP_BY_MIN_ENERGY}s")

                            await asyncio.sleep(delay=settings.SLEEP_BY_MIN_ENERGY)

                            continue

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | ❗️Unknown error: {error}")
                    await asyncio.sleep(delay=9)

                else:
                    sleep_between_clicks = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])

                    if active_turbo is True:
                        sleep_between_clicks = 10
                    elif noBalance is True:
                        sleep_between_clicks = 700

                    logger.info(f"😴 Sleep {sleep_between_clicks}s")
                    await asyncio.sleep(delay=sleep_between_clicks)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | ❗️Invalid Session")
