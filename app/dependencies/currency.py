import requests
from app.schemas.user import UserData
from fastapi import HTTPException

currency_fields = [
    "total_credit_limit",
    "used_credit_amount",
    "available_credit_limit",
    "total_card_balance",
    "total_income",
    "monthly_debt_payments",
]


def get_uah_to_usd() -> int:
    url = "https://v6.exchangerate-api.com/v6/4ca83eeae455d22f20ac2a2f/latest/USD"

    try:
        response = requests.get(url)
        data = response.json()
        return data["conversion_rates"]["UAH"]
    except Exception as e:
        raise HTTPException(status_code=500)


def convert_to_usd(userData: UserData):
    data = userData.model_dump()
    convertion_rate = get_uah_to_usd()
    for feat in currency_fields:
        data[feat] = data[feat] / convertion_rate if data[feat] != 0 else 0
    return UserData(**data)
