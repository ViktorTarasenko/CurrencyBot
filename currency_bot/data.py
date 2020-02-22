from datetime import timedelta

import requests


class CurrencyService:
    SYNC_TIME_MINUTES = 10
    HISTORY_URL = "https://api.exchangeratesapi.io/history"
    RATES_URL = "https://api.exchangeratesapi.io/latest"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, time_source):
        self.time_source = time_source
        self.rates = None
        self.last_sync_time = None

    def rates_list(self, base_currency):
        self.__load_rates_list(base_currency)
        return self.rates

    def exchange(self, base_currency, target_currency, amount):
        self.__load_rates_list(base_currency)
        if base_currency not in self.rates:
            raise CurrencyNotFound(base_currency)
        if target_currency not in self.rates:
            raise CurrencyNotFound(target_currency)
        return amount * (self.rates[target_currency] / self.rates[base_currency])

    def history(self, n_days, base_currency, target_currency):
        self.__load_rates_list(base_currency)
        if base_currency not in self.rates:
            raise CurrencyNotFound(base_currency)
        if target_currency not in self.rates:
            raise CurrencyNotFound(target_currency)
        end_date = self.time_source().date()
        start_date = end_date + timedelta(days=-n_days)
        request_params = {"start_at": start_date.strftime(self.DATE_FORMAT),
                          "end_at": end_date.strftime(self.DATE_FORMAT),
                          "base": base_currency, "symbols": target_currency}
        response = requests.get(self.HISTORY_URL, params=request_params);
        response.raise_for_status()
        rates = response.json()["rates"]
        if not rates:
            raise EmptyCurrencyHistory
        return rates

    def __load_rates_list(self, base_currency):
        if (not self.rates) or (not self.last_sync_time) or (
                (self.time_source() - self.last_sync_time).seconds / 60 >= self.SYNC_TIME_MINUTES):
            response = requests.get(self.RATES_URL, params={"base": base_currency})
            response.raise_for_status()
            self.rates = response.json()["rates"]
            self.last_sync_time = self.time_source()


class CurrencyNotFound(Exception):
    def __init__(self, currency):
        self.currency = currency


class EmptyCurrencyHistory(Exception):
    pass
