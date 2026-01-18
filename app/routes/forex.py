from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Forex
from datetime import timedelta
import math
from utils.date_utils import parse_date

router = APIRouter(prefix="/forex", tags=["Forex"])

@router.get("/list")
def list_forex(first_currency: str, second_currency: str, start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    """
    List all forex records in the database for the given currency pair.
    Optional: start_date, end_date
    """

    query = (
        db.query(Forex)
        .filter(Forex.first_currency == first_currency.upper())
        .filter(Forex.second_currency == second_currency.upper())
    )

    if start_date:
        start = parse_date(start_date)
        query = query.filter(Forex.date >= start)

    if end_date:
        end = parse_date(end_date) + timedelta(days=1)
        query = query.filter(Forex.date < end)

    records = query.order_by(Forex.date).all()

    if not records:
        raise HTTPException(status_code=404, detail="No records for this currency pair")

    result = []
    for r in records:
        if r.value is None or math.isnan(r.value) or math.isinf(r.value):
            continue
        result.append({
            "date": r.date.date().isoformat(),
            "value": r.value
        })
    return result