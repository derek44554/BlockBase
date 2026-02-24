from blocklink.utils.block_model import BlockModel

from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.ins_except import InsCertException
from apps.block.utils.block import BlockDB
from apps.block.utils.correction import block_correction

from apps.block.utils.db_block import (
    get_block_by_bid,
    get_link_target_count_by_bid,
    get_link_main_count_by_bid,
    get_blocks_by_bids,
    get_link_main_bids_filtered,
    get_links_by_main_paginated,
    get_links_by_targets, engine,
)

link_route = RouteBlock(route="/link")


@link_route.cert("/target/count")
async def link_target_count(node_model: NodeModel, ins_cert: InsCert):
    """
    获取目标块数量
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的BID
    bid = ins_cert.data["bid"]

    block_model = get_block_by_bid(bid)
    # 是否BID不存在
    if block_model is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31)

    count = get_link_target_count_by_bid(bid)

    return {"count": count}

@link_route.cert("/target/multiple")
async def link_target_multiple(node_model: NodeModel, ins_cert: InsCert):
    """
    获取link列表
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的BID
    bid = ins_cert.data["bid"]
    page = int(ins_cert.data.get("page", 1))
    limit = int(ins_cert.data.get("limit", 10))

    # 校验BID是否存在
    block_model = get_block_by_bid(bid)
    if block_model is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31)

    # 总数
    total = get_link_target_count_by_bid(bid)

    # 分页数据
    links = get_links_by_main_paginated(bid=bid, page=page, limit=limit)

    # 取出 target 列表
    target_bids = [link.target for link in links]

    # 批量查询对应 BlockDB
    items = []
    if target_bids:
        blocks = get_blocks_by_bids(target_bids)
        bid_to_block = {block.bid: block for block in blocks}
        # 按原 links 顺序返回对应的 block.json_data
        for target_bid in target_bids:
            block = bid_to_block.get(target_bid)
            if block is not None:
                items.append(block.json_data)

    return {"count": total, "page": page, "limit": limit, "items": items}





@link_route.cert("/main/count")
async def link_main_count(node_model: NodeModel, ins_cert: InsCert):
    """
    获取主块数量（指向该BID的主块个数）
    :param node_model:
    :param ins_cert:
    :return:
    """
    bid = ins_cert.data["bid"]
    permission_level = 3

    block_model = get_block_by_bid(bid)
    if block_model is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31)

    count = get_link_main_count_by_bid(bid,  permission_level=permission_level)

    return {"count": count}


@link_route.cert("/main/multiple")
async def link_main_multiple(node_model: NodeModel, ins_cert: InsCert):
    """
    获取外链块列表
    :param node_model:
    :param ins_cert:
    :return:
    """
    bid = ins_cert.data["bid"]
    page = int(ins_cert.data.get("page", 1))
    limit = int(ins_cert.data.get("limit", 10))

    model = ins_cert.data.get("model")

    tag = ins_cert.data.get("tag")

    # 时间排序参数，可选值: "desc"(降序), "asc"(升序), 或 None(不排序)
    order = ins_cert.data.get("order")

    # 校验BID是否存在
    block_model = get_block_by_bid(bid)
    if block_model is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31)
    total, main_bids = get_link_main_bids_filtered(
        target_bid=bid,
        page=page,
        limit=limit,
        model=model,
        tag=tag,
        order=order,
        permission_level=3,
    )

    if total == 0:
        return {"count": 0, "page": page, "limit": limit, "items": []}

    # 批量查询对应 BlockDB
    items = []
    if main_bids:
        blocks = get_blocks_by_bids(main_bids)
        bid_to_block = {block.bid: block for block in blocks}
        for main_bid in main_bids:
            block = bid_to_block.get(main_bid)
            if block is not None:
                items.append(block.json_data)

    return {"count": total, "page": page, "limit": limit, "items": items}


@link_route.cert("/main/multiple_by_targets")
async def link_main_multiple_by_targets(node_model: NodeModel, ins_cert: InsCert):
    """
    批量获取多个 target BID 对应指向它们的主块信息
    :param node_model:
    :param ins_cert:
    :return:
    """
    bids = ins_cert.data.get("bids", [])
    page = int(ins_cert.data.get("page", 1))
    limit = int(ins_cert.data.get("limit", 10))

    # "desc", "asc"
    order = ins_cert.data.get("order")

    links = get_links_by_targets(bids, order=order)

    total = len(links)

    if total == 0:
        return {"count": 0, "page": page, "limit": limit, "items": []}

    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_links = links[start_index:end_index]

    main_bids = [link.main for link in paginated_links]
    blocks = get_blocks_by_bids(main_bids)
    bid_to_block = {block.bid: block for block in blocks}

    items = []

    for link in paginated_links:
        block = bid_to_block.get(link.main)
        if block is None:
            continue

        items.append(
            block.json_data
        )

    return {"count": total, "page": page, "limit": limit, "items": items}