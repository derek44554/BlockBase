from blocklink.models.routers.route_block_app import RouteApp

from .routers.apps import apps_route


route_app = RouteApp("/apps", title="Apps")
route_app.add(apps_route)
