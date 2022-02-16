from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import List, Dict

from currencies import Currency, CURRENCIES
from markets import Market, MARKETS


@dataclass
class Listing:
    title: str
    base_price: float
    currency: Currency
    market: Market
    host_name: str
    calendar: list

    def to_dict(self):
        return asdict(self)


class LISTING:

    calendar = [date.today() + timedelta(days=x) for x in range(365)]

    __ALL__ = [
        Listing(
            "Comfortable Room In Cozy Neighborhood",
            867,
            CURRENCIES.USD,
            MARKETS.SAN_FRANCISCO,
            "John Smith",
            calendar,
        ),
        Listing(
            "Duplex Room In City Center",
            650,
            CURRENCIES.EUR,
            MARKETS.LISBON,
            "Tim Jones",
            calendar,
        ),
        Listing(
            "Private Villa In  Village",
            1200,
            CURRENCIES.JPY,
            MARKETS.TOKYO,
            "Billy Roberts",
            calendar,
        ),
        Listing(
            "Apartment In  Sub",
            1200,
            CURRENCIES.ILS,
            MARKETS.JERUSALEM,
            "John Rogers",
            calendar,
        ),
    ]

    @classmethod
    def get_all(cls):
        return cls.__ALL__

    @classmethod
    def base_price_calc(cls, market, base_price, calendar_date):

        if (market == MARKETS.LISBON or market == MARKETS.PARIS) and (
            calendar_date.weekday() == 5 or calendar_date.weekday() == 6
        ):
            base_price = base_price * 1.5

        if market == MARKETS.SAN_FRANCISCO and calendar_date.weekday() == 2:
            base_price = base_price * 0.7

        if (
            not (
                market == MARKETS.SAN_FRANCISCO
                or market == MARKETS.LISBON
                or market == MARKETS.PARIS
            )
            and calendar_date.weekday() == 4
        ):
            base_price = base_price * 1.25

        return base_price

    @classmethod
    def comparison_function(
        cls, listings_list, comparison_type, threshold_price
    ) -> List[Dict]:
        filtered_element = []
        for listing_item in listings_list:
            if comparison_type == "gt" and listing_item["base_price"] > threshold_price:
                filtered_element.append(listing_item)
            elif (
                comparison_type == "gte"
                and listing_item["base_price"] >= threshold_price
            ):
                filtered_element.append(listing_item)
            elif (
                comparison_type == "lt" and listing_item["base_price"] < threshold_price
            ):
                filtered_element.append(listing_item)
            elif (
                comparison_type == "lte"
                and listing_item["base_price"] <= threshold_price
            ):
                filtered_element.append(listing_item)
            elif (
                comparison_type == "e" and listing_item["base_price"] == threshold_price
            ):
                filtered_element.append(listing_item)

        return filtered_element

    @classmethod
    def currency_selector(cls, market) -> str:
        if market == MARKETS.SAN_FRANCISCO:
            return CURRENCIES.USD
        elif market == (MARKETS.LISBON or MARKETS.PARIS):
            return CURRENCIES.EUR
        elif market == MARKETS.JERUSALEM:
            return CURRENCIES.ILS
        elif market == MARKETS.TOKYO:
            return CURRENCIES.JPY
        elif market == MARKETS.BRISBANE:
            return CURRENCIES.AUD
