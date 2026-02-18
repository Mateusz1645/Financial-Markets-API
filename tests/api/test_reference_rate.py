from models import Reference_Rate


def test_reference_rate_list(client):
    response = client.get("/reference_rate/list")

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )

    data = response.json()

    assert isinstance(data, list), f"Expected list, got {type(data)}: {data}"
    assert len(data) > 0, "Expected non-empty list, got empty list"
    for idx, row in enumerate(data):
        assert "year" in row, f"Row {idx}: missing key 'year'"
        assert "value" in row, f"Row {idx}: missing key 'value'"

        year = row["year"]
        value = row["value"]

        assert isinstance(year, int), f"Row {idx}: year is not int: {year}"
        assert isinstance(value, (int, float)), (
            f"Row {idx}: value is not numeric: {value}"
        )

        assert value < 0.5, (
            f"Row {idx}: for year {year} expected value < 0.5, got {value}"
        )


def test_add_reference_rate(client, db_session):
    response = client.post(
        "/reference_rate/add", params={"month": 1, "year": 2099, "value": 0.2}
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )
    data = response.json()

    assert data["message"] == "Reference Rate added successfully", (
        f"Unexpected message: {data}"
    )
    assert data["month"] == 1, f"Expected month 1, got {data['month']}"
    assert data["year"] == 2099, f"Expected year 2099, got {data['year']}"
    assert data["value"] == 0.2, f"Expected value 0.2, got {data['value']}"

    db_record = db_session.query(Reference_Rate).filter_by(month=1, year=2099).first()
    assert db_record is not None, "Reference Rate record not found in DB after adding"
    assert db_record.value == 0.2, f"Expected DB value 0.5, got {db_record.value}"


def test_delete_reference_rate(client, db_session):
    record = Reference_Rate(month=2, year=2099, value=0.3)
    db_session.add(record)
    db_session.commit()

    response = client.delete(
        "/reference_rate/delete", params={"reference_rate_id": record.id}
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Response: {response.text}"
    )

    db_record = db_session.query(Reference_Rate).filter_by(id=record.id).first()
    assert db_record is None, (
        f"Record with id {record.id} still exists in DB after delete"
    )


def test_add_reference_rate_duplicate(client, db_session):
    response = client.post(
        "/reference_rate/add", params={"month": 12, "year": 2025, "value": 4.0}
    )

    assert response.status_code == 400, (
        f"Expected 400 for duplicate entry, got {response.status_code}. Response: {response.text}"
    )
