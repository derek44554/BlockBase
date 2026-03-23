from typing import Iterable, List, Optional, Tuple

from sqlmodel import select
from sqlmodel import SQLModel, create_engine
from sqlmodel import Session
from sqlalchemy import func

from apps.block.utils.block import BlockDB, TagDB, LinkDB

# 链接到数据库
engine = create_engine("sqlite:///data/database/block.db")


def create_db():
    # 创建数据库
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# 获取BID
def get_block_by_bid(bid):
    with Session(engine) as session:
        block_db = session.get(BlockDB, bid)
        if block_db is not None:
            session.expunge(block_db)

    return block_db


# 获取多个 Block
def get_blocks_by_bids(bids):
    with Session(engine) as session:
        statement = select(BlockDB).filter(BlockDB.bid.in_(bids))
        block_dbs = session.exec(statement).all()
        for block in block_dbs or []:
            session.expunge(block)

    if block_dbs is None:
        return None

    return block_dbs


def get_block_count(
        model: Optional[str] = None,
        tag: Optional[str] = None,
        exclude_models: Optional[List[str]] = None,
        permission_level: int = 1,
) -> int:
    with Session(engine) as session:
        count_query = select(func.count()).select_from(BlockDB)
        if tag:
            tag_subquery = select(TagDB.bid).where(TagDB.name == tag)
            count_query = count_query.where(BlockDB.bid.in_(tag_subquery))
        if model:
            count_query = count_query.where(BlockDB.model == model)
        if exclude_models and len(exclude_models) > 0:
            count_query = count_query.where(BlockDB.model.notin_(exclude_models))

        # 权限过滤逻辑
        if permission_level == 1:
            count_query = count_query.where(BlockDB.permission_level == 1)
        elif permission_level == 2:
            count_query = count_query.where(BlockDB.permission_level.in_([1, 2]))
        elif permission_level == 3:
            # permission_level == 3 时不添加过滤条件，获取全部数据
            ...
        else:
            raise ValueError(f"Invalid permission_level: {permission_level}")

        result = session.exec(count_query)
        row = result.first()

    if row is None:
        return 0

    if isinstance(row, (tuple, list)):
        return int((row[0] if row else 0) or 0)

    mapping = getattr(row, "_mapping", None)
    if mapping:
        try:
            first_value = next(iter(mapping.values()))
            return int(first_value or 0)
        except StopIteration:
            return 0

    try:
        return int(row)
    except Exception:
        return 0


# def get_blocks_paginated(
#         page: int,
#         limit: int,
#         order: Optional[str] = "asc",
#         model: Optional[str] = None,
#         tag: Optional[str] = None,
#         exclude_models: Optional[List[str]] = None,
# ):
#     if page is None or page < 1:
#         page = 1
#     if limit is None or limit < 1:
#         limit = 10

#     offset = (page - 1) * limit
#     statement = select(BlockDB)

#     if tag:
#         tag_subquery = select(TagDB.bid).where(TagDB.name == tag)
#         statement = statement.where(BlockDB.bid.in_(tag_subquery))

#     if model:
#         statement = statement.where(BlockDB.model == model)

#     if exclude_models and len(exclude_models) > 0:
#         statement = statement.where(BlockDB.model.notin_(exclude_models))

#     order_normalized = order.lower() if isinstance(order, str) else None
#     add_time_expr = BlockDB.add_time
#     if order_normalized in {"desc", "asc"}:
#         order_by_clause = (
#             add_time_expr.desc().nullslast()
#             if order_normalized == "desc"
#             else add_time_expr.asc().nullsfirst()
#         )
#         statement = statement.order_by(order_by_clause, BlockDB.bid)

#     with Session(engine) as session:
#         statement = statement.offset(offset).limit(limit)
#         blocks = session.exec(statement).all()
#         for block in blocks:
#             session.expunge(block)

#     return blocks

def get_blocks_paginated(
        page: int,
        limit: int,
        order: Optional[str] = "asc",
        model: Optional[str] = None,
        tag: Optional[str] = None,
        exclude_models: Optional[List[str]] = None,
        permission_level: int = 1,
):
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10

    offset = (page - 1) * limit
    statement = select(BlockDB)

    if tag:
        tag_subquery = select(TagDB.bid).where(TagDB.name == tag)
        statement = statement.where(BlockDB.bid.in_(tag_subquery))

    if model:
        statement = statement.where(BlockDB.model == model)

    if exclude_models and len(exclude_models) > 0:
        statement = statement.where(BlockDB.model.notin_(exclude_models))

    # 权限过滤逻辑
    if permission_level == 1:
        statement = statement.where(BlockDB.permission_level == 1)
    elif permission_level == 2:
        statement = statement.where(BlockDB.permission_level.in_([1, 2]))
    elif permission_level == 3:
        # permission_level == 3 时不添加过滤条件，获取全部数据
        ...
    else:
        raise

    order_normalized = order.lower() if isinstance(order, str) else None
    add_time_expr = BlockDB.add_time
    if order_normalized in {"desc", "asc"}:
        order_by_clause = (
            add_time_expr.desc().nullslast()
            if order_normalized == "desc"
            else add_time_expr.asc().nullsfirst()
        )
        statement = statement.order_by(order_by_clause, BlockDB.bid)

    with Session(engine) as session:
        statement = statement.offset(offset).limit(limit)
        blocks = session.exec(statement).all()
        for block in blocks:
            session.expunge(block)

    return blocks


# 获取某个主块的目标数量
def get_link_target_count_by_bid(bid: str) -> int:
    with Session(engine) as session:
        count_query = select(func.count()).select_from(LinkDB).where(LinkDB.main == bid)
        result = session.exec(count_query)
        row = result.first()

    # 结果可能为以下几种：None、int、(count,) 元组、Row 对象
    if row is None:
        return 0

    # 元组 / 列表
    if isinstance(row, (tuple, list)):
        return int((row[0] if row else 0) or 0)

    # SQLAlchemy Row（具备 _mapping）
    mapping = getattr(row, "_mapping", None)
    if mapping:
        try:
            first_value = next(iter(mapping.values()))
            return int(first_value or 0)
        except StopIteration:
            return 0

    # 标量（int）或可转为 int 的类型
    try:
        return int(row)
    except Exception:
        return 0


# 获取某个目标块被多少主块指向（主块数量）
def get_link_main_count_by_bid(bid: str, permission_level: int = 1) -> int:
    with Session(engine) as session:
        count_query = select(func.count()).select_from(LinkDB).where(LinkDB.target == bid)
        
        # 权限过滤逻辑 - 需要 join BlockDB 来过滤主块的权限
        count_query = count_query.join(BlockDB, BlockDB.bid == LinkDB.main)
        if permission_level == 1:
            count_query = count_query.where(BlockDB.permission_level == 1)
        elif permission_level == 2:
            count_query = count_query.where(BlockDB.permission_level.in_([1, 2]))
        elif permission_level == 3:
            # permission_level == 3 时不添加过滤条件，获取全部数据
            ...
        else:
            raise ValueError(f"Invalid permission_level: {permission_level}")
        
        result = session.exec(count_query)
        row = result.first()

    if row is None:
        return 0

    if isinstance(row, (tuple, list)):
        return int((row[0] if row else 0) or 0)

    mapping = getattr(row, "_mapping", None)
    if mapping:
        try:
            first_value = next(iter(mapping.values()))
            return int(first_value or 0)
        except StopIteration:
            return 0

    try:
        return int(row)
    except Exception:
        return 0


# 获取指向 target 的主块 BID（支持筛选）
# def get_link_main_bids_filtered(
#         target_bid: str,
#         page: int,
#         limit: int,
#         model: Optional[str] = None,
#         tag: Optional[str] = None,
# ) -> Tuple[int, List[str]]:
#     if page is None or page < 1:
#         page = 1
#     if limit is None or limit < 1:
#         limit = 10

#     with Session(engine) as session:
#         statement = select(LinkDB.main).where(LinkDB.target == target_bid)

#         if model:
#             statement = statement.join(BlockDB, BlockDB.bid == LinkDB.main)
#             statement = statement.where(BlockDB.model == model)

#         if tag:
#             statement = statement.join(TagDB, TagDB.bid == LinkDB.main)
#             statement = statement.where(TagDB.name == tag)

#         statement = statement.order_by(LinkDB.id)
#         rows = session.exec(statement).all()

#     main_bids = []
#     for row in rows or []:
#         if isinstance(row, (tuple, list)):
#             value = row[0] if row else None
#         else:
#             value = row
#         if value:
#             main_bids.append(value)

#     total = len(main_bids)
#     start = (page - 1) * limit
#     end = start + limit
#     paginated_bids = main_bids[start:end]

#     return total, paginated_bids

def get_link_main_bids_filtered(
        target_bid: str,
        page: int,
        limit: int,
        model: Optional[str] = None,
        tag: Optional[str] = None,
        order: Optional[str] = None,
        permission_level: int = 1,
) -> Tuple[int, List[str]]:
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10
    if permission_level is None:
        permission_level = 1

    with Session(engine) as session:
        statement = select(LinkDB.main).where(LinkDB.target == target_bid)

        statement = statement.join(BlockDB, BlockDB.bid == LinkDB.main)

        if model:
            statement = statement.where(BlockDB.model == model)

        # 权限过滤逻辑
        if permission_level == 1:
            statement = statement.where(BlockDB.permission_level == 1)
        elif permission_level == 2:
            statement = statement.where(BlockDB.permission_level.in_([1, 2]))
        elif permission_level == 3:
            # permission_level == 3 时不添加过滤条件，获取全部数据
            ...
        else:
            raise ValueError(f"Invalid permission_level: {permission_level}")

        if tag:
            statement = statement.join(TagDB, TagDB.bid == LinkDB.main)
            statement = statement.where(TagDB.name == tag)

        # 排序逻辑
        order_normalized = order.lower() if isinstance(order, str) else None
        if order_normalized in {"desc", "asc"}:
            add_time_expr = BlockDB.add_time
            order_by_clause = (
                add_time_expr.desc().nullslast()
                if order_normalized == "desc"
                else add_time_expr.asc().nullsfirst()
            )
            statement = statement.order_by(order_by_clause, LinkDB.id)
        else:
            statement = statement.order_by(LinkDB.id)

        rows = session.exec(statement).all()

    main_bids = []
    for row in rows or []:
        if isinstance(row, (tuple, list)):
            value = row[0] if row else None
        else:
            value = row
        if value:
            main_bids.append(value)

    total = len(main_bids)
    start = (page - 1) * limit
    end = start + limit
    paginated_bids = main_bids[start:end]

    return total, paginated_bids





# 分页获取某个主块指向的链接列表
def get_links_by_main_paginated(bid: str, page: int, limit: int):
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10

    offset = (page - 1) * limit

    with Session(engine) as session:
        statement = (
            select(LinkDB)
            .where(LinkDB.main == bid)
            .order_by(LinkDB.id)
            .offset(offset)
            .limit(limit)
        )
        links = session.exec(statement).all()

    return links


# 分页获取某个目标块被哪些主块指向（按 target == bid）
def get_links_by_target_paginated(bid: str, page: int, limit: int):
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10

    offset = (page - 1) * limit

    with Session(engine) as session:
        statement = (
            select(LinkDB)
            .where(LinkDB.target == bid)
            .order_by(LinkDB.id)
            .offset(offset)
            .limit(limit)
        )
        links = session.exec(statement).all()

    return links


# 批量获取 target 属于 bids 的链接列表
def get_links_by_targets(bids: Iterable[str], order: Optional[str] = None, tag: Optional[str] = None):
    bid_list = [bid for bid in bids if bid]
    if not bid_list:
        return []

    with Session(engine) as session:
        statement = (
            select(LinkDB)
            .where(LinkDB.target.in_(bid_list))
        )
        order_normalized = order.lower() if isinstance(order, str) else None

        if order_normalized in {"desc", "asc"}:
            statement = statement.join(BlockDB, BlockDB.bid == LinkDB.main, isouter=True)

        if tag:
            statement = statement.join(TagDB, TagDB.bid == LinkDB.main).where(TagDB.name == tag)

        if order_normalized in {"desc", "asc"}:
            add_time_expr = BlockDB.add_time
            order_by_clause = (
                add_time_expr.desc().nullslast()
                if order_normalized == "desc"
                else add_time_expr.asc().nullsfirst()
            )
            statement = statement.order_by(order_by_clause, LinkDB.id)

        links = session.exec(statement).all()

    return links


# 获取某个标签的 Block 数量
def get_tag_block_count_by_name(name: str) -> int:
    with Session(engine) as session:
        count_query = select(func.count()).select_from(TagDB).where(TagDB.name == name)
        result = session.exec(count_query)
        row = result.first()

    if row is None:
        return 0

    if isinstance(row, (tuple, list)):
        return int((row[0] if row else 0) or 0)

    mapping = getattr(row, "_mapping", None)
    if mapping:
        try:
            first_value = next(iter(mapping.values()))
            return int(first_value or 0)
        except StopIteration:
            return 0

    try:
        return int(row)
    except Exception:
        return 0


# 分页获取某个标签的 Block 列表
def get_blocks_by_tag_paginated(name: str, page: int, limit: int):
    if page is None or page < 1:
        page = 1
    if limit is None or limit < 1:
        limit = 10

    offset = (page - 1) * limit

    with Session(engine) as session:
        # 先获取该标签下的所有 BID
        tag_statement = (
            select(TagDB.bid)
            .where(TagDB.name == name)
            .order_by(TagDB.id)
            .offset(offset)
            .limit(limit)
        )
        tag_bids = session.exec(tag_statement).all()

        # 如果没有找到标签，返回空列表
        if not tag_bids:
            return []

        # 批量查询对应的 BlockDB
        block_statement = select(BlockDB).filter(BlockDB.bid.in_(tag_bids))
        blocks = session.exec(block_statement).all()

        # 按原 tag_bids 顺序返回对应的 block
        bid_to_block = {block.bid: block for block in blocks}
        ordered_blocks = []
        for bid in tag_bids:
            block = bid_to_block.get(bid)
            if block is not None:
                ordered_blocks.append(block)

    return ordered_blocks


# 获取某个主块的所有链接（用于 correction）
def get_links_by_main(bid: str):
    """获取某个主块的所有链接"""
    with Session(engine) as session:
        statement = select(LinkDB).where(LinkDB.main == bid)
        links = session.exec(statement).all()
    return links


# 获取某个块的所有标签（用于 correction）
def get_tags_by_bid(bid: str):
    """获取某个块的所有标签"""
    with Session(engine) as session:
        statement = select(TagDB).where(TagDB.bid == bid)
        tags = session.exec(statement).all()
    return tags


# 删除链接
def delete_link(link_id: int):
    """删除指定的链接"""
    with Session(engine) as session:
        link = session.get(LinkDB, link_id)
        if link:
            session.delete(link)
            session.commit()


# 删除标签
def delete_tag(tag_id: int):
    """删除指定的标签"""
    with Session(engine) as session:
        tag = session.get(TagDB, tag_id)
        if tag:
            session.delete(tag)
            session.commit()


# 添加链接
def add_link(main: str, target: str):
    """添加新的链接"""
    with Session(engine) as session:
        new_link = LinkDB(main=main, target=target)
        session.add(new_link)
        session.commit()
        return new_link


# 添加标签
def add_tag(name: str, bid: str):
    """添加新的标签"""
    with Session(engine) as session:
        new_tag = TagDB(name=name, bid=bid)
        session.add(new_tag)
        session.commit()
        return new_tag