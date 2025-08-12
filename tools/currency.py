import datetime
import os
from dotenv import load_dotenv
from python_exchange_rates import AbstractExchangeRates

from types.currency import CurrencyConversion

load_dotenv(override=True)

class CurrencyConverterTool:
    data: CurrencyConversion

    def __init__(self, data: CurrencyConversion):
        self.data = data

    @staticmethod
    def get_tool_description() -> dict:
        return {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another. Call this tool to convert a specified amount from one currency to another.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                            "from_currency": {
                                "type": "string",
                                "description": "The currency code to convert from (e.g., 'USD', 'EUR')."
                            },
                            "to_currency": {
                                "type": "string",
                                "description": "The currency code to convert to (e.g., 'JPY', 'GBP')."
                            },
                            "amount": {
                                "type": "number",
                                "description": "The amount of money to convert."
                            }
                        },
                        "required": ["from_currency", "to_currency", "amount"],
                        "additionalProperties": False
                    }
                },
                "required": ["data"],
                "additionalProperties": False
            }
        }

    def convert_currency(self) -> dict:
        api_key = os.getenv("ABSTRACT_API_KEY")

        if not api_key:
            raise ValueError("ABSTRACT_API_KEY environment variable is not set. Please set it in your .env file.")
        elif api_key.strip() != api_key:
            raise ValueError("ABSTRACT_API_KEY must not contain leading or trailing whitespace. Please check your API key.")
        else:
            print("Abstract API key is valid and loaded successfully.")

        base = self.data.get('from_currency')
        target = self.data.get('to_currency')
        amount = self.data.get('amount')
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        conversion_result = AbstractExchangeRates.convert(base, target, date, amount)

        if conversion_result is None:
            raise ValueError(f"Conversion from {base} to {target} failed. Please check the currency codes and try again.")
        return {
            "from_currency": base,
            "to_currency": target,
            "amount": amount,
            "converted_amount": conversion_result['result'],
        }