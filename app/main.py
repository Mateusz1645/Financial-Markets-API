from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from models import Asset
import pandas as pd
import requests

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Portfolio API",
    docs_url="/"
)

@app.post("/upload-portfolio")
def upload_portfolio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_excel(file.file)
    for _, row in df.iterrows():
        symbol, amount = row["symbol"], row["amount"]
        asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
        if asset:
            asset.amount += amount
        else:
            asset = Asset(symbol=symbol.upper(), amount=amount)
            db.add(asset)
    db.commit()
    return {"status": "success", "message": f"{len(df)} assets uploaded"}

@app.post("/portfolio/add")
def add_asset(symbol: str, amount: float, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
    if asset:
        asset.amount += amount
    else:
        asset = Asset(symbol=symbol.upper(), amount=amount)
        db.add(asset)
    db.commit()
    db.refresh(asset)
    return {"symbol": asset.symbol, "amount": asset.amount}

@app.get("/portfolio")
def list_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    return [{"symbol": a.symbol, "amount": a.amount} for a in assets]

@app.get("/portfolio/value")
def portfolio_value(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    total_value = 0
    values = []
    for a in assets:
        price = 100
        value = price * a.amount
        total_value += value
        values.append({"symbol": a.symbol, "amount": a.amount, "price": price, "value": value})
    return {"total_value": total_value, "assets": values}
