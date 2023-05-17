import decimal
from decimal import localcontext
from typing import NewType
from web3.types import Wei


Wei = Wei
Sun = NewType('Sun', int)


def from_sun(number: int):
    """
    Convert a value in SUN to TRX.
    """

    unit_value = decimal.Decimal('1000000')

    with localcontext() as ctx:
        ctx.prec = 999
        d_number = decimal.Decimal(value=number, context=ctx)
        result_value = d_number / unit_value

    return result_value


def to_sun(number: int) -> int:
    """
    Convert a value in TRX to SUN.
    """

    d_number = decimal.Decimal(value=number)

    s_number = str(number)
    unit_value = decimal.Decimal('1000000')

    if d_number == 0:
        return 0

    if d_number < 1 and '.' in s_number:
        with localcontext() as ctx:
            multiplier = len(s_number) - s_number.index('.') - 1
            ctx.prec = multiplier
            d_number = decimal.Decimal(value=number, context=ctx) * 10 ** multiplier
        unit_value /= 10 ** multiplier

    with localcontext() as ctx:
        ctx.prec = 999
        result_value = decimal.Decimal(value=d_number, context=ctx) * unit_value

    return int(result_value)
