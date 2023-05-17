import os
from typing import Union

from eth_utils import to_wei
from pydantic import BaseSettings, Field

from gas_calculator.utils.token_types import to_sun


class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 8000

    ETH_NODE: str
    TRON_NODE: str

    ETH_PRIORITY_PERCENTILE: int = Field(75, ge=1, le=99)
    ETH_PRIORITY_BLOCKS_COUNT: int = 20
    ETH_BASE_FEE_PER_GAS_MULTIPLIER: float | int = 1.5
    ETH_GAS_MULTIPLIER: float | int = 1.5

    ETH_MAX_PRIORITY_FEE_RESTRICTION: int = Field(100, description='Gwei')
    ETH_MAX_FEE_RESTRICTION: int = Field(300, description='Gwei')
    ETH_MAX_GAS_RESTRICTION: int = 500_000
    ETH_CALCULATE_GAS_ATTEMPTS: int = 2
    ETH_DEFAULT_GAS: int = 100_000
    ETH_DEFAULT_MAX_FEE: int = Field(60, description='Gwei')
    ETH_DEFAULT_MAX_PRIORITY_FEE: int = Field(1, description='Gwei')

    TRON_FEE_LIMIT_RESTRICTION: int = Field(2000, description='TRX')
    TRON_FEE_MULTIPLIER: float = 3.0
    TRON_DEFAULT_ENERGY_PRICE: int = Field(420, description='Sun')
    TRON_DEFAULT_FEE_LIMIT: int = Field(10_000_000, description='SUN')
    TRON_API_KEY: str
    TRON_CALCULATE_FEE_LIMIT_ATTEMPTS: int = 2

    SENTRY_RELEASE: str | None
    SENTRY_ENVIRONMENT: str = "release"
    SENTRY_DSN: str | None


class DevSettings(Settings):
    TRON_API_KEY: str = ''
    ETH_NODE = 'https://sepolia.infura.io/v3/1d329d459a73487cb7752be3262b5090'
    TRON_NODE = 'https://api.nileex.io'


class TestSettings(Settings):
    TRON_API_KEY: str = ''
    ETH_NODE = 'https://sepolia.infura.io/v3/1d329d459a73487cb7752be3262b5090'
    TRON_NODE = 'https://api.nileex.io'


configs = dict(
    prod=Settings,
    dev=DevSettings,
    test=TestSettings,
)

Config: Union[Settings, TestSettings] = configs[os.environ.get('ENV', 'prod').lower()]()

Config.ETH_MAX_PRIORITY_FEE_RESTRICTION = to_wei(Config.ETH_MAX_PRIORITY_FEE_RESTRICTION, 'gwei')
Config.ETH_MAX_FEE_RESTRICTION = to_wei(Config.ETH_MAX_FEE_RESTRICTION, 'gwei')
Config.ETH_DEFAULT_MAX_FEE = to_wei(Config.ETH_DEFAULT_MAX_FEE, 'gwei')
Config.ETH_DEFAULT_MAX_PRIORITY_FEE = to_wei(Config.ETH_DEFAULT_MAX_PRIORITY_FEE, 'gwei')

Config.TRON_FEE_LIMIT_RESTRICTION = to_sun(Config.TRON_FEE_LIMIT_RESTRICTION)
