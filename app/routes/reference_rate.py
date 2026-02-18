from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import Reference_Rate
import math

router = APIRouter(prefix="/reference_rate", tags=['Reference_Rate'])

@router.get("/list")
def list_reference_rate(db: Session = Depends(get_db)):
    """
    List all reference rate records in the database.
    """
    records = db.query(Reference_Rate).order_by(Reference_Rate.year, Reference_Rate.month).all()
    result = []
    for r in records:
        if r.value is None or math.isnan(r.value) or math.isinf(r.value):
            continue
        result.append({
            "id": r.id,
            "year": r.year,
            "month": r.month,
            "value": r.value
        })
    return result

@router.post("/add")
def add_reference_rate(month: int, year: int, value: Optional[float] = None, db: Session = Depends(get_db)):
    """
    Add a single reference rate for input month, year and optional value.
    """
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Month must be beetwen 1 and 12")
    
    reference_rate = db.query(Reference_Rate).filter(
        Reference_Rate.month == month,
        Reference_Rate.year == year,
        Reference_Rate.value.isnot(None)
    ).first()

    if reference_rate:
        raise HTTPException(status_code=400, detail=f"Reference Rate for month {month}, year {year} already exists: {reference_rate.value}")
    if value >= 1:
        value = round(float(value / 100), 4)
        
    reference_rate = Reference_Rate(
        month=month,
        year=year,
        value=value
    )

    db.add(reference_rate)
    db.commit()
    db.refresh(reference_rate)

    return {
        "message": "Reference Rate added successfully",
        "month": month,
        "year": year,
        "value": value
    }

@router.delete("/delete")
def delete_reference_rate(reference_rate_id: int, db: Session = Depends(get_db)):
    """
    Delete a single reference rate from database manually.
    """
    reference_rate = db.query(Reference_Rate).filter(Reference_Rate.id == reference_rate_id).first()
    if not reference_rate:
        raise HTTPException(status_code=404, detail="Reference_Rate not found")
    
    db.delete(reference_rate)
    db.commit()
    return {"status": "success", "message": f"Inflation with id {reference_rate.id} deleted year: {reference_rate.year}, month: {reference_rate.month}, value: {reference_rate.value}"}