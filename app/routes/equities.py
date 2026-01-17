from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Equity

router = APIRouter(prefix="/equities", tags=["Equities"])

@router.get("/list")
def list_equities(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List equities with limit and offset.
    """
    records = (
        db.query(Equity)
        .order_by(Equity.symbol)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
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
        }
        for r in records
    ]