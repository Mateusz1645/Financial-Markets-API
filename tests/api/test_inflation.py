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

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Inflation added successfully"
    assert data["month"] == 1
    assert data["year"] == 2099
    assert data["value"] == 0.5

    db_record = db_session.query(Inflation).filter_by(month=1, year=2099).first()
    assert db_record is not None
    assert db_record.value == 0.5

def test_delete_inflation(client, db_session):
    record = Inflation(month=2, year=2099, value=0.4)
    db_session.add(record)
    db_session.commit()

    response = client.delete("/inflation/delete", params={"inflation_id": record.id})
    assert response.status_code == 200

    db_record = db_session.query(Inflation).filter_by(id=record.id).first()
    assert db_record is None

