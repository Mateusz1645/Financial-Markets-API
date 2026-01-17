from fastapi import FastAPI
from db import engine, Base, get_db, wait_for_db
from routes import portfolio, inflation, equities
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from services.inflation_service import load_inflation_from_custom_csv
from services.market_data_services import import_all_equities_once

@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db(engine=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = next(get_db())
    load_inflation_from_custom_csv(db, "data/inflation.csv")
    import_all_equities_once(db)

    db.close()
    yield

app = FastAPI(
    title="Portfolio API",
    docs_url="/",    lifespan=lifespan
)

app.include_router(portfolio.router)
app.include_router(inflation.router)
app.include_router(equities.router)