from sqlalchemy import Column, Integer, String, Float, DateTime
from db import Base

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    isin = Column(String, index=True)
    date = Column(DateTime)
    amount = Column(Float)
    transaction_price = Column(Float)
    currency = Column(String)
    type_ = Column(String)
    coupon_rate = Column(Float)