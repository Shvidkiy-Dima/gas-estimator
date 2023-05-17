from aiohttp import web
from marshmallow import ValidationError

from gas_calculator.calculators import BaseCalculator
from gas_calculator.utils.errors import ExceedError, InsufficientFundsError, HTTPBadRequestJson
from .serializers import GasRequestSerializer, EthResponse, TronResponse


async def calculate_eth(request: web.Request):
    calculator = request.app['eth_calculator']
    fee: EthResponse = await _calculate(request, calculator)
    return web.json_response(fee, status=200)


async def calculate_tron(request: web.Request):
    calculator = request.app['tron_calculator']
    fee: TronResponse = await _calculate(request, calculator)
    return web.json_response(fee, status=200)


async def _calculate(request: web.Request, calculator: BaseCalculator):

    try:
        data = GasRequestSerializer.load(await request.json())
    except ValidationError as err:
        raise HTTPBadRequestJson(err.messages)

    try:
        fee = await calculator.calculate_gas_token(**data)
    except ExceedError as e:
        raise HTTPBadRequestJson({'error': str(e), 'code': e.err_code})

    except InsufficientFundsError as e:
        raise HTTPBadRequestJson({'error': str(e), 'code': e.err_code})

    except Exception as e:
        raise HTTPBadRequestJson({'error': str(e), 'code': None})

    return fee
