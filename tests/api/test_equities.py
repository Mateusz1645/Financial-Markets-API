from models import Equity

def test_list_equities(client):
    response = client.get("/equities/list")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}.  Response: {response.text}"
    assert isinstance(response.json(), list), f"Expected list, got {type(response.json())}: {response.json()}"
    assert len(response.json()) > 0, "Equities list is empty"

def test_add_equities(client):
    response = client.post(
        "/equities/add",
        params={
            "symbol": "XXX13211XXX",
            "name": "Test equities"
        }
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    assert response.json()["status"] == "success", f"Expected status 'success', got {response.json()}"

def test_add_equities_duplicate_symbol(client):
    response = client.post(
        "/equities/add",
        params={
            "symbol": "AAPL",
            "name": "Test equities"
        }
    )

    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert response.json()["detail"] == "Equity with symbol 'AAPL' already exists"

def test_add_equities_duplicate_isin(client):
    response = client.post(
        "/equities/add",
        params={
            "symbol": "XXXX142141XXXX",
            "isin": "US0378331005",
            "name": "Test equities"
        }
    )

    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert response.json()["detail"] == "Equity with ISIN 'US0378331005' already exists"
