from enum import Enum


class Query(str, Enum):
    QUERY_GAME_CONFIG = "query QUERY_GAME_CONFIG {\n telegramGameGetConfig {\n ...FragmentBossFightConfig\n __typename\n }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n _id\n coinsAmount\n currentEnergy\n maxEnergy\n weaponLevel\n zonesCount\n tapsReward\n energyLimitLevel\n energyRechargeLevel\n tapBotLevel\n currentBoss {\n _id\n level\n currentHealth\n maxHealth\n __typename\n }\n freeBoosts {\n _id\n currentTurboAmount\n maxTurboAmount\n turboLastActivatedAt\n turboAmountLastRechargeDate\n currentRefillEnergyAmount\n maxRefillEnergyAmount\n refillEnergyLastActivatedAt\n refillEnergyAmountLastRechargeDate\n __typename\n }\n bonusLeaderDamageEndAt\n bonusLeaderDamageStartAt\n bonusLeaderDamageMultiplier\n nonce\n __typename\n}"
    MutationTelegramUserLogin = "mutation MutationTelegramUserLogin($webAppData: TelegramWebAppDataInput!) {\n  telegramUserLogin(webAppData: $webAppData) {\n    access_token\n    __typename\n  }\n}"
    MutationGameProcessTapsBatch = "mutation MutationGameProcessTapsBatch($payload: TelegramGameTapsBatchInput!) {\n  telegramGameProcessTapsBatch(payload: $payload) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  nonce\n  __typename\n}"
    telegramGameSetNextBoss = "mutation telegramGameSetNextBoss {\n telegramGameSetNextBoss {\n ...FragmentBossFightConfig\n __typename\n }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n _id\n coinsAmount\n currentEnergy\n maxEnergy\n weaponLevel\n zonesCount\n tapsReward\n energyLimitLevel\n energyRechargeLevel\n tapBotLevel\n currentBoss {\n _id\n level\n currentHealth\n maxHealth\n __typename\n }\n freeBoosts {\n _id\n currentTurboAmount\n maxTurboAmount\n turboLastActivatedAt\n turboAmountLastRechargeDate\n currentRefillEnergyAmount\n maxRefillEnergyAmount\n refillEnergyLastActivatedAt\n refillEnergyAmountLastRechargeDate\n __typename\n }\n bonusLeaderDamageEndAt\n bonusLeaderDamageStartAt\n bonusLeaderDamageMultiplier\n nonce\n __typename\n}"
    telegramGameActivateBooster = "mutation telegramGameActivateBooster($boosterType: BoosterType!) {\n  telegramGameActivateBooster(boosterType: $boosterType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  nonce\n  __typename\n}"
    telegramGamePurchaseUpgrade = "mutation telegramGamePurchaseUpgrade($upgradeType: UpgradeType!) {\n  telegramGamePurchaseUpgrade(type: $upgradeType) {\n    ...FragmentBossFightConfig\n    __typename\n  }\n}\n\nfragment FragmentBossFightConfig on TelegramGameConfigOutput {\n  _id\n  coinsAmount\n  currentEnergy\n  maxEnergy\n  weaponLevel\n  energyLimitLevel\n  energyRechargeLevel\n  tapBotLevel\n  currentBoss {\n    _id\n    level\n    currentHealth\n    maxHealth\n    __typename\n  }\n  freeBoosts {\n    _id\n    currentTurboAmount\n    maxTurboAmount\n    turboLastActivatedAt\n    turboAmountLastRechargeDate\n    currentRefillEnergyAmount\n    maxRefillEnergyAmount\n    refillEnergyLastActivatedAt\n    refillEnergyAmountLastRechargeDate\n    __typename\n  }\n  nonce\n  __typename\n}"
    QueryTelegramUserMe = "query QueryTelegramUserMe {\n  telegramUserMe {\n    firstName\n    lastName\n    telegramId\n    username\n    referralCode\n    isDailyRewardClaimed\n    referral {\n      username\n      lastName\n      firstName\n      bossLevel\n      coinsAmount\n      __typename\n    }\n    isReferralInitialJoinBonusAvailable\n    league\n    leagueIsOverTop10k\n    leaguePosition\n    _id\n    opens {\n      isAvailable\n      openType\n      __typename\n    }\n    features\n    __typename\n  }\n}"
    TapbotConfig = "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nquery TapbotConfig {\n  telegramGameTapbotGetConfig {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
    TapbotStart = "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotStart {\n  telegramGameTapbotStart {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
    TapbotClaim = "fragment FragmentTapBotConfig on TelegramGameTapbotOutput {\n  damagePerSec\n  endsAt\n  id\n  isPurchased\n  startsAt\n  totalAttempts\n  usedAttempts\n  __typename\n}\n\nmutation TapbotClaim {\n  telegramGameTapbotClaimCoins {\n    ...FragmentTapBotConfig\n    __typename\n  }\n}"
    Mutation = "mutation Mutation {\n  telegramUserClaimReferralBonus\n}"
    ClanMy = "fragment FragmentClanProfile on ClanProfileOutput {\n id\n clanDetails {\n id\n name\n rarity\n username\n avatarImageUrl\n coinsAmount\n createdAt\n description\n membersCount\n __typename\n }\n clanOwner {\n id\n userId\n username\n avatarImageUrl\n coinsAmount\n currentBossLevel\n firstName\n lastName\n isClanOwner\n isMe\n __typename\n }\n __typename\n}\n\nquery ClanMy {\n clanMy {\n ...FragmentClanProfile\n __typename\n }\n}"
    Leave = "mutation Mutation {\n  clanActionLeaveClan\n}"
    Join = "mutation ClanActionJoinClan($clanId: String!) {\n clanActionJoinClan(clanId: $clanId)\n}"
    #сейчас не используются

    #TelegramMemefiWalletConfig = "query TelegramMemefiWalletConfig {\n telegramMemefiWalletConfig {\n rpcUrls\n memefiContractAddress\n listingDate\n __typename\n }\n}"
    #TelegramMemefiWallet = "query TelegramMemefiWallet {\n telegramMemefiWallet {\n walletAddress\n dropMemefiAmountWei\n signedTransaction {\n contractAddress\n functionName\n contractType\n deadline\n nativeTokenValue\n chainId\n execTransactionValuesStringified\n __typename\n }\n __typename\n }\n}"
    #PaymentsTokens = "query PaymentsTokens {\n paymentsTokens {\n paymentToken\n tokenAddress\n toUsdRate\n __typename\n }\n}"
    

    #clanProfile = "fragment FragmentClanProfile on ClanProfileOutput {\n id\n clanDetails {\n id\n name\n rarity\n username\n avatarImageUrl\n coinsAmount\n createdAt\n description\n membersCount\n __typename\n }\n clanOwner {\n id\n userId\n username\n avatarImageUrl\n coinsAmount\n currentBossLevel\n firstName\n lastName\n isClanOwner\n isMe\n __typename\n }\n __typename\n}\n\nquery clanProfile($clanId: String!) {\n clanProfile(clanId: $clanId) {\n ...FragmentClanProfile\n __typename\n }\n}"
    #ClanMembersPaginated = "query ClanMembersPaginated($clanId: String!, $pagination: PaginationInput!) {\n clanMembersPaginated(clanId: $clanId, pagination: $pagination) {\n items {\n id\n userId\n username\n firstName\n lastName\n avatarImageUrl\n coinsAmount\n currentBossLevel\n isClanOwner\n isMe\n __typename\n }\n meta {\n currentPage\n itemCount\n itemsPerPage\n totalItems\n totalPages\n __typename\n }\n __typename\n }\n}"

class OperationName(str, Enum):
    QUERY_GAME_CONFIG = "QUERY_GAME_CONFIG"
    MutationTelegramUserLogin = "MutationTelegramUserLogin"
    MutationGameProcessTapsBatch = "MutationGameProcessTapsBatch"
    telegramGameSetNextBoss = "telegramGameSetNextBoss"
    telegramGameActivateBooster = "telegramGameActivateBooster"
    telegramGamePurchaseUpgrade = "telegramGamePurchaseUpgrade"
    QueryTelegramUserMe = "QueryTelegramUserMe"
    TapbotConfig = "TapbotConfig"
    TapbotStart = "TapbotStart"
    TapbotClaim = "TapbotClaim"
    Mutation = "Mutation"
    ClanMy = "ClanMy"
    Leave = "Mutation"
    Join = "ClanActionJoinClan"
    #сейчас не используются
    #TelegramMemefiWalletConfig = "TelegramMemefiWalletConfig"
    #TelegramMemefiWallet = "TelegramMemefiWallet"
    #PaymentsTokens = "PaymentsTokens"
    
    #clanProfile = "clanProfile"
    #ClanMembersPaginated = "ClanMembersPaginated"
