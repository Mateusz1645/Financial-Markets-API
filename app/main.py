from fastapi import FastAPI
from db import engine, Base
from routes import portfolio

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Portfolio API",
    docs_url="/"
)

app.include_router(portfolio.router)
