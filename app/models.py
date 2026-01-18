from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from db import Base

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    isin = Column(String, index=True)
    name = Column(String)
    date = Column(DateTime)
    amount = Column(Float)
    transaction_price = Column(Float)
    currency = Column(String)
    currency_transaction = Column(String)
    type_ = Column(String)
    coupon_rate = Column(Float)
    inflation_first_year = Column(Float)

class Inflation(Base):
    __tablename__ = "inflation"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    value = Column(Float)

class Equity(Base):
    __tablename__ = "equities"

    id = Column(Integer, primary_key=True, index=True)
    # identifiers
    symbol = Column(String, unique=True, index=True, nullable=False)
    isin = Column(String, index=True)
    cusip = Column(String, index=True)
    figi = Column(String, index=True)
    composite_figi = Column(String)
    shareclass_figi = Column(String)
    # basic info
    name = Column(String, nullable=False)
    summary = Column(Text)
    currency = Column(String)
    # classification
    sector = Column(String, index=True)
    industry_group = Column(String)
    industry = Column(String)
    # market info
    exchange = Column(String, index=True)
    market = Column(String)
    market_cap = Column(String)
    # location
    country = Column(String, index=True)
    state = Column(String)
    city = Column(String)
    zipcode = Column(String)
    # web
    website = Column(String)

class Forex(Base):
    __tablename__ = "forex"
    id = Column(Integer, primary_key=True, index=True)
    first_currency = Column(String, index=True)
    second_currency = Column(String, index=True)
    value = Column(Float, index=True)
    date = Column(DateTime, index=True)