from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    MIN_AVAILABLE_ENERGY: int = 300
    SLEEP_BY_MIN_ENERGY: int = 314

    ADD_TAPS_ON_TURBO: list[int] = [500, 1500]

    AUTO_BUY_TAPBOT: bool = True

    AUTO_UPGRADE_TAP: bool = False
    MAX_TAP_LEVEL: int = 5
    AUTO_UPGRADE_ENERGY: bool = False
    MAX_ENERGY_LEVEL: int = 5
    AUTO_UPGRADE_CHARGE: bool = False
    MAX_CHARGE_LEVEL: int = 3

    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_TURBO: bool = True

    RANDOM_TAPS_COUNT: list[int] = [7, 31]
    SLEEP_BETWEEN_TAP: list[int] = [19, 36]

    USE_PROXY_FROM_FILE: bool = False
    
    REF: bool = True
    REF_ID: str = ''

    EMERGENCY_STOP: bool = False

    ROLL_CASINO: bool = True
    VALUE_SPIN: int = 1
    LOTTERY_INFO: bool = True

    LINEA_WALLET: bool = True
    LINEA_SHOW_BALANCE: bool = False
    LINEA_API: str = ''

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = [3, 15]

    WATCH_VIDEO: bool = True


settings = Settings()
