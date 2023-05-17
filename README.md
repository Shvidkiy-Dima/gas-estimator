
# Gas_calculator

## technology stack

- python 3.10+
- is not using databases
- aiohttp
- async by default

## Run

```shell
docker build . -t gas_calculator
docker run -p 8000:8000 gas_calculator --env-file ./.env
```

## Run tests

```shell
docker build . -t gas_calculator
docker run -e ENV=test pytest .
```


## Usage

Endpoint `/eth` POST

Request:

```json
{
  "contract_address": "0x6175a8471C2122f778445e7E07A164250a19E661", 
 "to_address": "0x96d2aab66eC89fb172471e4F7e855FF2f9751309", 
 "from_address": "0xDC79ed8051e4BFE82C5CcFf711cd6B573910e53C",
 "value": 1000000000000000000
}
```
Response:
```json
{
	"gas": 32448,
	"maxFeePerGas": 37549573831,
	"maxPriorityFeePerGas": 2157325625
}
```

Endpoint `/tron` POST

Request:

```json
{
  "contract_address":  "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
 "to_address": "TVxbJ1nXoNjr4eyEnB67hcrV6CaqRfzkSS",
 "from_address": "TZ9VCSxse7AJgDHpQwsmRWG3UEmUAVbJXy",
 "value": 453220000000
}
```
Response:
```json
{
	"fee_limit": 5223960
}
```


## Environment variables

| Variable                          | Default  | Comments                                          |
|-----------------------------------|----------|---------------------------------------------------|
| ENV                               | prod     | prod, test, dev                                   |
| HOST                              | 0.0.0.0  |                                                   |
| PORT                              | 8000     |                                                   |
| ETH_NODE                          |          | eth node                                          |
| TRON_NODE                         |          | tron node                                         |
| TRON_API_KEY                      |          | tron api key                                      |
| SENTRY_DSN                        |          | sentry dsn                                        |
| SENTRY_ENVIRONMENT                | release  | sentry environment                                |
| SENTRY_RELEASE                    |          | sentry release                                    |
| ETH_PRIORITY_PERCENTILE           | 75       | 0<n<100 - чем выше - тем выше PRIORITY_FEE        |
| ETH_PRIORITY_BLOCKS_COUNT         | 20       |                                                   |
| ETH_BASE_FEE_PER_GAS_MULTIPLIER   | 1.5      | чем выше - тем выше MAX_FEE                       |
| ETH_GAS_MULTIPLIER                | 1.5      | чем выше - тем выше GAS                           |
| ETH_MAX_PRIORITY_FEE_RESTRICTION  | 100      | Gwei                                              |
| ETH_MAX_FEE_RESTRICTION           | 300      | Gwei                                              |
| ETH_MAX_GAS_RESTRICTION           | 500000   | кол-во газа                                       |
| ETH_CALCULATE_GAS_ATTEMPTS        | 2        |                                                   |
| ETH_DEFAULT_GAS                   | 100000   | кол-во газа, в случае неудачи вернем это значение |
| ETH_DEFAULT_MAX_FEE               | 60       | Gwei, в случае неудачи вернем это значение        |
| ETH_DEFAULT_MAX_PRIORITY_FEE      | 1        | Gwei, в случае неудачи вернем это значение        |
| TRON_FEE_LIMIT_RESTRICTION        | 2000     | TRX                                               |
| TRON_FEE_MULTIPLIER               | 3        | чем выше - тем выше FEE_LIMIT                     |
| TRON_DEFAULT_ENERGY_PRICE         | 420      | SUN                                               |
| TRON_DEFAULT_FEE_LIMIT            | 10000000 | SUN - в случае неудачи вернем это значение        |
| TRON_CALCULATE_FEE_LIMIT_ATTEMPTS | 2        |                                                   |

