from fastapi import FastAPI
from db import engine, Base, get_db
from routes import portfolio, inflation
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from services.inflation_service import load_inflation_from_custom_csv

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db: Session = next(get_db())
    load_inflation_from_custom_csv(db, "data/inflation.csv")

    yield

app = FastAPI(
    title="Portfolio API",
    docs_url="/",    lifespan=lifespan
)

app.include_router(portfolio.router)
app.include_router(inflation.router)
