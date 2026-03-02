from models import Asset
from datetime import datetime


def test_add_asset(client):
    response = client.post(
        "/assets/add",
        params={
            "isin": "PLTEST000000",
            "name": "Test Asset",
            "amount": 10,
            "date": "01.01.2024 12:00",
            "transaction_price": 100,
            "currency": "PLN",
            "currency_transaction": "PLN",
            "type_": "EQUITY",
        },
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["status"] == "success", (
        f"Expected status 'success', got {response.json()}"
    )


def test_add_asset_duplicate(client, db_session):

    asset = Asset(
        isin="PLTEST000000",
        name="Test Asset",
        date=datetime(2024, 1, 1, 12, 0),
        amount=10,
        transaction_price=100,
        currency="PLN",
        currency_transaction="PLN",
        type_="EQUITY",
    )
    db_session.add(asset)
    db_session.commit()

    response = client.post(
        "/assets/add",
        params={
            "isin": "PLTEST000000",
            "name": "Test Asset",
            "amount": 10,
            "date": "01.01.2024 12:00",
            "transaction_price": 100,
            "currency": "PLN",
            "currency_transaction": "PLN",
            "type_": "EQUITY",
        },
    )
    asset_in_db = db_session.query(Asset).first()
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["status"] == "success", (
        f"Expected status 'success', got {response.json()}"
    )
    assert asset_in_db.amount == 20, (
        f"Wrong amount in asset got: {asset_in_db.amount}, expected: 20"
    )
    assert asset_in_db.transaction_price == 200, (
        f"Wrong transaction_price in asset got: {asset_in_db.transaction_price}, expected: 200"
    )


def test_delete_asset(client, db_session):

    asset = Asset(
        isin="TEST123",
        name="Test Asset",
        date=datetime.utcnow(),
        amount=10,
        transaction_price=100,
        currency="USD",
        currency_transaction="USD",
        type_="STOCK",
    )
    db_session.add(asset)
    db_session.commit()

    response = client.delete("/assets/delete", params={"asset_id": 1})
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["status"] == "success", (
        f"Expected status 'success', got {response.json()}"
    )


def test_delete_asset_not_exist(client, db_session):

    response = client.delete("/assets/delete", params={"asset_id": 99999})
    assert response.status_code == 404, (
        f"Expected 404, got {response.status_code}. Response: {response.text}"
    )


def test_list_assets(client):
    response = client.get("/assets/list")

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}.  Response: {response.text}"
    )
    assert isinstance(response.json(), list), (
        f"Expected list, got {type(response.json())}: {response.json()}"
    )


def test_upload_assets_valid_csv(client):
    with open("sample_portfolio.csv", "rb") as f:
        response = client.post(
            "/assets/upload", files={"file": ("sample_portfolio.csv", f, "text/csv")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"][-15:] == "assets uploaded"
