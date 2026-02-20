import json
from typing import Optional

from blocklink.utils.tools import generate_bid
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint


class BlockDB(SQLModel, table=True):
    bid: Optional[str] = Field(default_factory=generate_bid, primary_key=True, nullable=False, max_length=32)
    data: Optional[str] = Field(default=..., nullable=False)  # 用于保存 JSON 数据作为字符串
    model: Optional[str] = Field(default=..., nullable=False, max_length=32, index=True)
    add_time: Optional[str] = Field(default=None, nullable=True, max_length=40, index=True)
    permission_level: Optional[int] = Field(default=None, nullable=True, index=True)
    __tablename__ = "block"

    @property
    def json_data(self):
        if self.data:
            return json.loads(self.data)  # 解析 JSON 字符串
        return {}

    @json_data.setter
    def json_data(self, value):
        value = value or {}
        self.data = json.dumps(value)  # 将字典转换为 JSON 字符串
        self.model = value.get("model")
        self.add_time = value.get("add_time")
        permission = value.get("permission_level")
        try:
            self.permission_level = int(permission) if permission is not None else None
        except (TypeError, ValueError):
            self.permission_level = None


class TagDB(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True, max_length=64)
    bid: str = Field(default=..., nullable=False, index=True, max_length=32)

    __table_args__ = (
        UniqueConstraint("name", "bid", name="uq_tag_name_bid"),
    )


class LinkDB(SQLModel, table=True):
    __tablename__ = "link"

    id: Optional[int] = Field(default=None, primary_key=True)
    main: str = Field(default=..., nullable=False, index=True, max_length=32)  # 主块
    target: str = Field(default=..., nullable=False, index=True, max_length=32)  # 目标块

    __table_args__ = (
        UniqueConstraint("main", "target", name="uq_link_main_target"),
    )
