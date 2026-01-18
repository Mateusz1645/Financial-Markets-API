from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import Equity
router = APIRouter(prefix="/equities", tags=["Equities"])

@router.get("/list")
def list_equities(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    """
    List equities with limit and offset.
    """
    records = (db.query(Equity).order_by(Equity.symbol).offset(offset).limit(limit).all())

    return [{
            "symbol": r.symbol,
            "isin": r.isin,
            "name": r.name,
            "currency": r.currency,
            "sector": r.sector,
            "industry": r.industry,
            "exchange": r.exchange,
            "market": r.market,
            "country": r.country,
            "market_cap": r.market_cap
        } for r in records]

@router.post("/add")
def add_equity(symbol: str, name: str, isin: Optional[str] = None, cusip: Optional[str] = None, figi: Optional[str] = None, composite_figi: Optional[str] = None, shareclass_figi: Optional[str] = None, summary: Optional[str] = None, currency: Optional[str] = None, sector: Optional[str] = None, industry_group: Optional[str] = None, industry: Optional[str] = None, exchange: Optional[str] = None, market: Optional[str] = None, market_cap: Optional[str] = None, country: Optional[str] = None, state: Optional[str] = None, city: Optional[str] = None, zipcode: Optional[str] = None, website: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Add equity to database.
    symbol and isin must be unique.
    """

    symbol = symbol.upper().strip()
    isin = isin.upper().strip() if isin else None

    if db.query(Equity).filter(Equity.symbol == symbol).first():
        raise HTTPException(status_code=400, detail=f"Equity with symbol '{symbol}' already exists")

    if isin and db.query(Equity).filter(Equity.isin == isin).first():
        raise HTTPException(status_code=400, detail=f"Equity with ISIN '{isin}' already exists")

    equity = Equity(
        symbol=symbol,
        name=name,
        isin=isin,
        cusip=cusip,
        figi=figi,
        composite_figi=composite_figi,
        shareclass_figi=shareclass_figi,
        summary=summary,
        currency=currency,
        sector=sector,
        industry_group=industry_group,
        industry=industry,
        exchange=exchange,
        market=market,
        market_cap=market_cap,
        country=country,
        state=state,
        city=city,
        zipcode=zipcode,
        website=website,
    )

    db.add(equity)
    db.commit()
    db.refresh(equity)

    return {"status": "success", "id": equity.id, "symbol": equity.symbol, "isin": equity.isin}

@router.delete("/delete")
def delete_equity(symbol: Optional[str] = None, isin: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Delete equity by symbol or ISIN.
    """

    if not symbol and not isin:
        raise HTTPException(status_code=400, detail="Provide symbol or isin")

    query = db.query(Equity)

    if symbol:
        query = query.filter(Equity.symbol == symbol.upper().strip())
    if isin:
        query = query.filter(Equity.isin == isin.upper().strip())

    equity = query.first()

    if not equity:
        raise HTTPException(status_code=404, detail="Equity not found")

    db.delete(equity)
    db.commit()

    return {
        "status": "success",
        "message": "Equity deleted",
        "symbol": equity.symbol,
        "isin": equity.isin
    }

@router.get("/get_symbol")
def get_symbol_from_isin(isin: str, db: Session = Depends(get_db)):
    """
    Return symbol for isin in db equities.
    """
    if isin is None:
        raise HTTPException(status_code=400, detail="Need isin input")

    records = db.query(Equity).filter_by(isin=isin).all()

    if not records:
        raise HTTPException(status_code=400, detail=f"No data in db equities for isin: {isin}")

    return [r.symbol for r in records]