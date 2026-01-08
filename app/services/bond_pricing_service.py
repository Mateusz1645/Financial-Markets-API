from fastapi import HTTPException
from models import Asset
import datetime
from services.api_requests import get_inflation_for_month
from requests.exceptions import HTTPError

def value_coi(inflation: float, margin: float, days: float, value: int = 100, tax: float = 0.19) -> float:
    rate = inflation + margin
    interest = value * rate * days / 365.25
    return interest * (1 - tax)

def calculate_value_of_bond(asset: Asset):

    if asset.type_.upper() != "BOND" or asset.coupon_rate is None or asset.inflation_first_year is None:
        raise HTTPException(status_code=400, detail=f"Wrong asset type or wront coupont_rate, inflation in first year choose to calculate current value of bond isin: {asset.isin}, name: {asset.name}, date:{asset.date}.")
    
    date_start = asset.date
    today = datetime.datetime.now()
    type_of_bond = asset.isin[:3]
    value = asset.transaction_price

    if type_of_bond == "COI":
        days_since_purchase = (today - date_start).days

        # BOND term shorter than one year
        if days_since_purchase <= 365.25: 
            value += value_coi(
                inflation=asset.inflation_first_year,
                margin=asset.coupon_rate,
                value=asset.amount,
                days=days_since_purchase
            )
            return value
        
        # BOND first year with input coupon_rate
        value += value_coi(
            inflation=asset.inflation_first_year,
            margin=asset.coupon_rate,
            value=asset.amount,
            days=365.25
        )

        # BOND after firsty year without last
        current_date = date_start + datetime.timedelta(days=365.25)
        while current_date + datetime.timedelta(days=365.25) <= today:
            inflation = get_inflation_for_month(current_date.month, current_date.year)
            value += value_coi(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=asset.amount,
                days=365.25
            )
            current_date += datetime.timedelta(days=365.25)

        # BOND last year
        remaining_days = (today - current_date).days
        if remaining_days > 0:
            month, year = today.month, today.year
            inflation = None
            while inflation is None:
                try:
                    inflation = get_inflation_for_month(month, year)
                except (HTTPError, ValueError):
                    month -= 1
                    if month == 0:
                        month = 12
                        year -= 1
            value += value_coi(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=value,
                days=remaining_days
            )

        return value

    else:
        raise HTTPException(status_code=400, detail="Bond type not supported.")



