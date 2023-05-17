import sys
import requests
import random
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from web3 import Account
from web3 import Web3, HTTPProvider
from web3.types import HexBytes, TxParams
from eth_utils import to_checksum_address

from gas_calculator.app import init_app
from gas_calculator.abi.erc20 import ERC20_ABI
from gas_calculator.config import Config
from .test_utils import add_decimals


# get usdt https://chaindrop.org/?chainid=11155111&token=0x6175a8471c2122f778445e7e07a164250a19e661

ADDRESS_1 = {'address': to_checksum_address('0x96d2aab66eC89fb172471e4F7e855FF2f9751309'),
            'pk': HexBytes('0xab22b55f3b41b78ec092c92094ae368bd5aa70b744113e03841a734eefa8d14d')}

ADDRESS_2 = {'address': to_checksum_address('0xA9644504d7DFC47cff229beE12106B473fF1f7dd'),
            'pk': HexBytes('0xd6145debe9bb734191afff4bb64d7a88df140d5acae0ca3e4ac0394a4a9304bf')}


NODE = 'https://sepolia.infura.io/v3/1d329d459a73487cb7752be3262b5090'
USDT_CONTRACT = to_checksum_address('0x6175a8471C2122f778445e7E07A164250a19E661')


@pytest.mark.asyncio
async def test_api(aiohttp_client):
    client = await aiohttp_client(init_app())
    print(client.app['config'].ETH_NODE)
    from_address = random.choice([ADDRESS_1, ADDRESS_2])
    to_address = next(filter(lambda a: a != from_address, [ADDRESS_1, ADDRESS_2]))
    value = add_decimals(1, 18)

    provider = Web3(HTTPProvider(client.app['config'].ETH_NODE))
    acct = provider.eth.account.from_key(from_address['pk'])
    contract = provider.eth.contract(USDT_CONTRACT, abi=ERC20_ABI)
    func = contract.functions.transfer(to_address['address'], value)
    print(from_address)
    res = await client.post('/eth', json={
        'contract_address': USDT_CONTRACT,
        'to_address': to_address['address'],
        'from_address':  from_address['address'],
        'value': value
    })

    print(await res.json())
    assert res.status == 200
    fee_data = await res.json()

    assert fee_data['gas'] < Config.ETH_MAX_GAS_RESTRICTION
    assert fee_data['maxFeePerGas'] < Config.ETH_MAX_FEE_RESTRICTION
    assert fee_data['maxPriorityFeePerGas'] < Config.ETH_MAX_PRIORITY_FEE_RESTRICTION


    params = {
        'chainId': provider.eth.chain_id,
        'value': 0,
        'from': from_address['address'],
        'type': '0x2',
        'gas': fee_data['gas'],
        "maxFeePerGas": fee_data['maxFeePerGas'],
        "maxPriorityFeePerGas": fee_data['maxPriorityFeePerGas'],
        "nonce": provider.eth.get_transaction_count(from_address['address'])
    }

    func.build_transaction(params)

