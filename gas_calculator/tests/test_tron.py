import random
import requests
import pytest

from eth_utils import to_checksum_address
from web3.types import TxParams
from tronpy import Tron
from tronpy.keys import to_base58check_address, PrivateKey
from tronpy.exceptions import TransactionNotFound

from gas_calculator.config import Config
from gas_calculator.app import init_app
from .test_utils import add_decimals


# get usdt https://chaindrop.org/?chainid=11155111&token=0x6175a8471c2122f778445e7e07a164250a19e661


ADDRESS_1 = {'address': to_base58check_address('TT4iJm5ATF7KpN5GjGsXvzde7Xt9mnB3gL'),
            'pk': 'b616af6260ca3a78347af8bcafe60f2ec5ca8ca7b2907e82aafbd5f7fdc9ce2c'}

ADDRESS_2 = {'address': to_base58check_address('TQ8ki9iyazUBFmWkP34f5E6CsXaENXrPPh'),
            'pk': '42285c95117e698e67c1d0d72c23ed911a1af617b3ed6a38c8d690f21a22117f'}


USDT_CONTRACT = 'TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj'


@pytest.mark.asyncio
async def test_tron(aiohttp_client):
    client = await aiohttp_client(init_app())

    from_address = random.choice([ADDRESS_1, ADDRESS_2])
    to_address = next(filter(lambda a: a != from_address, [ADDRESS_1, ADDRESS_2]))

    provider = Tron(network='nile')
    contract = provider.get_contract(to_base58check_address(USDT_CONTRACT))
    value = add_decimals(0.1, 6)

    res = await client.post('/tron', json={
        'contract_address': USDT_CONTRACT,
        'to_address': to_address['address'],
        'from_address':  from_address['address'],
        'value': 0
    })

    assert res.status == 200

    fee_limit = (await res.json())['fee_limit']

    assert fee_limit < Config.TRON_FEE_LIMIT_RESTRICTION

    contract.functions.transfer(to_base58check_address(to_address['address']), value) \
        .with_owner(from_address['address']) \
        .fee_limit(fee_limit) \
        .build() \
        .sign(PrivateKey(bytes.fromhex(from_address['pk'])))


