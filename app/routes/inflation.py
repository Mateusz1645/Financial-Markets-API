from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import Inflation
from services.inflation_service import get_inflation_for_month
import time
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
            "id": r.id,
            "year": r.year,
            "month": r.month,
            "value": r.value
        })
    return result


@router.post("/add")
def add_inflation(month: int, year: int, value: Optional[float] = None, db: Session = Depends(get_db)):
    """
    Add a single inflation for input month, year and optional value.
    If a value is not entered, an attempt will be made to retrieve the value from the GUS API. If this fails after 5 attempts, an error will be displayed.
    """
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Month must be beetwen 1 and 12")
    
    inflation = db.query(Inflation).filter(
        Inflation.month == month,
        Inflation.year == year,
        Inflation.value.isnot(None)
    ).first()

    if inflation:
        raise HTTPException(status_code=400, detail=f"Inflation for month {month}, year {year} already exists: {inflation.value}")
    if value is None:
        max_retries = 5
        last_exception = None

        for _ in range(max_retries):
            try:
                value = get_inflation_for_month(month=month, year=year)
                break
            except Exception as e:
                last_exception = e
                time.sleep(1)
        else:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch inflation after {max_retries} attempts: {last_exception}"
            )
        
    if value >= 1:
        value = round(float(value / 100), 4)

    inflation = Inflation(
        month=month,
        year=year,
        value=value
    )

    db.add(inflation)
    db.commit()
    db.refresh(inflation)

    return {
        "message": "Inflation added successfully",
        "month": month,
        "year": year,
        "value": value
    }

@router.delete("/delete")
def delete_inflation(inflation_id: int, db: Session = Depends(get_db)):
    """
    Delete a single inflation from database manually.
    """
    inflation = db.query(Inflation).filter(Inflation.id == inflation_id).first()
    if not inflation:
        raise HTTPException(status_code=404, detail="Inflation not found")
    
    db.delete(inflation)
    db.commit()
    return {"status": "success", "message": f"Inflation with id {inflation_id} deleted year: {inflation.year}, month: {inflation.month}, value: {inflation.value}"}