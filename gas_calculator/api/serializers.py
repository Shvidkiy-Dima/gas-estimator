from marshmallow import Schema,  fields
from gas_calculator.utils.token_types import Wei, Sun


class GasRequestSchema(Schema):
    contract_address = fields.String(required=True)
    to_address = fields.String(required=True)
    from_address = fields.String(required=True)
    value = fields.Integer(required=True)

    def dump(self, *args, **kwargs):
        res = super().dump(*args, **kwargs)
        res['amount'] = str(res['amount'])
        return res


class EthResponse:
    gas: int
    maxFeePerGas: Wei
    maxPriorityFeePerGas: Wei


class TronResponse:
    fee_limit: Sun


GasRequestSerializer = GasRequestSchema()