from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db import get_db
from models import Asset
from datetime import datetime, timedelta
from typing import Optional
from services.bond_pricing_service import calculate_value_of_bond
from utils.date_utils import parse_date
from utils.bond_utils import validate_bond_fields
import pandas as pd

router = APIRouter(
    prefix="/assets",
    tags=["Portfolio"]
)

@router.post("/upload")
def upload_portfolio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a portfolio file (Excel or CSV) to the database.
    Transactions on the same day with the same attributes (ISIN, currency, type, coupon_rate) 
    are merged into a single record to save space.
    """
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use Excel or CSV.")
    try:
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")
    
    for _, row in df.iterrows():
        isin = row["ISIN"].upper()
        name = row["NAME"]
        amount = row["QUANTITY"]
        date = row["DATE"]
        transaction_price = row["TRANSACTION PRICE"]
        currency = row.get("CURRENCY", None)
        type_ = row.get("TYPE", None)
        coupon_rate = row.get("COUPON RATE (%)", None)
        inflation_first_year = row.get("INFLATION_FIRST_YEAR", None)

        coupon_rate, inflation_first_year = validate_bond_fields(
            type_=type_,
            isin=isin,
            coupon_rate=coupon_rate,
            inflation_first_year=inflation_first_year
        )

        transaction_date = parse_date(date)
        start_of_day = datetime(transaction_date.year, transaction_date.month, transaction_date.day)
        end_of_day = start_of_day + timedelta(days=1)
        coupon_rate = (round(coupon_rate / 100, 4) if coupon_rate and coupon_rate >= 1 else coupon_rate) if coupon_rate is not None else None
        inflation_first_year = (round(inflation_first_year / 100, 4) if inflation_first_year and inflation_first_year >= 1 else inflation_first_year) if inflation_first_year is not None else None
        type_ = type_.upper()

        asset = db.query(Asset).filter(
            Asset.isin == isin.upper(),
            Asset.name == name,
            Asset.currency == currency,
            Asset.type_ == type_,
            Asset.coupon_rate == coupon_rate,
            Asset.inflation_first_year == inflation_first_year,
            Asset.date >= start_of_day,
            Asset.date < end_of_day
        ).first()

        if asset:
            asset.amount += amount
            asset.transaction_price += transaction_price
        else:
            asset = Asset(
                isin=isin.upper(),
                name=name,
                date=transaction_date,
                amount=amount,
                transaction_price=transaction_price,
                currency=currency,
                type_=type_,
                coupon_rate=coupon_rate,
                inflation_first_year=inflation_first_year)
            db.add(asset)
    db.commit()
    return {"status": "success", "message": f"{len(df)} assets uploaded"}


@router.post("/add")
def add_asset(isin: str, name: str, amount: float, date: str, transaction_price: float, currency: str, type_: str, coupon_rate: Optional[float] = None, inflation_first_year: Optional[float] = None, db: Session = Depends(get_db)):
    """
    Add a single asset to the database manually.
    """
    try:
        transaction_date = parse_date(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in format DD.MM.YYYY HH:MM")
    
    coupon_rate, inflation_first_year = validate_bond_fields(
            type_=type_,
            isin=isin,
            coupon_rate=coupon_rate,
            inflation_first_year=inflation_first_year
        )

    start_of_day = datetime(transaction_date.year, transaction_date.month, transaction_date.day)
    end_of_day = start_of_day + timedelta(days=1)
    coupon_rate = (round(coupon_rate / 100, 4) if coupon_rate and coupon_rate >= 1 else coupon_rate) if coupon_rate is not None else None
    inflation_first_year = (round(inflation_first_year / 100, 4) if inflation_first_year and inflation_first_year >= 1 else inflation_first_year) if inflation_first_year is not None else None
    type_ = type_.upper()

    asset = db.query(Asset).filter(
        Asset.isin == isin.upper(),
        Asset.name == name,
        Asset.type_ == type_,
        Asset.currency == currency,
        Asset.coupon_rate == coupon_rate,
        Asset.inflation_first_year == inflation_first_year,
        Asset.date >= start_of_day,
        Asset.date < end_of_day
    ).first()

    if asset:
        asset.amount += amount
        asset.transaction_price += transaction_price
    else:
        asset = Asset(
            isin=isin.upper(),
            name=name,
            amount=amount,
            date=transaction_date,
            transaction_price=transaction_price,
            currency=currency,
            type_=type_,
            coupon_rate=coupon_rate,
            inflation_first_year=inflation_first_year
        )
        db.add(asset)

    db.commit()
    return {"status": "success", "message": "Asset added or updated"}

@router.delete("/detele")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Delete a single asset from database manually.
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    return {"status": "success", "message": f"Asset with id {asset_id} deleted"}

@router.get("/list")
def list_assets(db: Session = Depends(get_db)):
    """
    List all assets in the database.
    """
    assets = db.query(Asset).limit(300).all()
    result = []
    for a in assets:
        result.append({
            "id": a.id,
            "symbol": a.isin,
            "name": a.name,
            "date": a.date.isoformat() if a.date else None,
            "amount": float(a.amount) if a.amount is not None and pd.notna(a.amount) else 0,
            "transaction_price": float(a.transaction_price) if a.transaction_price is not None and pd.notna(a.transaction_price) else 0,
            "currency": a.currency,
            "type": a.type_,
            "coupon_rate": float(a.coupon_rate)if a.coupon_rate is not None and pd.notna(a.coupon_rate) else None,
            "inflation_first_year": float(a.inflation_first_year) if a.inflation_first_year is not None and pd.notna(a.inflation_first_year) else None
        })
    
    return result

@router.get("/choices")
def assets_choices(db: Session = Depends(get_db)):
    """
    List available assets (ISIN + NAME) for selection.
    """
    results = db.query(Asset.isin, Asset.name).distinct(Asset.isin).all()
    return [{"isin": isin, "name": name} for isin, name in results]

@router.post("/calc_current_value")
def calculate_asset_value(id: Optional[int] = None, isin: Optional[str] = None, date: Optional[str] = None, date_to_calculate: Optional[str] = "today", db: Session = Depends(get_db)):
    """
    Calculate value of selected asset for date=date_to_calculate if not entered date=today.

    Possible search by:
    - `id`
    - `isin` and `date`
    """

    if id:
        asset = db.query(Asset).filter(Asset.id == id).first()
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with id {id} not found")
    elif isin and date:
        try:
            date_obj = parse_date(date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Date format should be YYYY-MM-DD")
        
        start_of_day = datetime.combine(date_obj, datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)

        asset = db.query(Asset).filter(
            Asset.isin == isin.upper(),
            Asset.date >= start_of_day,
            Asset.date < end_of_day
        ).first()

        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {isin} not found for given date {date}")
    else:
        raise HTTPException(
            status_code=400, 
            detail="Provide either `id` or both `isin` and `date`"
        )

    try:
        if asset.type_.upper() == "BOND":
            value = calculate_value_of_bond(asset=asset, db=db, date=date_to_calculate)
        else:
            value = asset.transaction_price or 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating value for {asset.isin}: {str(e)}")

    return [{
        "id": asset.id,
        "isin": asset.isin,
        "name": asset.name,
        "date": asset.date,
        "amount": asset.amount,
        "value_before": asset.transaction_price,
        "value_now": value
    }]