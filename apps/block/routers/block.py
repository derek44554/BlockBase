from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.ins.ins_open import InsOpen
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.block_model import BlockModel
from blocklink.utils.ins_except import InsCertException
from blocklink.utils.send import execute_send_ins

from apps.block.utils.block import BlockDB
from apps.block.utils.correction import block_correction
from apps.block.utils.db_block import (
    get_block_by_bid,
    get_blocks_by_bids,
    get_block_count,
    get_blocks_paginated,
    engine,
)
from starlette.websockets import WebSocket
from websockets import ClientConnection

block_route = RouteBlock(route="/block")


@block_route.cert("/all")
async def block_cert_all(node_model: NodeModel, ins_cert: InsCert):
    """
    获取这个节点全部的Block 带有分页
    :param node_model:
    :param ins_cert:
    :return:
    """
    page = int(ins_cert.data.get("page", 1))
    limit = int(ins_cert.data.get("limit", 10))

    # "desc", "asc"
    order = ins_cert.data.get("order")

    model = ins_cert.data.get("model")

    tag = ins_cert.data.get("tag")

    permission_level = 3

    # 排除的 model 列表，可以不传或为空列表
    exclude_models = ins_cert.data.get("exclude_models")
    if exclude_models is not None and not isinstance(exclude_models, list):
        exclude_models = None

    total = get_block_count(model=model, tag=tag, exclude_models=exclude_models, permission_level=permission_level)
    if total == 0:
        return {"count": 0, "page": page, "limit": limit, "items": []}

    blocks = get_blocks_paginated(
        page=page,
        limit=limit,
        order=order,
        model=model,
        tag=tag,
        exclude_models=exclude_models,
        permission_level=permission_level,
    )
    items = [block.json_data for block in blocks]

    return {"count": total, "page": page, "limit": limit, "items": items}


@block_route.cert("/get")
async def block_cert_get(node_model: NodeModel, ins_cert: InsCert):
    """
    获取单个Block
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的BID
    bid = ins_cert.data["bid"]

    block_db = get_block_by_bid(bid)
    # 是否BID不存在
    if block_db is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31)

    # -------------- 权限判断

    return block_db.json_data


@block_route.cert("/multiple")
async def block_multiple(node_model: NodeModel, ins_cert: InsCert):
    """
    获取多个Block
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的BID列表，确保它是一个列表
    bids = ins_cert.data.get("bids")

    if bids is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=42)

    # 获取多个Block 列表
    blocks = get_blocks_by_bids(bids, permission_level=3)

    # -------------- 权限判断

    # 准备要发送的数据
    block_data = [block.json_data for block in blocks]

    return {"blocks": block_data, "deny_bids": []}
