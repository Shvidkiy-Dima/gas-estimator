import asyncio
from aiohttp import ClientSession
from tronpy import AsyncTron
from tronpy.keys import to_base58check_address
from tronpy.providers import AsyncHTTPProvider
from loguru import logger

from gas_calculator.abi.erc20 import ERC20_ABI
from gas_calculator.calculators import BaseCalculator
from gas_calculator.config import Config
from gas_calculator.utils.token_types import Sun, from_sun
from gas_calculator.utils.errors import ExceedError


class TronCalculator(BaseCalculator):

    def __init__(self, api_url, api_key):
        self.tron_client = AsyncTron(AsyncHTTPProvider(api_url, api_key=api_key))
        self.http_client = ClientSession(headers={'TRON-PRO-API-KEY': api_key})
        self.node = self.tron_client.provider.endpoint_uri

    async def calculate_gas_crypto(self, from_address, to_address, value):
        raise NotImplemented

    async def calculate_gas_token(self, contract_address, to_address, from_address, value):

        for attempt in range(Config.TRON_CALCULATE_FEE_LIMIT_ATTEMPTS):
            try:
                return await self._calculate_gas_token(contract_address, to_address, from_address, value)

            except ExceedError as e:
                if attempt == Config.TRON_CALCULATE_FEE_LIMIT_ATTEMPTS-1:
                    logger.exception(e)
                    raise

                logger.warning('Failed attempt during gas estimation - exceed funds: Tron')
                await asyncio.sleep(1)

            except Exception:
                if attempt == Config.ETH_CALCULATE_GAS_ATTEMPTS - 1:
                    logger.exception('Failed attempt during gas estimation: TRON - return default fee params')
                    return {'fee_limit': Config.TRON_DEFAULT_FEE_LIMIT}

                logger.warning('Failed attempt during gas estimation: Tron')

    async def _calculate_gas_token(self, contract_address: str, to_address: str, from_address: str, value):
        try:
            energy_price = await self._get_energy_price()
        except Exception:
            logger.exception(f'Get energy price error, use default {Config.TRON_DEFAULT_ENERGY_PRICE}')
            energy_price = Config.TRON_DEFAULT_ENERGY_PRICE

        energy = await self._get_energy(contract_address, to_address, from_address, value)
        fee_limit = round(energy * energy_price * Config.TRON_FEE_MULTIPLIER)

        if fee_limit > Config.TRON_FEE_LIMIT_RESTRICTION:
            raise ExceedError(f'Estimated fee_limit was much higher than expected - fee_limit {from_sun(fee_limit)} TRX')

        logger.info(f'Fee limit: {from_sun(fee_limit)} TRX')
        return {'fee_limit': fee_limit}

    async def _get_energy_price(self) -> Sun:
        async with self.http_client.post(f'{self.node}/wallet/getenergyprices') as resp:
            res = await resp.json()
            energy_price = res['prices'].split(',')[-1].split(':')[1]
            return Sun(int(energy_price))

    async def _get_energy(self, contract_address, to_address, from_address, value) -> Sun:
        contract = await self.tron_client.get_contract(contract_address)
        if not contract.abi:
            contract.abi = ERC20_ABI

        c_function = contract.functions.transfer
        func_params = c_function._prepare_parameter(to_base58check_address(to_address), value)

        data = {
            "owner_address": from_address,
            "contract_address": contract_address,
            "function_selector": c_function.function_signature, #"transfer(address,uint256)",
            "parameter": func_params,
            "visible": True
        }

        async with self.http_client.post(f'{self.node}/wallet/triggerconstantcontract', json=data) as resp:
            res = await resp.json()
            return Sun(res['energy_used'])
