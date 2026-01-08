from fastapi import FastAPI
from db import engine, Base
from routes import portfolio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Portfolio API",
    docs_url="/",    lifespan=lifespan
)

app.include_router(portfolio.router)
