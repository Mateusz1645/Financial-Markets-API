from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db import get_db
from models import Asset
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

router = APIRouter()

@router.post("/assets/upload")
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
        amount = row["QUANTITY"]
        date = row["DATE"]
        transaction_price = row["TRANSACTION PRICE"]
        currency = row.get("CURRENCY", None)
        type_ = row.get("TYPE", None)
        coupon_rate = row.get("COUPON RATE (%)", None)

        # If bond must have coupon_rate input
        if type_.upper() == "BOND" and coupon_rate is None:
            raise HTTPException(status_code=400, detail=f"coupon_rate is required for BOND type \n check input file {file.filename}")
        if type_.upper() != "BOND":
            coupon_rate = None

        transaction_date = datetime.strptime(date, "%d.%m.%Y %H:%M")
        start_of_day = datetime(transaction_date.year, transaction_date.month, transaction_date.day)
        end_of_day = start_of_day + timedelta(days=1)

        asset = db.query(Asset).filter(
            Asset.isin == isin.upper(),
            Asset.currency == currency,
            Asset.type_ == type_,
            Asset.coupon_rate == coupon_rate,
            Asset.date >= start_of_day,
            Asset.date < end_of_day
        ).first()

        if asset:
            asset.amount += amount
            asset.transaction_price += transaction_price
        else:
            asset = Asset(
                isin=isin.upper(),
                date=transaction_date,
                amount=amount,
                transaction_price=transaction_price,
                currency=currency,
                type_=type_,
                coupon_rate=coupon_rate)
            db.add(asset)
    db.commit()
    return {"status": "success", "message": f"{len(df)} assets uploaded"}


@router.post("/assets/add")
def add_asset(isin: str, amount: float, date: str, transaction_price: float, currency: str, type_: str, coupon_rate: Optional[float] = None, db: Session = Depends(get_db)):
    """
    Add a single asset to the database manually.
    """
    try:
        transaction_date = datetime.strptime(date, "%d.%m.%Y %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in format DD.MM.YYYY HH:MM")
    # If bond must have coupon_rate input
    if type_.upper() == "BOND" and coupon_rate is None:
        raise HTTPException(status_code=400, detail="coupon_rate is required for BOND type")
    if type_.upper() != "BOND":
        coupon_rate = None

    start_of_day = datetime(transaction_date.year, transaction_date.month, transaction_date.day)
    end_of_day = start_of_day + timedelta(days=1)


    asset = db.query(Asset).filter(
        Asset.isin == isin.upper(),
        Asset.type_ == type_,
        Asset.currency == currency,
        Asset.coupon_rate == coupon_rate,
        Asset.date >= start_of_day,
        Asset.date < end_of_day
    ).first()

    if asset:
        asset.amount += amount
        asset.transaction_price += transaction_price
    else:
        asset = Asset(
            isin=isin.upper(),
            amount=amount,
            date=transaction_date,
            transaction_price=transaction_price,
            currency=currency,
            type_=type_,
            coupon_rate=coupon_rate
        )
        db.add(asset)

    db.commit()
    return {"status": "success", "message": "Asset added or updated"}

@router.get("/assets/")
def list_assets(db: Session = Depends(get_db)):
    """
    List all assets in the database.
    """
    assets = db.query(Asset).all()
    result = []
    for a in assets:
        result.append({
            "symbol": a.isin,
            "date": a.date.isoformat() if a.date else None,
            "amount": float(a.amount) if a.amount is not None and pd.notna(a.amount) else 0,
            "transaction_price": float(a.transaction_price) if a.transaction_price is not None and pd.notna(a.transaction_price) else 0,
            "currency": a.currency,
            "type": a.type_,
            "coupon_rate": float(a.coupon_rate) if a.coupon_rate is not None and pd.notna(a.coupon_rate) else None
        })
    
    return result