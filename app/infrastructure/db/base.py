from datetime import datetime
from typing import Any, ClassVar, Type

from sqlalchemy import MetaData, text, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict, Field


naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata


class TimestampMixin:
    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
        nullable=False,
    )


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = Field(default=None, read_only=True)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    orm_model: ClassVar[Type[Base]] = None

    def to_orm(self) -> Any:
        if self.orm_model is None:
            raise RuntimeError("Укажите BaseSchema.orm_model в наследнике")

        data = self.model_dump(
            exclude_none=True,
            exclude={"id", "created_at", "updated_at"}
        )

        for key, val in list(data.items()):
            if isinstance(val, BaseSchema):
                data[key] = val.to_orm()
            elif isinstance(val, list):
                data[key] = [
                    item.to_orm() if isinstance(item, BaseSchema) else item
                    for item in val
                ]

        return self.orm_model(**data)
