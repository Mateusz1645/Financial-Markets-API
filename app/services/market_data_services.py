import financedatabase as fd
import pandas as pd
from sqlalchemy.orm import Session
from models import Equity

def import_all_equities_once(db: Session):
    if db.query(Equity).first():
        return

    equities = fd.Equities()
    df = equities.select()

    objects = []

    for symbol, row in df.iterrows():
        objects.append(
            Equity(
                symbol=symbol,
                isin=row.get("isin"),
                name=row.get("name"),
                currency=row.get("currency"),
                sector=row.get("sector"),
                industry=row.get("industry"),
                exchange=row.get("exchange"),
                market=row.get("market"),
                country=row.get("country"),
                market_cap=row.get("market_cap"),
            )
        )

    db.bulk_save_objects(objects)
    db.commit()
