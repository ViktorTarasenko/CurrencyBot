import decimal
from datetime import timedelta


class CurrencyService:
    SYNC_TIME_MINUTES = 10
    HISTORY_URL = "https://api.exchangeratesapi.io/history"
    RATES_URL = "https://api.exchangeratesapi.io/latest"
    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, datetime, requests, object_storage):
        self.datetime = datetime
        self.requests = requests
        self.last_sync_time = None
        self.object_storage = object_storage

    def rates_list(self, base_currency):
        self.__load_rates_list(base_currency)
        return self.object_storage["rates"]

    def exchange(self, base_currency, target_currency, amount):
        self.__load_rates_list(base_currency)
        if base_currency not in self.object_storage["rates"]:
            raise CurrencyNotFound(base_currency)
        if target_currency not in self.object_storage["rates"]:
            raise CurrencyNotFound(target_currency)
        result = amount * (self.object_storage["rates"][target_currency] / self.object_storage["rates"][base_currency])
        return round(result, 2)

    def history(self, n_days, base_currency, target_currency):
        self.__load_rates_list(base_currency)
        if base_currency not in self.object_storage["rates"]:
            raise CurrencyNotFound(base_currency)
        if target_currency not in self.object_storage["rates"]:
            raise CurrencyNotFound(target_currency)
        end_date = self.datetime.now().date()
        start_date = end_date + timedelta(days=-n_days + 1)
        request_params = {"start_at": start_date.strftime(self.DATE_FORMAT),
                          "end_at": end_date.strftime(self.DATE_FORMAT),
                          "base": base_currency, "symbols": target_currency}
        response = self.requests.get(self.HISTORY_URL, params=request_params)
        response.raise_for_status()
        rates = response.json(parse_float=decimal.Decimal)["rates"]
        if not rates:
            raise EmptyCurrencyHistory
        return rates

    def __load_rates_list(self, base_currency):
        now = self.datetime.now()
        if ("rates" not in self.object_storage) or (not self.last_sync_time) or (
                (now - self.last_sync_time).seconds / 60 >= self.SYNC_TIME_MINUTES):
            response = self.requests.get(self.RATES_URL, params={"base": base_currency})
            response.raise_for_status()
            self.object_storage["rates"] = response.json(parse_float=decimal.Decimal)["rates"]
            self.last_sync_time = now


# for simpliсity in memory realization provided, but can be made as persistent, for example using shelve
class MemoryObjectStorage:
    def __init__(self):
        self.objects_dict = {}

    def __getitem__(self, item):
        return self.objects_dict[item]

    def __setitem__(self, key, value):
        self.objects_dict[key] = value

    def __contains__(self, key):
        return key in self.objects_dict


class CurrencyNotFound(Exception):
    def __init__(self, currency):
        self.currency = currency


class EmptyCurrencyHistory(Exception):
    pass
