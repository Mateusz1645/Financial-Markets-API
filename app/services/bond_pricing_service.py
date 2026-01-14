from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Asset
import datetime
from dateutil.relativedelta import relativedelta
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

def get_ots_days(date_start, valuation_date):
    end_of_period = date_start + relativedelta(months=3)
    if valuation_date < end_of_period:
        return (valuation_date - date_start).days
    else:
        return (end_of_period - date_start).days
    
def value_ots(margin: float, days: float, value: int = 100, tax: float = 0.19) -> float:
    interest = value * margin * days / 365.25
    return interest * (1 - tax)

def value_tos(margin: float, days: float, value: int = 100) -> float:
    interest = value * margin * days / 365.25
    return interest

def calculate_value_of_bond(asset: Asset , db: Session, date: str="today"):

    type_of_bond = asset.isin[:3]

    if asset.type_.upper() != "BOND":
        raise HTTPException(
            status_code=400,
            detail=f"Wrong asset type for calculating bond value: {asset.isin}, {asset.name}, {asset.date}"
        )

    if type_of_bond in ["COI", "EDO"] and (asset.coupon_rate is None or asset.inflation_first_year is None):
        raise HTTPException(
            status_code=400,
            detail=f"coupon_rate and inflation_first_year are required for {type_of_bond} bond {asset.isin}, {asset.name}"
        )

    if type_of_bond in ["OTS", "TOS"] and asset.coupon_rate is None:
        raise HTTPException(
            status_code=400,
            detail=f"coupon_rate is required for {type_of_bond} bond {asset.isin}, {asset.name}"
        )
    
    date_start = asset.date
    valuation_date = datetime.datetime.now() if date == "today" else parse_date(date)

    if valuation_date <= date_start:
        return asset.transaction_price
    
    value = asset.transaction_price
    days_since_purchase = (valuation_date - date_start).days

    max_years = None
    if type_of_bond == "COI":
        max_years = 4
    elif type_of_bond == "TOS":
        max_years = 3
    elif type_of_bond == "EDO":
        max_years = 10
    
    if max_years is not None:
        max_end_date = date_start + relativedelta(years=max_years)
        if valuation_date > max_end_date:
            valuation_date = max_end_date
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
        current_date = date_start + relativedelta(years=1)
        while current_date + relativedelta(years=1) <= valuation_date:
            inflation = get_inflation(db, current_date.month, current_date.year)
            value += value_coi(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=asset.transaction_price,
                days=365.25
            )
            current_date += relativedelta(years=1)

        # COI last year
        remaining_days = (valuation_date - current_date).days
        if remaining_days > 0:
            tmp_date = current_date
            inflation = None
            while inflation is None:
                try:
                    inflation = get_inflation(db, tmp_date.month, tmp_date.year)
                except (HTTPError, ValueError):
                    tmp_date -= relativedelta(months=1)
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
        current_date = date_start + relativedelta(years=1)
        while current_date + relativedelta(years=1) <= valuation_date:
            inflation = get_inflation(db, current_date.month, current_date.year)
            value += value_edo(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=value,
                days=365.25
            )
            current_date += relativedelta(years=1)

        # EDO last year
        remaining_days = (valuation_date - current_date).days
        if remaining_days > 0:
            tmp_date = current_date
            inflation = None
            while inflation is None:
                try:
                    inflation = get_inflation(db, tmp_date.month, tmp_date.year)
                except (HTTPError, ValueError):
                        tmp_date -= relativedelta(months=1)
            value += value_edo(
                inflation=inflation,
                margin=asset.coupon_rate,
                value=value,
                days=remaining_days
            )

        value = (value - ((value - asset.transaction_price) * 0.19))

        return value
    
    elif type_of_bond == "OTS":
        # OTS only last 3 months
        days = get_ots_days(date_start, valuation_date)
        value += value_ots(
            margin=asset.coupon_rate,
            value=asset.transaction_price,
            days=days
        )
        return value

    elif type_of_bond == "TOS":
        # TOS term shorter than one year
        if days_since_purchase <= 365.25: 
            value += value_tos(
                margin=asset.coupon_rate,
                value=value,
                days=days_since_purchase
            )
            return (value - ((value - asset.transaction_price) * 0.19))
        
        value += value_tos(
            margin=asset.coupon_rate,
            value=value,
            days=365.25
        )

        # TOS after firsty year without last
        current_date = date_start + relativedelta(years=1)
        while current_date + relativedelta(years=1) <= valuation_date:
            value += value_tos(
                margin=asset.coupon_rate,
                value=value,
                days=365.25
            )
            current_date += relativedelta(years=1)

        # TOS last year
        remaining_days = (valuation_date - current_date).days
        if remaining_days > 0:
            value += value_tos(
                margin=asset.coupon_rate,
                value=value,
                days=remaining_days
            )

        value = (value - ((value - asset.transaction_price) * 0.19))

        return value

    else:
        raise HTTPException(status_code=400, detail="Bond type not supported.")



