from fastapi import HTTPException
import numpy as np
import pandas as pd
from models import Asset
import datetime
import requests
from app.services.api_requests import get_inflation_for_month

# def value_coi(inflation: float, margin: float, value: int = 100, days: int, tax: float = 0.19) -> float:
#     rate = inflation + margin
#     interest = value * rate * days / 365.25
#     return value + interest * (1 - tax)

# def calculate_value_of_bond(asset: Asset):

#     if asset.type_.upper() != "BOND" or asset.coupon_rate is None:
#         raise HTTPException(status_code=400, detail=f"Wrong asset type choose to calculate current value of bond isin: {asset.isin}, name: {asset.name}, date:{asset.date}.")
    
#     today = datetime.date.today()
#     type_of_bond = asset.isin[:3]

#     if type_of_bond == "COI":

