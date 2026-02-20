from blocklink.models.routers.route_block_app import RouteApp
from .routers.file import file_route
from .routers.ipfs import ipfs_fast_api

ipfs_app = RouteApp("/ipfs", title="IPFS")
ipfs_app.add(file_route)
ipfs_app.add_api(name="/ipfs", api_router=ipfs_fast_api)
