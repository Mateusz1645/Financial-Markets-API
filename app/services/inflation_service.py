from fastapi import HTTPException
import pandas as pd
import requests
import time
from sqlalchemy.orm import Session
from models import Inflation

ID_PERIOD_TO_MONTH_GUS_API = {
    1: 247,  # January
    2: 248,  # February
    3: 249,  # March
    4: 250,  # April
    5: 251,  # May
    6: 252,  # June
    7: 253,  # July
    8: 254,  # August
    9: 255,  # September
    10: 256,  # October
    11: 257,  # November
    12: 258,  # December
}

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
    "Grudzień": 12,
}


def get_inflation_for_month(month, year):
    ip_period = ID_PERIOD_TO_MONTH_GUS_API.get(month)
    url = f"https://api-sdp.stat.gov.pl/api/variable/variable-data-section?id-zmienna=305&id-przekroj=739&id-rok={year}&id-okres={ip_period}&page-size=50&page=0&lang=pl"
    response = requests.get(url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            records = data.get("data", [])
            df = pd.DataFrame(records)
            df = df[
                (df["id-pozycja-2"] == 6656078)
                & (df["id-sposob-prezentacji-miara"] == 5)
            ]  # 6656078 for Poland in general and 5 for cpi
            if df.empty:
                return None
            time.sleep(1)  # to not overloard gus api
            return round((df["wartosc"].iloc[0] - 100) / 100, 4)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error from api-sdp.stat.gov: {e, response.status_code}",
        )


def get_inflation(db: Session, month: int, year: int) -> float:
    record = db.query(Inflation).filter_by(year=year, month=month).first()
    if record:
        return record.value

    value = get_inflation_for_month(month, year)
    if value is not None:
        new_record = Inflation(year=year, month=month, value=value)
        db.add(new_record)
        db.commit()
    return value


def load_inflation_from_custom_csv(db: Session, csv_path: str):
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        month_name = row["label"]
        month = MONTHS_PL.get(month_name)
        if not month:
            continue

        for year_col in df.columns[1:]:
            try:
                year = int(year_col)
                value = round(float(row[year_col] / 100), 4)
            except (ValueError, TypeError):
                continue

            record = db.query(Inflation).filter_by(year=year, month=month).first()
            if not record:
                db.add(Inflation(year=year, month=month, value=value))

    db.commit()
