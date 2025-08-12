from typing import TypedDict


class CurrencyConversion(TypedDict):
    from_currency: str
    to_currency: str
    amount: float