from sqlalchemy import NUMERIC, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

transaction_tags = Table(
    'transaction_tags',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(NUMERIC(10, 2), nullable=False)  # type: ignore[var-annotated]
    type = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    category_rel = relationship("Category", back_populates="transactions")
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, index=True)
    tags = relationship("Tag", secondary=transaction_tags, back_populates="transactions")
