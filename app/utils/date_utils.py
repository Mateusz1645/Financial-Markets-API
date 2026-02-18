from datetime import datetime
import pandas as pd
from fastapi import HTTPException

DATE_FORMATS = [
    "%d.%m.%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%Y.%m.%d",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y",
]


def parse_date(value) -> datetime:
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.to_pydatetime() if hasattr(value, "to_pydatetime") else value

    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="Invalid date type")

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue

    raise HTTPException(
        status_code=400,
        detail="Invalid date format. Accepted formats: DD.MM.YYYY, DD.MM.YYYY HH:MM, YYYY-MM-DD, etc.",
    )
