from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import Reference_Rate
from utils.date_utils import parse_date
import math

router = APIRouter(prefix="/reference_rate", tags=["Reference_Rate"])


@router.get("/list")
def list_reference_rate(db: Session = Depends(get_db)):
    """
    List all reference rate records in the database.
    """
    records = db.query(Reference_Rate).order_by(Reference_Rate.date).all()
    result = []
    for r in records:
        if r.value is None or math.isnan(r.value) or math.isinf(r.value):
            continue
        result.append(
            {"id": r.id, "date": r.date.strftime("%Y-%m-%d"), "value": r.value}
        )
    return result


@router.post("/add")
def add_reference_rate(
    date: str, value: Optional[float] = None, db: Session = Depends(get_db)
):
    """
    Add a single reference rate for input month, year and optional value.
    """
    try:
        date = parse_date(date)
    except HTTPException:
        raise HTTPException(status_code=400, detail=f"Wrong data input {date}")

    reference_rate = (
        db.query(Reference_Rate)
        .filter(
            Reference_Rate.date == date,
            Reference_Rate.value.isnot(None),
        )
        .first()
    )

    if reference_rate:
        raise HTTPException(
            status_code=400,
            detail=f"Reference Rate for date: {reference_rate.date} already exists: {reference_rate.value}",
        )
    if value >= 1:
        value = round(float(value / 100), 4)

    reference_rate = Reference_Rate(date=date, value=value)

    db.add(reference_rate)
    db.commit()
    db.refresh(reference_rate)

    return {
        "message": "Reference Rate added successfully",
        "date": date.strftime("%Y-%m-%d"),
        "value": value,
    }


@router.delete("/delete")
def delete_reference_rate(reference_rate_id: int, db: Session = Depends(get_db)):
    """
    Delete a single reference rate from database manually.
    """
    reference_rate = (
        db.query(Reference_Rate).filter(Reference_Rate.id == reference_rate_id).first()
    )
    if not reference_rate:
        raise HTTPException(status_code=404, detail="Reference_Rate not found")

    db.delete(reference_rate)
    db.commit()
    return {
        "status": "success",
        "message": f"Reference rate with id {reference_rate.id} deleted, date: {reference_rate.date}, value: {reference_rate.value}",
    }
