from fastapi import HTTPException
import pandas as pd
import requests
import time
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
    10: 256, # October
    11: 257, # November
    12: 258  # December
}


def get_inflation_for_month(month, year):
    ip_period = ID_PERIOD_TO_MONTH_GUS_API.get(month)
    url = f"https://api-sdp.stat.gov.pl/api/variable/variable-data-section?id-zmienna=305&id-przekroj=739&id-rok={year}&id-okres={ip_period}&page-size=50&page=0&lang=pl"
    response = requests.get(url)
    try: 
        response = requests.get(url)  
        if response.status_code == 200:
            data = response.json()
            records = data.get('data', [])
            df = pd.DataFrame(records)
            df = df[(df['id-pozycja-2'] == 6656078) & (df['id-sposob-prezentacji-miara'] == 5)] # 6656078 for Poland in general and 5 for cpi
            if df.empty:
                return None
            time.sleep(1) # to not overloard gus api
            return df['wartosc'].iloc[0] - 100
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error from api-sdp.stat.gov: {e, response.status_code}")
    