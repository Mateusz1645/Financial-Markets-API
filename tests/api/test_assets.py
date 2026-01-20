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
            "type_": "EQUITY"
        }
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    assert response.json()["status"] == "success", f"Expected status 'success', got {response.json()}"

def test_delete_asset(client, db_session):

    asset = Asset(
        isin="TEST123",
        name="Test Asset",
        date=datetime.utcnow(),
        amount=10,
        transaction_price=100,
        currency="USD",
        currency_transaction="USD",
        type_="STOCK"
    )
    db_session.add(asset)
    db_session.commit()

    response = client.delete(
        "/assets/delete",
        params={
            "asset_id": 1
        }
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    assert response.json()["status"] == "success", f"Expected status 'success', got {response.json()}"

def test_list_assets(client):
    response = client.get("/assets/list")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}.  Response: {response.text}"
    assert isinstance(response.json(), list), f"Expected list, got {type(response.json())}: {response.json()}"

    
        