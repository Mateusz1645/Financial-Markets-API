import financedatabase as fd
from fastapi import HTTPException
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from models import Equity
import yfinance as yf
from datetime import date, timedelta
from utils.date_utils import parse_date

def import_all_equities_once(db: Session):
    if db.query(Equity).first():
        return

    equities = fd.Equities()
    df = equities.select()

    objects = []

    for symbol, row in df.iterrows():
        objects.append(
            Equity(
                symbol=symbol,
                isin=row.get("isin"),
                name=row.get("name"),
                currency=row.get("currency"),
                sector=row.get("sector"),
                industry=row.get("industry"),
                exchange=row.get("exchange"),
                market=row.get("market"),
                country=row.get("country"),
                market_cap=row.get("market_cap"),
            )
        )

    db.bulk_save_objects(objects)
    db.commit()

def get_current_price_from_yfinance(symbol: str, target_date: Optional[date] = "today") -> float:
    
    ticker = yf.Ticker(symbol)
    
    if target_date == "today":
        data = ticker.history(period="1d")
    else:
        target_date = parse_date(target_date)
        data = target_date + timedelta(days=1)
        data = ticker.history(start=target_date, end=target_date + timedelta(days=1))
    if data.empty:
        raise HTTPException(status_code=404, detail=f"No data for symbol: {symbol}")

    row = data.iloc[-1]
    price = float(row["Close"])
    currency = ticker.fast_info.get("currency")
    return {
        "symbol": symbol,
        "date": row.name.date().isoformat(),
        "price": price,
        "currency": currency
    }