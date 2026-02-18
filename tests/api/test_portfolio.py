from datetime import datetime, timedelta

BONDS_TO_CALCULATE = {
    "bond_coi": {
        "isin": "COI123456",
        "name": "Test COI Bond",
        "type_": "BOND",
        "amount": 100,
        "transaction_price": 1000,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.05,
        "inflation_first_year": 0.03,
        "days_ago": 200,
    },
    "bond_edo": {
        "isin": "EDO123456",
        "name": "Test EDO Bond",
        "type_": "BOND",
        "amount": 50,
        "transaction_price": 500,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.04,
        "inflation_first_year": 0.02,
        "days_ago": 400,
    },
    "bond_rod": {
        "isin": "ROD123456",
        "name": "Test ROD Bond",
        "type_": "BOND",
        "amount": 50,
        "transaction_price": 500,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.04,
        "inflation_first_year": 0.02,
        "days_ago": 400,
    },
    "bond_ros": {
        "isin": "ROS123456",
        "name": "Test ROS Bond",
        "type_": "BOND",
        "amount": 20,
        "transaction_price": 200,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.04,
        "inflation_first_year": 0.02,
        "days_ago": 300,
    },
    "bond_ots": {
        "isin": "OTS123456",
        "name": "Test OTS Bond",
        "type_": "BOND",
        "amount": 20,
        "transaction_price": 200,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.04,
        "inflation_first_year": None,
        "days_ago": 50,
    },
    "bond_tos": {
        "isin": "TOS123456",
        "name": "Test OTS Bond",
        "type_": "BOND",
        "amount": 20,
        "transaction_price": 200,
        "currency_transaction": "PLN",
        "currency": "PLN",
        "coupon_rate": 0.04,
        "inflation_first_year": None,
        "days_ago": 500,
    },
}


def test_calc_current_value_bonds(client):

    for bond_data in BONDS_TO_CALCULATE.values():
        bond_datetime = (
            datetime.utcnow() - timedelta(days=bond_data["days_ago"])
        ).replace(hour=0, minute=0, second=0, microsecond=0)

        params = {
            "isin": bond_data["isin"],
            "name": bond_data["name"],
            "amount": bond_data["amount"],
            "date": bond_datetime.strftime("%d.%m.%Y %H:%M"),
            "transaction_price": bond_data["transaction_price"],
            "currency": bond_data["currency"],
            "currency_transaction": bond_data["currency_transaction"],
            "type_": bond_data["type_"],
            "coupon_rate": bond_data["coupon_rate"],
        }

        if bond_data["inflation_first_year"] is not None:
            params["inflation_first_year"] = bond_data["inflation_first_year"]

        response_add = client.post("/assets/add", params=params)
        assert response_add.status_code == 200, (
            f"Status: {response_add.status_code}, Respons: {response_add.text}"
        )

        response_calc = client.get(
            "/assets/calc_current_value",
            params={
                "isin": bond_data["isin"],
                "date": bond_datetime.strftime("%Y-%m-%d"),
            },
        )

        assert response_calc.status_code == 200, (
            f"Status: {response_calc.status_code}, Respons: {response_calc.text}"
        )

        data = response_calc.json()[0]

        assert data["isin"] == bond_data["isin"], (
            f"Wrong isin got: {data['isin']} expected: {bond_data['isin']}"
        )
        assert data["value"] >= bond_data["transaction_price"], (
            f"Current value is smaller than transaction price: {data['value']} < {bond_data['transaction_price']}"
        )
        assert data["value_in_currency_per_unit"] > 0, (
            f"value_in_currency_per_unit = {data['value_in_currency_per_unit']} < 0"
        )
        assert data["amount"] == bond_data["amount"], (
            f"Amount before not equal after: before - {data['amount']}, after - {bond_data['amount']}"
        )
