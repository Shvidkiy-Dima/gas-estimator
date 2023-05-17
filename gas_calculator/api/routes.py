from .views import calculate_eth, calculate_tron


def add_routes(app):
    app.router.add_route('POST', r'/eth', calculate_eth, name='eth')
    app.router.add_route('POST', r'/tron', calculate_tron, name='tron')
