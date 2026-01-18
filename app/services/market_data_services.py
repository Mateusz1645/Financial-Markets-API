import financedatabase as fd
from fastapi import HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from models import Equity, Forex
import yfinance as yf
from datetime import date, timedelta, datetime
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

def import_all_forex_once(db: Session):

    pairs = [
        ("USD", "PLN"),
        ("EUR", "PLN"),
        ("GBP", "PLN"),
        ("CHF", "PLN"),
        ("JPY", "PLN"),
        ("CAD", "PLN"),
        ("AUD", "PLN"),
        ("NZD", "PLN"),
        ("SEK", "PLN"),
        ("NOK", "PLN"),
        ("DKK", "PLN"),
    ]

    start_date = datetime.now() - timedelta(days=365*10)
    end_date = datetime.now()

    for first, second in pairs:
        symbol = f"{first}{second}=X"
        ticker = yf.Ticker(symbol)

        df = ticker.history(start=start_date, end=end_date, interval="1d")

        if df.empty:
            continue

        objects = []
        for index, row in df.iterrows():
            objects.append(Forex(
                    first_currency=first,
                    second_currency=second,
                    value=float(row["Close"]),
                    date=index.to_pydatetime()))

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

def get_forex_rate(db: Session, first: str, second: str, date: datetime.date):
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)

    rate = (
        db.query(Forex)
        .filter(Forex.first_currency == first.upper())
        .filter(Forex.second_currency == second.upper())
        .filter(Forex.date >= start_of_day)
        .filter(Forex.date < end_of_day)
        .order_by(Forex.date.desc())
        .first()
    )

    if not rate:
        rate = (
            db.query(Forex)
            .filter(Forex.first_currency == first.upper())
            .filter(Forex.second_currency == second.upper())
            .filter(Forex.date < start_of_day)
            .order_by(Forex.date.desc())
            .first()
        )

    if not rate:
        raise ValueError(f"No forex rate for {first}/{second} on {date}")

    return rate.value