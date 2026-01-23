from sqlalchemy import Column, ForeignKey, Integer, String, Date
from db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(Date)

    entries = relationship("MoneyEntry", back_populates="user")
    
class MoneyEntry(Base):
    __tablename__ = "money_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="entries")