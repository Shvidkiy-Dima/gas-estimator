from abc import ABC, abstractmethod


class BaseCalculator(ABC):

    @abstractmethod
    async def calculate_gas_crypto(self, from_address, to_address, value):
        ...

    @abstractmethod
    async def calculate_gas_token(self, contract_address, to_address, from_address, value):
        ...
