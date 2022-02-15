from dataclasses import dataclass, asdict
import requests
import ast

YOUR_APP_ID = "c445eedf3afd4694bce32d580a9186f8"
decoded_request = requests.get(
    "https://openexchangerates.org/api/latest.json?app_id={}".format(YOUR_APP_ID)
).content.decode("utf-8")
exchange_dict = ast.literal_eval(decoded_request)


@dataclass
class Currency:
    code: str
    name: str
    symbol: str

    def to_dict(self):
        return asdict(self)


class CURRENCIES:
    # Codes
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    ILS = "ILS"
    AUD = "AUD"

    # Define all currencies
    __ALL__ = [
        Currency(USD, "United States Dollar", "$"),
        Currency(EUR, "Euro", "€"),
        Currency(JPY, "Japanese Yen", "¥"),
        Currency(ILS, "Israeli shekel", "₪"),
        Currency(AUD, "Australian Dollar", "A$"),
    ]
    # Organize per code for convenience
    __PER_CODE__ = {currency.code: currency for currency in __ALL__}

    @classmethod
    def get_all(cls):
        return cls.__ALL__

    @classmethod
    def get_by_code(cls, code):
        if code not in cls.__PER_CODE__:
            raise Exception(f"Currency with code={code} does not exist")
        return cls.__PER_CODE__[code]

    @classmethod
    def exchange_coefficient(cls, base_currency, target_currency) -> float:
        return (
            exchange_dict["rates"][target_currency]
            / exchange_dict["rates"][base_currency]
        )
