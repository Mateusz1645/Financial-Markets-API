from typing import Optional
from fastapi import HTTPException


def validate_bond_fields(type_: str, isin: str, coupon_rate: Optional[float], inflation_first_year: Optional[float]) -> tuple[Optional[float], Optional[float]]:

    if type_.upper() != "BOND":
        return None, None

    bond_type = isin[:3].upper()

    # COI / EDO / ROS / ROD
    if bond_type in ("COI", "EDO", "ROS", "ROD"):
        if coupon_rate is None or inflation_first_year is None:
            raise HTTPException(
                status_code=400,
                detail=f"COI/EDO bonds require coupon_rate and inflation_first_year ({isin})"
            )

    # OTS / TOS
    elif bond_type in ("OTS", "TOS"):
        if coupon_rate is None:
            raise HTTPException(
                status_code=400,
                detail=f"OTS/TOS bonds require coupon_rate ({isin})"
            )
        inflation_first_year = None

    else:
        coupon_rate = None
        inflation_first_year = None

    return coupon_rate, inflation_first_year

