import asyncio
from itertools import chain
from enum import Enum
from statistics import fmean
from web3.contract.async_contract import AsyncContractFunction
from web3 import AsyncHTTPProvider, AsyncWeb3
from eth_utils.curried import from_wei
from eth_utils import to_checksum_address
from loguru import logger

from gas_calculator.abi.erc20 import ERC20_ABI
from gas_calculator.utils.errors import InsufficientFundsError, ExceedError
from gas_calculator.calculators import BaseCalculator
from gas_calculator.config import Config
from gas_calculator.utils.token_types import Wei


class EthCalculator(BaseCalculator):

    class TxTypes(Enum):
        Legacy = '0x0'
        EIP1559 = '0x2'

    def __init__(self, node):
        self.node = node
        self.provider = AsyncWeb3(AsyncHTTPProvider(node))
        self.chain_id = None

    @classmethod
    async def async_init(cls, node) -> 'EthCalculator':
        self = cls(node)
        self.chain_id = await self.provider.eth.chain_id
        return self

    async def calculate_gas_crypto(self, from_address, to_address, value):
        raise NotImplemented

    async def calculate_gas_token(self, contract_address: str, to_address: str, from_address: str, value):

        contract_address, to_address, from_address = map(to_checksum_address,
                                                         [contract_address, to_address, from_address]
                                                         )

        for attempt in range(Config.ETH_CALCULATE_GAS_ATTEMPTS):
            try:
                return await self._calculate_gas_token(contract_address, to_address, from_address, value)

            except InsufficientFundsError as e:
                logger.error(e)
                raise

            except ExceedError as e:
                if attempt == Config.ETH_CALCULATE_GAS_ATTEMPTS-1:
                    logger.error(e)
                    raise

                logger.warning('Failed attempt during gas estimation - exceed funds: ETH')
                await asyncio.sleep(1)

            except Exception:

                if attempt == Config.ETH_CALCULATE_GAS_ATTEMPTS-1:
                    logger.exception('Failed attempt during gas estimation: ETH - return default fee params')

                    return {'gas': Config.ETH_DEFAULT_GAS,
                            'maxFeePerGas': Config.ETH_DEFAULT_MAX_FEE,
                            'maxPriorityFeePerGas': Config.ETH_DEFAULT_MAX_PRIORITY_FEE}

                logger.warning('Failed attempt during gas estimation: ETH')

    async def _calculate_gas_token(self, contract_address, to_address, from_address, value):
        max_priority_fee_per_gas = await self.get_max_priority_fee_per_gas()
        base_fee_per_gas = await self.get_base_fee_per_gas()
        max_fee_per_gas = base_fee_per_gas + max_priority_fee_per_gas

        params = {
            'chainId': self.chain_id,
            'value': 0,
            'from': from_address,
            'type': self.TxTypes.EIP1559.value,
            'maxPriorityFeePerGas': max_priority_fee_per_gas,
            'maxFeePerGas': max_fee_per_gas
        }

        if max_fee_per_gas > Config.ETH_MAX_FEE_RESTRICTION or \
                max_priority_fee_per_gas > Config.ETH_MAX_PRIORITY_FEE_RESTRICTION:

            raise ExceedError(f'Estimated gas fee was much higher than expected:'
                              f' maxFeePerGas={max_fee_per_gas}'
                              f' (x{max_fee_per_gas * 1.0 / Config.ETH_MAX_FEE_RESTRICTION}),'
                              f' maxPriorityFeePerGas={max_priority_fee_per_gas}'
                              f' (x{max_priority_fee_per_gas * 1.0 / Config.ETH_MAX_PRIORITY_FEE_RESTRICTION})')

        contract = self.provider.eth.contract(contract_address, abi=ERC20_ABI)
        func = contract.functions.transfer(to_address, value)
        gas = await self.estimate_gas(params, func, contract, value)

        if gas > Config.ETH_MAX_GAS_RESTRICTION:
            raise ExceedError(f'Estimated amount of gas was much higher than expected: {gas=}')

        logger.info(f"Gas - {gas}, "
                    f"maxFeePerGas - {from_wei(max_fee_per_gas, 'gwei')}G, "
                    f"maxPriorityFeePerGas - {from_wei(max_priority_fee_per_gas, 'gwei')}G"
              )

        return {'gas': gas, 'maxFeePerGas': max_fee_per_gas, 'maxPriorityFeePerGas': max_priority_fee_per_gas}

    async def estimate_gas(self, tx_params, func: AsyncContractFunction, contract, value) -> int:
        try:
            gas = await func.estimate_gas(tx_params)
            return round(gas * Config.ETH_GAS_MULTIPLIER)
        except ValueError as e:
            error = e.args[0]

            if not isinstance(error, dict):
                raise

            if error['message'] == 'insufficient funds for transfer':
                balance = await self.provider.eth.get_balance(tx_params["from"])
                raise InsufficientFundsError(f'insufficient eth funds for transfer; '
                                             f'user {tx_params["from"]} eth balance {balance}'
                                             )

            if error['message'] == 'invalid opcode: INVALID':
                balance = await contract.functions.balanceOf(tx_params['from']).call()
                if value > balance:
                    raise InsufficientFundsError(f'insufficient token funds for transfer: user balance - {balance}, value - {value}')
                else:
                    raise

    async def get_base_fee_per_gas(self) -> Wei:
        block = await self.provider.eth.get_block('pending')
        base_fee_per_gas = block['baseFeePerGas']
        return Wei(round(base_fee_per_gas * Config.ETH_BASE_FEE_PER_GAS_MULTIPLIER))

    async def get_max_priority_fee_per_gas(self) -> Wei:
        """
        Tips to the miner. if higher, the more likely your transaction will be included in the block.
        """
        history = await self.provider.eth.fee_history(
            Config.ETH_PRIORITY_BLOCKS_COUNT,
            "latest",
            [Config.ETH_PRIORITY_PERCENTILE]
        )
        return Wei(
            round(
                fmean(
                    chain.from_iterable(
                        history['reward']
                    )
                )
            )
        )
