from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Asset
import datetime
from services.inflation_service import get_inflation
from requests.exceptions import HTTPError
from utils.date_utils import parse_date

def value_coi(inflation: float, margin: float, days: float, value: int = 100, tax: float = 0.19) -> float:
    rate = inflation + margin
    interest = value * rate * days / 365.25
    return interest * (1 - tax)

def value_edo(inflation: float, margin: float, days: float, value: int = 100) -> float:
    rate = inflation + margin
    interest = value * rate * days / 365.25
    return interest

def calculate_value_of_bond(asset: Asset , db: Session, date: str="today"):

    if asset.type_.upper() != "BOND" or asset.coupon_rate is None or asset.inflation_first_year is None:
        raise HTTPException(status_code=400, detail=f"Wrong asset type or wront coupont_rate, inflation in first year choose to calculate current value of bond isin: {asset.isin}, name: {asset.name}, date:{asset.date}.")
    
    date_start = asset.date
    valuation_date = (
        datetime.datetime.now()
        if date == "today"
        else parse_date(date)
    )

    if valuation_date <= date_start:
        return asset.transaction_price
    
    type_of_bond = asset.isin[:3]
    value = asset.transaction_price
    days_since_purchase = (valuation_date - date_start).days
    if type_of_bond == "COI":

        # COI term shorter than one year
        if days_since_purchase <= 365.25: 
            value += value_coi(
                inflation=asset.inflation_first_year,
                margin=asset.coupon_rate,
                value=asset.transaction_price,
                days=days_since_purchase
            )
            return value
        
        # COI first year with input coupon_rate
        value += value_coi(
            inflation=asset.inflation_first_year,
            margin=asset.coupon_rate,
            value=asset.transaction_price,
            days=365.25
        )

        # COI after firsty year without last
        current_date = date_start + datetime.timedelta(days=365.25)
        while current_date + datetime.timedelta(days=365.25) <= valuation_date:
            inflation = get_inflation(db, current_date.month, current_date.year)
            value += value_coi(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=asset.transaction_price,
                days=365.25
            )
            current_date += datetime.timedelta(days=365.25)

        # COI last year
        remaining_days = (valuation_date - current_date).days
        if remaining_days > 0:
            month, year = valuation_date.month, valuation_date.year
            inflation = None
            while inflation is None:
                try:
                    inflation = get_inflation(db, current_date.month, current_date.year)
                except (HTTPError, ValueError):
                    month -= 1
                    if month == 0:
                        month = 12
                        year -= 1
            value += value_coi(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=asset.transaction_price,
                days=remaining_days
            )
        return value
    
    elif type_of_bond == 'EDO':

        # EDO term shorter than one year
        if days_since_purchase <= 365.25: 
            value += value_edo(
                inflation=asset.inflation_first_year,
                margin=asset.coupon_rate,
                value=value,
                days=days_since_purchase
            )
            return (value - ((value - asset.transaction_price) * 0.19))

        value += value_edo(
            inflation=asset.inflation_first_year,
            margin=asset.coupon_rate,
            value=value,
            days=365.25
        )

        # EDO after firsty year without last
        current_date = date_start + datetime.timedelta(days=365.25)
        while current_date + datetime.timedelta(days=365.25) <= valuation_date:
            inflation = get_inflation(db, current_date.month, current_date.year)
            value += value_edo(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=value,
                days=365.25
            )
            current_date += datetime.timedelta(days=365.25)

        # EDO last year
        remaining_days = (valuation_date - current_date).days
        if remaining_days > 0:
            month, year = valuation_date.month, valuation_date.year
            inflation = None
            while inflation is None:
                try:
                    inflation = get_inflation(db, current_date.month, current_date.year)
                except (HTTPError, ValueError):
                    month -= 1
                    if month == 0:
                        month = 12
                        year -= 1
            value += value_edo(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=value,
                days=remaining_days
            )

        value = (value - ((value - asset.transaction_price) * 0.19))

        return value

    else:
        raise HTTPException(status_code=400, detail="Bond type not supported.")



