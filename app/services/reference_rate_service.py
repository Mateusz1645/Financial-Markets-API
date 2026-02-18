import pandas as pd
from sqlalchemy.orm import Session
from models import Reference_Rate

MONTHS_PL = {
    "Styczeń": 1,
    "Luty": 2,
    "Marzec": 3,
    "Kwiecień": 4,
    "Maj": 5,
    "Czerwiec": 6,
    "Lipiec": 7,
    "Sierpień": 8,
    "Wrzesień": 9,
    "Październik": 10,
    "Listopad": 11,
    "Grudzień": 12
}


def load_reference_rate_from_custom_csv(db: Session, csv_path: str):
    df = pd.read_csv(csv_path, skipinitialspace=True)
    df = df.replace(r'^\s*$', None, regex=True)

    for _, row in df.iterrows():
        month_name = row['label']
        month = MONTHS_PL.get(month_name)
        if not month:
            continue

        for year_col in df.columns[1:]:
            try:
                year = int(year_col)
            except ValueError:
                continue

            raw_value = row[year_col]

            if raw_value is None or pd.isna(raw_value):
                continue

            try:
                value = round(float(raw_value) / 100, 4)
            except ValueError:
                continue

            record = db.query(Reference_Rate).filter_by(year=year, month=month).first()
            if not record:
                db.add(Reference_Rate(year=year, month=month, value=value))

    db.commit()
