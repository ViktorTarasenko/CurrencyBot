from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch
import seaborn as sns
import io

import imgkit

from currency_bot.view import render_error, render_help, render_currency_list, render_exchange_rate, render_history


class BytesIoMock:
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def __eq__(self, other):
        return self.data == other.data

    def seek(self, *args):
        pass


class TestView(TestCase):
    def test_render_error(self):
        bot = Mock()
        message = Mock()
        message.chat.id = 1
        render_error(bot, message, "error occured")
        bot.send_message.assert_called_with(1, "<b>error occured</b>", parse_mode="HTML")

    def test_render_help(self):
        bot = Mock()
        message = Mock()
        message.chat.id = 1
        render_help(bot, message, "$")
        bot.send_message.assert_called_with(1, "Welcome to the currency_bot! The following commands are "
                                               "available:\n\'/start\',\'/help\': \'Gives you information about the "
                                               "available commands\',\n\'/list\',\'/lst\': \'Get currency rates for "
                                               "$\',\n\'/exchange\': \'Calculate exchange using "
                                               "rates, example: /exchange 10 EUR to CAD, for USD can be: /exchange "
                                               "10$ to CAD\',\n\'/history\': \'Get chart with currency rate "
                                               "history, for example /history USD/CAD\'")

    def test_render_exchange_usd_round(self):
        bot = Mock()
        message = Mock()
        render_exchange_rate(bot, message, "USD", 10.2355)
        bot.reply_to.assert_called_with(message, "10.24$")

    def test_render_exchange_usd_int(self):
        bot = Mock()
        message = Mock()
        render_exchange_rate(bot, message, "USD", 102)
        bot.reply_to.assert_called_with(message, "102.00$")

    def test_render_exchange_round(self):
        bot = Mock()
        message = Mock()
        render_exchange_rate(bot, message, "EUR", 10.2355)
        bot.reply_to.assert_called_with(message, "10.24 EUR")

    def test_render_exchange_int(self):
        bot = Mock()
        message = Mock()
        render_exchange_rate(bot, message, "EUR", 102)
        bot.reply_to.assert_called_with(message, "102.00 EUR")

    def test_render_currency_list(self):
        rates = {"CAD": 1.3258031664, "HKD": 7.7878900102, "ISK": 128.0436996574, "PHP": 50.87954819,
                 "DKK": 6.9162114619, "HUF": 312.1007314138, "CZK": 23.2024812517, "GBP": 0.773169151,
                 "RON": 4.4477363207, "SEK": 9.7852050736, "IDR": 13765.0032404407, "INR": 71.9877789094,
                 "BRL": 4.4023701509, "RUB": 64.3903342283, "HRK": 6.8965836497, "JPY": 111.9896305898,
                 "THB": 31.6304045922, "CHF": 0.9823164522, "EUR": 0.9258402, "MYR": 4.1935006018, "BGN": 1.8107582631,
                 "TRY": 6.1226738265, "CNY": 7.0312933988, "NOK": 9.3392278493, "NZD": 1.583557078, "ZAR": 15.087954819,
                 "USD": 1.0, "MXN": 18.9966669753, "SGD": 1.4008888066, "AUD": 1.5149523192, "ILS": 3.4242199796,
                 "KRW": 1212.3414498658, "PLN": 3.9658364966}
        bot = Mock()
        message = Mock()
        message.chat.id = 1
        photo = imgkit.from_string("<ul>\r\n   \r\n    <li>CAD:1.33</li>\r\n   \r\n    <li>HKD:7.79</li>\n   \n   "
                                   " <li>ISK:128.04</li>\n   \n    <li>PHP:50.88</li>\n   \n    "
                                   "<li>DKK:6.92</li>\n   \n    <li>HUF:312.10</li>\n   \n    "
                                   "<li>CZK:23.20</li>\n   \n    <li>GBP:0.77</li>\n   \n    "
                                   "<li>RON:4.45</li>\n   \n    <li>SEK:9.79</li>\n   \n    "
                                   "<li>IDR:13765.00</li>\n   \n    <li>INR:71.99</li>\n   \n    "
                                   "<li>BRL:4.40</li>\n   \n    <li>RUB:64.39</li>\n   \n    "
                                   "<li>HRK:6.90</li>\n   \n    <li>JPY:111.99</li>\n   \n    "
                                   "<li>THB:31.63</li>\n   \n    <li>CHF:0.98</li>\n   \n    "
                                   "<li>EUR:0.93</li>\n   \n    <li>MYR:4.19</li>\n   \n    "
                                   "<li>BGN:1.81</li>\n   \n    <li>TRY:6.12</li>\n   \n    "
                                   "<li>CNY:7.03</li>\n   \n    <li>NOK:9.34</li>\n   \n    "
                                   "<li>NZD:1.58</li>\n   \n    <li>ZAR:15.09</li>\n   \n    "
                                   "<li>USD:1.00</li>\n   \n    <li>MXN:19.00</li>\n   \n    "
                                   "<li>SGD:1.40</li>\n   \n    <li>AUD:1.51</li>\n   \n    "
                                   "<li>ILS:3.42</li>\n   \n    <li>KRW:1212.34</li>\n   \n    "
                                   "<li>PLN:3.97</li>\n   \n</ul>", output_path=None)
        render_currency_list(bot, message, rates)
        bot.send_photo.assert_called_with(photo=photo, chat_id=1)

    def test_render_history(self):
        rates = {"2019-11-27": {"CAD": 1.3266418385}, "2019-11-28": {"CAD": 1.3289413903},
                 "2019-12-03": {"CAD": 1.3320386596}, "2019-12-02": {"CAD": 1.3295835979},
                 "2019-11-29": {"CAD": 1.3307230013}}

        x = [datetime.strptime(key, "%Y-%m-%d").strftime("%b,%d") for key in rates.keys()]
        y = [float(round(value[list(value.keys())[0]], 2)) for value in rates.values()]
        plot_data = {"x": x, "y": y}

        def lineplot_method_mock(data, x, y):
            def savefig(file, format):
                file.write(str(data))
                file.write(str(x))
                file.write(str(y))

            lineplot_mock = Mock()
            figure_mock = Mock()
            figure_mock.savefig = savefig
            lineplot_mock.figure = figure_mock
            return lineplot_mock

        with(patch("seaborn.lineplot", lineplot_method_mock)):
            with(patch("io.BytesIO", BytesIoMock)):
                figure = sns.lineplot(data=plot_data, x="x", y="y").figure
                file = io.BytesIO()
                figure.savefig(file, format='png')
                file.seek(0)

                bot = Mock()
                message = Mock()
                message.chat.id = 1

                render_history(bot, message, rates)
                bot.send_photo.assert_called_with(photo=file, chat_id=1)
