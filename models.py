from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    level = Column(String)
    cashback = Column(Float)
    spend = Column(Float, default=0.0)  # Параметр потраченных денег
