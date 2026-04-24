from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from apps.block.utils.db_block import get_block_by_bid, get_blocks_by_bids, engine, get_tag_block_count_by_name, get_blocks_by_tag_paginated


tag_route = RouteBlock(route="/tag")


@tag_route.cert("/count")
async def tag_count(node_model: NodeModel, ins_cert: InsCert):
    """
    获取 Tag 数量
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的标签名
    name = ins_cert.data["name"]

    # 获取该标签下的 Block 数量
    count = get_tag_block_count_by_name(name)

    return {"count": count}

@tag_route.cert("/multiple")
async def tag_multiple(node_model: NodeModel, ins_cert: InsCert):
    """
    获取 Tag 下的 Block 列表
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的标签名
    name = ins_cert.data["name"]
    page = int(ins_cert.data.get("page", 1))
    limit = int(ins_cert.data.get("limit", 10))

    # 获取总数
    total = get_tag_block_count_by_name(name)

    # 分页获取 Block 列表
    blocks = get_blocks_by_tag_paginated(name=name, page=page, limit=limit)

    # 准备要发送的数据
    items = [block.json_data for block in blocks]

    return {"count": total, "page": page, "limit": limit, "items": items}
