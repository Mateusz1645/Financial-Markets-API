from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import time
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def wait_for_db(engine, retries=10):
    for _ in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Database not ready")