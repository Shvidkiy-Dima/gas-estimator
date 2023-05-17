import uvloop
from aiohttp import web
from gas_calculator.app import init_app


def main() -> None:
    uvloop.install()
    app = init_app()
    web.run_app(app, host=app['config'].HOST, port=app['config'].PORT)


if __name__ == '__main__':
    main()
