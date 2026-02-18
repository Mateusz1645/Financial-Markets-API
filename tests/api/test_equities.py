from models import Equity

GET_SYMBOL = {
    "US0378331005": "AAPL",  # Apple
    "US5949181045": "MSFT",  # Microsoft
    "US0231351067": "AMZN",  # Amazon
    "US30303M1027": "META",  # Meta
    "US88160R1014": "TSLA",  # Tesla
    "ZZ0000000000": None,
}


def test_list_equities(client):
    response = client.get("/equities/list")

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}.  Response: {response.text}"
    )
    assert isinstance(response.json(), list), (
        f"Expected list, got {type(response.json())}: {response.json()}"
    )
    assert len(response.json()) > 0, "Equities list is empty"


def test_add_equities(client):
    response = client.post(
        "/equities/add", params={"symbol": "XXX13211XXX", "name": "Test equities"}
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["status"] == "success", (
        f"Expected status 'success', got {response.json()}"
    )


def test_add_equities_duplicate_symbol(client):
    response = client.post(
        "/equities/add", params={"symbol": "AAPL", "name": "Test equities"}
    )

    assert response.status_code == 400, (
        f"Expected 400, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["detail"] == "Equity with symbol 'AAPL' already exists"


def test_add_equities_duplicate_isin(client):
    response = client.post(
        "/equities/add",
        params={
            "symbol": "XXXX142141XXXX",
            "isin": "US0378331005",
            "name": "Test equities",
        },
    )

    assert response.status_code == 400, (
        f"Expected 400, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["detail"] == "Equity with ISIN 'US0378331005' already exists"


def test_delete_equity(client, db_session):

    equity = Equity(
        symbol="TEST12321",
        isin="TEST123",
        name="Test Equity",
    )
    db_session.add(equity)
    db_session.commit()

    response = client.delete(
        "/equities/delete", params={"symbol": "TEST12321", "isin": "TEST123"}
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    assert response.json()["status"] == "success", (
        f"Expected status 'success', got {response.json()}"
    )
    assert response.json()["symbol"] == "TEST12321", (
        f"Wrong symbol deleted: {response.symbol}"
    )


def test_get_equities(client):
    errors = []
    for isin, expected_symbol in GET_SYMBOL.items():
        response = client.get("/equities/get_symbol", params={"isin": isin})
        if response.status_code != 200:
            errors.append(f"{isin}: status {response.status_code}")
            continue

        data = response.json()

        if expected_symbol is None:
            if data != []:
                errors.append(f"{isin}: expected empty list, got {data}")
            continue

        if not any(symbol == expected_symbol for symbol in data):
            errors.append(f"{isin}: expected [{expected_symbol}], got {data}")

    assert not errors, f"Found errors: {errors}"
