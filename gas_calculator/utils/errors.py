import json
from aiohttp.web_exceptions import HTTPBadRequest


class BaseError(Exception):
    err_code = None

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class InsufficientFundsError(BaseError):
    err_code = 'insufficient_funds'


class ExceedError(BaseError):
    err_code = 'exceed_funds'


class HTTPBadRequestJson(HTTPBadRequest):

    def __init__(self, data: dict, *args, **kwargs):
        super().__init__(text=json.dumps(data), content_type='application/json', *args, **kwargs)
