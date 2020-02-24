import unittest
from decimal import Decimal
from unittest import TestCase
from unittest.mock import Mock, MagicMock
from datetime import datetime

from currency_bot.data import CurrencyService, CurrencyNotFound


class TestCurrencyService(TestCase):
    def test_history_ok(self):
        history = {"2019-11-27": {"CAD": 1.3266418385}, "2019-11-28": {"CAD": 1.3289413903},
                   "2019-12-03": {"CAD": 1.3320386596}, "2019-12-02": {"CAD": 1.3295835979},
                   "2019-11-29": {"CAD": 1.3307230013}}
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                 "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                 "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                 "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}
        rates_later = {"CAD": 2.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                       "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                       "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                       "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                       "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                       "BGN": 1.8107582631,
                       "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                       "ZAR": 15.087954819,
                       "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                       "ILS": 3.4242199796,
                       "KRW": 1212.3414498658, "PLN": 3.9658364966}
        datetime_mock = Mock()
        requests_mock = Mock()
        get_mock = Mock()
        json_mock = MagicMock()
        json_mock.__getitem__.side_effect = [rates, history, history, rates_later, history]

        requests_mock.get.return_value = get_mock
        get_mock.json.return_value = json_mock
        datetime_mock.now.side_effect = [datetime(2020, 2, 24, 0, 0, 0, 0), datetime(2020, 2, 24, 0, 0, 0, 0),
                                         datetime(2020, 2, 24, 0, 9, 59, 59), datetime(2020, 2, 24, 0, 9, 59, 59),
                                         datetime(2020, 2, 24, 0, 10, 0, 0), datetime(2020, 2, 24, 0, 10, 0, 0)]
        object_storage_mock = MagicMock()
        object_storage_mock.__getitem__.side_effect = [rates, rates, rates, rates, rates_later, rates_later]
        object_storage_mock.__contains__.side_effect = [False, True, True]
        currency_service = CurrencyService(datetime_mock, requests_mock, object_storage_mock, "USD")
        result = currency_service.history(8, 'USD', 'CAD')
        object_storage_mock.__setitem__.assert_called_with("rates", rates)
        requests_mock.get.assert_any_call(CurrencyService.HISTORY_URL, params={"start_at": "2020-02-17",
                                                                               "end_at": "2020-02-24",
                                                                               "base": "USD", "symbols": "CAD"})
        assert result == history
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time less than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.history(8, 'USD', 'CAD')
        object_storage_mock.__setitem__.assert_not_called()
        requests_mock.get.assert_any_call(CurrencyService.HISTORY_URL, params={"start_at": "2020-02-17",
                                                                               "end_at": "2020-02-24",
                                                                               "base": "USD", "symbols": "CAD"})
        assert result == history
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time more than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.history(8, 'USD', 'CAD')
        object_storage_mock.__setitem__.assert_called_with("rates", rates_later)
        requests_mock.get.assert_any_call(CurrencyService.HISTORY_URL, params={"start_at": "2020-02-17",
                                                                               "end_at": "2020-02-24",
                                                                               "base": "USD", "symbols": "CAD"})
        assert result == history
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 10, 0, 0)

    def test_history_currency_not_found_first_currency(self):
        history = {"2019-11-27": {"CAD": 1.3266418385}, "2019-11-28": {"CAD": 1.3289413903},
                   "2019-12-03": {"CAD": 1.3320386596}, "2019-12-02": {"CAD": 1.3295835979},
                   "2019-11-29": {"CAD": 1.3307230013}}
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                 "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                 "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                 "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}
        datetime_mock = Mock()
        requests_mock = Mock()
        get_mock = Mock()
        json_mock = MagicMock()
        json_mock.__getitem__.side_effect = [rates, history, rates, history]

        requests_mock.get.return_value = get_mock
        get_mock.json.return_value = json_mock
        datetime_mock.now.side_effect = [datetime(2020, 2, 24, 0, 0, 0, 0), datetime(2020, 2, 24, 0, 0, 0, 0)]
        object_storage_mock = MagicMock()
        object_storage_mock.__getitem__.side_effect = [rates, rates, rates, rates]
        currency_service = CurrencyService(datetime_mock, requests_mock, object_storage_mock, "USD")
        with(self.assertRaises(CurrencyNotFound)):
            currency_service.history(8, 'USF', 'CAD')
        with(self.assertRaises(CurrencyNotFound)):
            currency_service.history(8, 'CAD', 'USF')

    def test_exchange_ok(self):
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                 "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                 "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                 "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}
        for key, value in rates.items():
            rates[key] = Decimal(value)
        rates_later = {"CAD": 2.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                       "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                       "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                       "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                       "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                       "BGN": 1.8107582631,
                       "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                       "ZAR": 15.087954819,
                       "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                       "ILS": 3.4242199796,
                       "KRW": 1212.3414498658, "PLN": 3.9658364966}
        for key, value in rates_later.items():
            rates_later[key] = Decimal(value)
        datetime_mock = Mock()
        requests_mock = Mock()
        get_mock = Mock()
        json_mock = MagicMock()
        json_mock.__getitem__.side_effect = [rates, rates_later]

        requests_mock.get.return_value = get_mock
        get_mock.json.return_value = json_mock
        datetime_mock.now.side_effect = [datetime(2020, 2, 24, 0, 0, 0, 0),
                                         datetime(2020, 2, 24, 0, 9, 59, 59),
                                         datetime(2020, 2, 24, 0, 10, 0, 0)]
        object_storage_mock = MagicMock()
        object_storage_mock.__getitem__.side_effect = [rates, rates, rates, rates, rates, rates, rates, rates,
                                                       rates_later, rates_later, rates_later, rates_later]
        object_storage_mock.__contains__.side_effect = [False, True, True]
        currency_service = CurrencyService(datetime_mock, requests_mock, object_storage_mock, "USD")
        result = currency_service.exchange("USD", "CAD", Decimal(10.25))
        object_storage_mock.__setitem__.assert_called_with("rates", rates)

        assert (result == Decimal("13.59"))
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time less than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.exchange("USD", "CAD", Decimal(10.25))
        object_storage_mock.__setitem__.assert_not_called()

        assert (result == Decimal("13.59"))
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time more than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.exchange("USD", "CAD", Decimal(10.25))
        object_storage_mock.__setitem__.assert_called_with("rates", rates_later)

        assert (result == Decimal("23.84"))
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 10, 0, 0)

    def test_exchange_currency_not_found(self):
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                 "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                 "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                 "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}

        datetime_mock = Mock()
        requests_mock = Mock()
        get_mock = Mock()
        json_mock = MagicMock()
        json_mock.__getitem__.side_effect = [rates, rates]

        requests_mock.get.return_value = get_mock
        get_mock.json.return_value = json_mock
        datetime_mock.now.side_effect = [datetime(2020, 2, 24, 0, 0, 0, 0), datetime(2020, 2, 24, 0, 0, 0, 0)]
        object_storage_mock = MagicMock()
        object_storage_mock.__getitem__.side_effect = [rates, rates, rates, rates, rates, rates, rates, rates]
        currency_service = CurrencyService(datetime_mock, requests_mock, object_storage_mock, "USD")
        with(self.assertRaises(CurrencyNotFound)):
            currency_service.exchange("USF", "CAD", Decimal(10.25))
        with(self.assertRaises(CurrencyNotFound)):
            currency_service.exchange("USD", "CAF", Decimal(10.25))

    def test_list_ok(self):
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                 "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                 "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                 "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}
        rates_later = {"CAD": 2.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                       "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                       "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                       "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                       "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018,
                       "BGN": 1.8107582631,
                       "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078,
                       "ZAR": 15.087954819,
                       "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192,
                       "ILS": 3.4242199796,
                       "KRW": 1212.3414498658, "PLN": 3.9658364966}
        datetime_mock = Mock()
        requests_mock = Mock()
        get_mock = Mock()
        json_mock = MagicMock()
        json_mock.__getitem__.side_effect = [rates, rates_later]

        requests_mock.get.return_value = get_mock
        get_mock.json.return_value = json_mock
        datetime_mock.now.side_effect = [datetime(2020, 2, 24, 0, 0, 0, 0),
                                         datetime(2020, 2, 24, 0, 9, 59, 59),
                                         datetime(2020, 2, 24, 0, 10, 0, 0)]
        object_storage_mock = MagicMock()
        object_storage_mock.__getitem__.side_effect = [rates, rates, rates_later]
        object_storage_mock.__contains__.side_effect = [False, True, True]
        currency_service = CurrencyService(datetime_mock, requests_mock, object_storage_mock, "USD")
        result = currency_service.rates_list()
        object_storage_mock.__setitem__.assert_called_with("rates", rates)
        requests_mock.get.assert_any_call(CurrencyService.RATES_URL, params={"base": "USD"})
        assert result == rates
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time less than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.rates_list()
        object_storage_mock.__setitem__.assert_not_called()
        requests_mock.get.assert_not_called()
        assert result == rates
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 0, 0, 0)

        # shifting time more than ten minutes, see side_effect above
        object_storage_mock.reset_mock()
        requests_mock.reset_mock()
        result = currency_service.rates_list()
        object_storage_mock.__setitem__.assert_called_with("rates", rates_later)
        requests_mock.get.assert_any_call(CurrencyService.RATES_URL, params={"base": "USD"})
        assert result == rates_later
        assert currency_service.last_sync_time == datetime(2020, 2, 24, 0, 10, 0, 0)


if __name__ == '__main__':
    unittest.main()
