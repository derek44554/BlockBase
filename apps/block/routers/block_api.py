from typing import Optional

from blocklink.utils.ins_except import InsCertException
from fastapi import Query
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from apps.block.utils.db_block import get_block_count, get_blocks_paginated, get_block_by_bid, get_blocks_by_bids

block_fast_api = APIRouter()


@block_fast_api.get("", summary='获取Block列表')
async def get_list(
        model: Optional[str] = Query(None, description="model"),
        tag: Optional[str] = Query(None, description="tag"),
        page: Optional[int] = Query(1, description="page"),
        limit: Optional[int] = Query(10, description="limit"),
        order: Optional[str] = Query(None, description="order"),
        exclude_models: Optional[list] = Query(None, description="exclude models"),
):
    """
    获取Block列表
    """
    permission_level = 1
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


@block_fast_api.get("/multiple", summary='批量获取Block')
async def get_blocks_multiple(
        bids: list[str] = Query(..., description="bids"),
):
    """
    根据 bids 批量获取 Block（仅公开权限）
    """
    if not bids:
        return {"blocks": [], "deny_bids": []}

    blocks = get_blocks_by_bids(bids, permission_level=1)
    bid_to_block = {block.bid: block for block in blocks}

    block_data = []
    deny_bids = []
    for bid in bids:
        block = bid_to_block.get(bid)
        if block is None:
            deny_bids.append(bid)
            continue
        block_data.append(block.json_data)

    return {"blocks": block_data, "deny_bids": deny_bids}


@block_fast_api.get("/{bid}", summary='获取Block')
async def get_block(bid: str):
    """

    """
    block_db = get_block_by_bid(bid)
    # 是否BID不存在
    if block_db is None:
        raise HTTPException(status_code=404, detail="not found")

    if block_db.permission_level != 1:
        raise HTTPException(status_code=403, detail="forbidden")

    return block_db.json_data
