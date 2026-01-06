from fastapi import FastAPI
from db import engine, Base
from routes import portfolio

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Portfolio API",
    docs_url="/"
)

app.include_router(portfolio.router)


# @app.post("/portfolio/add")
# def add_asset(symbol: str, amount: float, db: Session = Depends(get_db)):
#     asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
#     if asset:
#         asset.amount += amount
#     else:
#         asset = Asset(symbol=symbol.upper(), amount=amount)
#         db.add(asset)
#     db.commit()
#     db.refresh(asset)
#     return {"symbol": asset.symbol, "amount": asset.amount}

# @app.get("/portfolio")
# def list_assets(db: Session = Depends(get_db)):
#     assets = db.query(Asset).all()
#     return [{"symbol": a.isin, "amount": a.amount} for a in assets]

# @app.get("/portfolio/value")
# def portfolio_value(db: Session = Depends(get_db)):
#     assets = db.query(Asset).all()
#     total_value = 0
#     values = []
#     for a in assets:
#         price = 100
#         value = price * a.amount
#         total_value += value
#         values.append({"symbol": a.symbol, "amount": a.amount, "price": price, "value": value})
#     return {"total_value": total_value, "assets": values}
