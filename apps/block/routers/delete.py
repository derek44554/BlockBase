from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.block_model import BlockModel
from blocklink.utils.ins_except import InsCertException
from blocklink.utils.node_meta import NodeMeta

from sqlmodel import Session, select

from apps.block.utils.block import BlockDB, LinkDB, TagDB
from apps.block.utils.correction import block_correction
from apps.block.utils.db_block import get_block_by_bid, get_blocks_by_bids, engine

delete_route = RouteBlock(route="/delete")

@delete_route.cert("/simple")
async def simple(node_model: NodeModel, ins_cert: InsCert):
    """
    删除Block及其所有关联关系
    删除Block本身、所有相关的Link（作为main或target）、所有相关的Tag
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 获取要删除的BID
    bid = ins_cert.data.get("bid")
    
    # 验证BID
    if bid is None or len(bid) != 32:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32,
                               content="Incorrect BID")
    
    # 检查Block是否存在
    block_db = get_block_by_bid(bid)
    if block_db is None:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=31,
                               content="Block not found")
    
    with Session(engine) as session:
        # 1. 删除所有相关的Link（该Block作为main的链接）
        statement = select(LinkDB).where(LinkDB.main == bid)
        links_as_main = session.exec(statement).all()
        for link in links_as_main:
            session.delete(link)
        
        # 2. 删除所有相关的Link（该Block作为target的链接）
        statement = select(LinkDB).where(LinkDB.target == bid)
        links_as_target = session.exec(statement).all()
        for link in links_as_target:
            session.delete(link)
        
        # 3. 删除所有相关的Tag
        statement = select(TagDB).where(TagDB.bid == bid)
        tags = session.exec(statement).all()
        for tag in tags:
            session.delete(tag)
        
        # 4. 删除Block本身
        block = session.get(BlockDB, bid)
        if block:
            session.delete(block)
        
        session.commit()
    
    return {}