from typing import Optional

from blocklink.utils.ins_except import InsCertException
from fastapi import Query
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from apps.block.utils.db_block import (
    get_block_by_bid,
    get_link_main_bids_filtered,
    get_blocks_by_bids,
)

link_fast_api = APIRouter()


@link_fast_api.get("", summary='获取外链块列表')
async def link_main_multiple(
        bid: Optional[str] = Query(..., description="bid"),
        model: Optional[str] = Query(None, description="model"),
        tag: Optional[str] = Query(None, description="tag"),
        page: Optional[int] = Query(1, description="page"),
        limit: Optional[int] = Query(10, description="limit"),
        order: Optional[str] = Query(None, description="order"),
):
    """
    获取外链块列表
    """
    permission_level = 1

    # 校验BID是否存在
    block_model = get_block_by_bid(bid)
    if block_model is None:
        raise HTTPException(status_code=404, detail="Block not found")

    # 权限检查
    if block_model.permission_level != 1:
        raise HTTPException(status_code=403, detail="Forbidden")

    total, main_bids = get_link_main_bids_filtered(
        target_bid=bid,
        page=page,
        limit=limit,
        model=model,
        tag=tag,
        order=order,
        permission_level=permission_level,
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