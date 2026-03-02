import pandas as pd
from sqlalchemy.orm import Session
from models import Reference_Rate
from utils.date_utils import parse_date
from fastapi import HTTPException
from datetime import datetime


def load_reference_rate_from_custom_csv(db: Session, csv_path: str):
    df = pd.read_csv(csv_path, skipinitialspace=True)
    df = df.replace(r"^\s*$", None, regex=True)

    for _, row in df.iterrows():
        date = row["date"]
        date = parse_date(date)
        raw_value = row["value"]
        if not date:
            continue
        try:
            value = round(float(raw_value) / 100, 4)
        except ValueError:
            continue

        record = db.query(Reference_Rate).filter_by(date=date).first()
        if not record:
            db.add(Reference_Rate(date=date, value=value))

    db.commit()


def get_reference_rate(db: Session, target_date: datetime) -> float:
    record = (
        db.query(Reference_Rate)
        .filter(Reference_Rate.date <= target_date)
        .order_by(Reference_Rate.date.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No reference rate found before {target_date}",
        )

    return record.value
