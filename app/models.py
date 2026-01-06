from sqlalchemy import Column, Integer, String, Float
from db import Base

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    isin = Column(String, index=True)
    amount = Column(Float)
    transaction_price = Column(Float)