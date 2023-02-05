import logging
import requests
import pandas as pd
from contextlib import closing
from typing import Optional


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

    @classmethod
    def validate_date(export_date: str, data_date: str, date_frmt: str) -> Optional[str]:
        """
        Checking the correctness of the date received from the api
        and recording this data in accordance with the selected data format
        :param export_date: date of data upload specified by the user
        :param data_date: date when data was uploaded from the api
        :param date_fmt: the data format specified by the user (date: %Y-%m-%d, datetime: %Y-%m-%dT%H:%m:%S)
        """
        _export_date = export_date.split("T")[0]

        # create datetime
        _raw_export_datetime = export_date.split(".")[0].split("T")
        _export_datetime = " ".join(_raw_export_datetime)

        if _export_date == data_date:
            date_formats = {"date": _export_date, "datetime": _export_datetime}
            return date_formats[date_frmt]
        raise ValueError("The dates don't match")

    @classmethod
    def validate_rate(rate: float) -> Optional[float]:
        """
        Checking the correctness of the rate received from the api
        :param rate: rate when data was uploaded from the api
        """
        if isinstance(rate, float):
            return rate
        raise ValueError("Rate is not a float type number")
