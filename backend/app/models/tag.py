from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

transaction_tags = Table(
    'transaction_tags',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    transactions = relationship("Transaction", secondary=transaction_tags, back_populates="tags")
