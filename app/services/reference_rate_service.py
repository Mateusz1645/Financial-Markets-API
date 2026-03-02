import pandas as pd
from sqlalchemy.orm import Session
from models import Reference_Rate
from utils.date_utils import parse_date


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
