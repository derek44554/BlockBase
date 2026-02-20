from blocklink.utils.block_model import BlockModel
from apps.block.utils.db_block import (
    get_links_by_main,
    get_tags_by_bid,
    delete_link,
    delete_tag,
    add_link,
    add_tag
)


"""
修正Block的关系
tag link
"""

def block_correction(block_model: BlockModel):
    """
    修正Block的关系数据
    将数据库中的LinkDB和TagDB与block_model中的标准数据进行同步
    
    当Block中的link或tag减少时，会自动删除数据库中多余的关系记录
    当Block中的link或tag增加时，会自动添加缺失的关系记录
    
    :param block_model: Block模型，包含最新的标准数据
    """
    bid = block_model["bid"]
    
    if not bid:
        raise ValueError("Block BID cannot be empty")
    
    link = block_model["link"]  # 最新的标准链接数据
    tag = block_model["tag"]    # 最新的标准标签数据
    
    # 修正链接关系
    _correct_links(bid, link)

    # 修正标签关系
    _correct_tags(bid, tag)


def _correct_links(bid: str, standard_links: list):
    """
    修正链接关系
    将数据库中的LinkDB与标准链接数据进行同步
    
    - 删除数据库中存在但标准数据中不存在的链接（处理link减少的情况）
    - 添加标准数据中存在但数据库中不存在的链接（处理link增加的情况）
    
    :param bid: 主块的BID
    :param standard_links: 标准链接数据列表（target BID列表）
    """
    # 处理空值情况
    if standard_links is None:
        standard_links = []
    
    # 获取数据库中该主块的所有链接
    db_links = get_links_by_main(bid)
    
    # 将标准链接转换为集合，便于比较（过滤空值）
    standard_targets = {target for target in standard_links if target}
    
    # 将数据库链接转换为集合
    db_targets = {link.target for link in db_links}
    
    # 找出需要删除的链接（数据库中有但标准数据中没有）
    links_to_delete = db_targets - standard_targets
    
    # 找出需要添加的链接（标准数据中有但数据库中没有）
    links_to_add = standard_targets - db_targets
    
    # 删除多余的链接
    for target in links_to_delete:
        for link in db_links:
            if link.target == target:
                delete_link(link.id)
                break
    
    # 添加缺少的链接
    for target in links_to_add:
        add_link(main=bid, target=target)


def _correct_tags(bid: str, standard_tags: list):
    """
    修正标签关系
    将数据库中的TagDB与标准标签数据进行同步
    
    - 删除数据库中存在但标准数据中不存在的标签（处理tag减少的情况）
    - 添加标准数据中存在但数据库中不存在的标签（处理tag增加的情况）
    
    :param bid: 块的BID
    :param standard_tags: 标准标签数据列表（标签名称列表）
    """
    # 处理空值情况
    if standard_tags is None:
        standard_tags = []
    
    # 获取数据库中该块的所有标签
    db_tags = get_tags_by_bid(bid)
    
    # 将标准标签转换为集合，便于比较（过滤空值）
    standard_tag_names = {tag for tag in standard_tags if tag}
    
    # 将数据库标签转换为集合
    db_tag_names = {tag.name for tag in db_tags}
    
    # 找出需要删除的标签（数据库中有但标准数据中没有）
    tags_to_delete = db_tag_names - standard_tag_names
    
    # 找出需要添加的标签（标准数据中有但数据库中没有）
    tags_to_add = standard_tag_names - db_tag_names
    
    # 删除多余的标签
    for tag_name in tags_to_delete:
        for tag in db_tags:
            if tag.name == tag_name:
                delete_tag(tag.id)
                break
    
    # 添加缺少的标签
    for tag_name in tags_to_add:
        add_tag(name=tag_name, bid=bid)