from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.transaction import transaction_tags


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    transactions = relationship("Transaction", secondary=transaction_tags, back_populates="tags")
