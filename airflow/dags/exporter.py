import logging
import requests
import pandas as pd
from contextlib import closing
from validation import *


class ParseExchangeRate:
    BASE_URL = "https://api.exchangerate.host"

    def __init__(self, currency_from: str = "BTC", currency_to: str = "USD") -> None:
        self.currency_from = currency_from
        self.currency_to = currency_to

    def parse_to_pair(self, export_date: str, date_fmt: str) -> pd.DataFrame:
        data = [{}]
        URL = f"{self.BASE_URL}/convert?from={self.currency_from}&to={self.currency_to}"
        with closing(
            requests.Session().get(URL, params={"date": export_date})
        ) as response:
            response.raise_for_status()
            raw_data = response.json()
            data.append(
                {
                    "pair": f"{self.currency_from}/{self.currency_to}",
                    "date": validate_date(export_date, raw_data["date"], date_fmt),
                    "rate": validate_rate(raw_data["info"]["rate"]),
                }
            )
            df = pd.DataFrame(data)
            df.dropna(inplace=True)
            df['rate'] = df['rate'].astype(str)
        logging.info(f"Number of uploaded data - {df.shape[0]}")
        return df

    @classmethod
    def export_data_from_source(
        cls,
        date_fmt: str,
        currency_from: str = "BTC",
        currency_to: str = "USD",
        export_date: str = None,
    ):
        er = cls(currency_from, currency_to)
        return er.parse_to_pair(export_date, date_fmt)
