from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from db import get_db
from models import Asset
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()

@router.post("/upload-portfolio")
def upload_portfolio(file: UploadFile = File(...), db: Session = Depends(get_db)):
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

        transaction_date = pd.to_datetime(row["DATE"], dayfirst=True)
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
            asset = Asset(isin=isin.upper(), amount=amount, transaction_price=transaction_price)
            db.add(asset)
    db.commit()
    return {"status": "success", "message": f"{len(df)} assets uploaded"}