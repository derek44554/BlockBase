from blocklink.models.routers.route_block_app import RouteApp
from .routers.file import file_route
from .routers.ipfs import ipfs_fast_api

route_app = RouteApp("/ipfs", title="IPFS")
route_app.add(file_route)
route_app.add_api(name="/ipfs", api_router=ipfs_fast_api)
