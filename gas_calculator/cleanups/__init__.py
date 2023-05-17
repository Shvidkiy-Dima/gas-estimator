from aiohttp import web


async def cleanup_calculators(app: web.Application):
    await app['tron_calculator'].http_client.close()
