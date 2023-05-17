import logging
import os
from aiohttp import web
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.logging import EventHandler

from gas_calculator.config import Config
from gas_calculator.startups import init_calculators
from gas_calculator.cleanups import cleanup_calculators
from gas_calculator.api.routes import add_routes


def init_app() -> web.Application:
    app = web.Application()

    app['config'] = Config
    logger.info(f'Start {os.environ.get("ENV", "prod")} env')

    sentry_sdk.init(dsn=Config.SENTRY_DSN,
                    environment=Config.SENTRY_ENVIRONMENT,
                    release=Config.SENTRY_RELEASE)

    if Config.SENTRY_DSN:
        logger.add(EventHandler(level=logging.ERROR), level=logging.ERROR)

    app.on_startup.append(init_calculators)
    app.on_cleanup.append(cleanup_calculators)
    add_routes(app)

    return app
