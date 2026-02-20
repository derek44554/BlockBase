from blocklink.models.ins.ins_cert import InsCert
from blocklink.models.node.node import NodeModel
from blocklink.models.routers.route_block import RouteBlock
from blocklink.utils.block_model import BlockModel
from blocklink.utils.ins_except import InsCertException
from blocklink.utils.node_meta import NodeMeta

from sqlmodel import Session

from apps.block.utils.block import BlockDB
from apps.block.utils.correction import block_correction
from apps.block.utils.db_block import get_block_by_bid, get_blocks_by_bids, engine

write_route = RouteBlock(route="/write")


@write_route.cert("/simple")
async def simple(node_model: NodeModel, ins_cert: InsCert):
    """
    简易写入
    如果不存在bid则创建
    :param node_model:
    :param ins_cert:
    :return:
    """
    # 要获取的BID
    bid = ins_cert.data.get("bid")
    model = ins_cert.data.get("model")
    print(ins_cert.data)

    # 是否 BID错误
    if bid is None or len(bid) != 32:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32,
                               content="Incorrect BID")

    # 是否 BID 不符合本节点
    if NodeMeta()["bid"][:10] != bid[:10]:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32,
                               content="Incorrect BID")

    # 是否 model错误
    if model is None or len(model) != 32:
        raise InsCertException(node=node_model, ins_cert=ins_cert, status_code=32,
                               content="Incorrect model")

    block_db = get_block_by_bid(bid)

    # 存在
    if block_db:
        block_db.json_data = ins_cert.data

    else:
        block_db = BlockDB()
        block_db.bid = bid
        block_db.json_data = ins_cert.data

    with Session(engine) as session:
        session.add(block_db)
        session.commit()
        session.refresh(block_db)

    # --------------
    block_model = BlockModel(data=block_db.json_data)
    block_correction(block_model=block_model)

    return {}

