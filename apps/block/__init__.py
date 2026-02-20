from blocklink.models.routers.route_block_app import RouteApp
from .routers.block import block_route
from .routers.delete import delete_route
from .routers.link import link_route
from .routers.tag import tag_route
from .routers.write import write_route
from .utils.db_block import create_db
from .routers.block_api import block_fast_api
from .routers.link_api import link_fast_api


# 创建数据库
create_db()

block_app = RouteApp("/block", title="Block")
block_app.add(block_route)
block_app.add(link_route)
block_app.add(tag_route)
block_app.add(write_route)
block_app.add(delete_route)

block_app.add_api(name="/block", api_router=block_fast_api)
block_app.add_api(name="/link", api_router=link_fast_api)