from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Inflation
import math

router = APIRouter(prefix="/inflation", tags=["Inflation"])

@router.get("/list")
def list_inflation(db: Session = Depends(get_db)):
    """
    List all inflation records in the database.
    """
    records = db.query(Inflation).order_by(Inflation.year, Inflation.month).all()
    result = []
    for r in records:
        if r.value is None or math.isnan(r.value) or math.isinf(r.value):
            continue
        result.append({
            "year": r.year,
            "month": r.month,
            "value": r.value
        })
    return result
