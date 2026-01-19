from datetime import datetime
from models import Forex

def test_forex_pairs_exist_in_db(db_session):
    pairs = [
        ("USD", "PLN"),
        ("EUR", "PLN"),
        ("GBP", "PLN"),
        ("CHF", "PLN"),
        ("JPY", "PLN"),
        ("CAD", "PLN"),
        ("AUD", "PLN"),
        ("NZD", "PLN"),
        ("SEK", "PLN"),
        ("NOK", "PLN"),
        ("DKK", "PLN"),
    ]

    missing_pairs = []

    for first, second in pairs:
        exists = db_session.query(Forex).filter(
            Forex.first_currency == first,
            Forex.second_currency == second
        ).first()

        if not exists:
            missing_pairs.append((first, second))

    assert not missing_pairs, f"Missing pairs in DB: {missing_pairs}"

def test_forex_list(client, db_session):
    db_session.add_all([
        Forex(first_currency="USD", second_currency="PLN", value=4.5, date=datetime(2099, 1, 1)),
        Forex(first_currency="USD", second_currency="PLN", value=4.6, date=datetime(2099, 1, 2)),
        Forex(first_currency="EUR", second_currency="PLN", value=4.3, date=datetime(2099, 1, 1)),
    ])
    db_session.commit()

    response = client.get("/forex/list", params={
        "first_currency": "USD",
        "second_currency": "PLN"
    })

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    assert data[-1]["date"] == "2099-01-02"
    assert data[-1]["value"] == 4.6
