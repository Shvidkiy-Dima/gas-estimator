from aiohttp import web

from gas_calculator.calculators.eth import EthCalculator
from gas_calculator.calculators.tron import TronCalculator
from gas_calculator.config import Config


async def init_calculators(app: web.Application):
    app['eth_calculator'] = await EthCalculator.async_init(Config.ETH_NODE)
    app['tron_calculator'] = TronCalculator(Config.TRON_NODE, Config.TRON_API_KEY)