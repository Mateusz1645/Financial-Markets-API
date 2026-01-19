import warnings
from models import Inflation

def test_inflation(client):
    response = client.get("/inflation/list")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

    data = response.json()

    assert isinstance(data, list), f"Expected list, got {type(data)}: {data}"
    assert len(data) > 0, "Expected non-empty list, got empty list"
    for idx, row in enumerate(data):
        assert "year" in row, f"Row {idx}: missing key 'year'"
        assert "value" in row, f"Row {idx}: missing key 'value'"

        year = row["year"]
        value = row["value"]

        assert isinstance(year, int), f"Row {idx}: year is not int: {year}"
        assert isinstance(value, (int, float)), f"Row {idx}: value is not numeric: {value}"
        
        if year >= 1992:
            assert value < 0.5, f"Row {idx}: for year {year} expected value < 0.5, got {value}"
        elif 1992 > year > 1990:
            if value > 0.5:
                assert value < 1, f"Row {idx}: for year {year} expected value < 1, got {value}"
        else:
            assert value <= 1200, f"Row {idx}: value > 1.5 for year {year}: {value}"

def test_add_inflation(client, db_session):
    response = client.post("/inflation/add", params={
        "month": 1,
        "year": 2099,
        "value": 0.5
    })

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()

    assert data["message"] == "Inflation added successfully", f"Unexpected message: {data}"
    assert data["month"] == 1, f"Expected month 1, got {data['month']}"
    assert data["year"] == 2099, f"Expected year 2099, got {data['year']}"
    assert data["value"] == 0.5, f"Expected value 0.5, got {data['value']}"

    db_record = db_session.query(Inflation).filter_by(month=1, year=2099).first()
    assert db_record is not None, "Inflation record not found in DB after adding"
    assert db_record.value == 0.5, f"Expected DB value 0.5, got {db_record.value}"

def test_delete_inflation(client, db_session):
    record = Inflation(month=2, year=2099, value=0.4)
    db_session.add(record)
    db_session.commit()

    response = client.delete("/inflation/delete", params={"inflation_id": record.id})
    assert response.status_code == 200

    db_record = db_session.query(Inflation).filter_by(id=record.id).first()
    assert db_record is None

def test_delete_inflation(client, db_session):
    record = Inflation(month=2, year=2099, value=0.4)
    db_session.add(record)
    db_session.commit()

    response = client.delete("/inflation/delete", params={"inflation_id": record.id})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"

    db_record = db_session.query(Inflation).filter_by(id=record.id).first()
    assert db_record is None, f"Record with id {record.id} still exists in DB after delete"

def test_add_inflation_duplicate(client, db_session):
    response = client.post("/inflation/add", params={
        "month": 1,
        "year": 2024,
        "value": 0.5
    })

    assert response.status_code == 401, f"Expected 400 for duplicate entry, got {response.status_code}. Response: {response.text}"

