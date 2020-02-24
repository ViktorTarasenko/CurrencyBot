import re
from decimal import Decimal

import requests
import telebot
from telebot.util import extract_arguments

from currency_bot.data import CurrencyService, NoDataAvailable, CurrencyNotFound, MemoryObjectStorage
from currency_bot.view import render_currency_list, render_help, render_error
from currency_bot.view import render_exchange_rate
from currency_bot.view import render_history
import datetime
import logging

API_TOKEN = "<put you token here>"
BASE_CURRENCY = "USD"
HISTORY_N_DAYS = 7

bot = telebot.TeleBot(API_TOKEN)

currency_service = CurrencyService(datetime.datetime, requests, MemoryObjectStorage(), BASE_CURRENCY)


def handle_common_error(e, message, bot):
    render_error(bot, message, "Unknown error occurred!")
    logging.exception(e)


@bot.message_handler(commands=['list', 'lst'])
def currency_list(message):
    try:
        render_currency_list(bot, message, currency_service.rates_list())
    except Exception as e:
        handle_common_error(e, message, bot)


@bot.message_handler(commands=['exchange'], regexp="\d+([.]\d{1,2})?\$\sto\s[A-Z]{3}|\d+([.]\d{1,2})?\s[A-Z]{3}\sto\s[A-Z]{3}")
def exchange(message):
    try:
        args = extract_arguments(message.text)
        if re.compile("\d+\$\sto\s[A-Z]{3}").match(args):
            base_currency = 'USD'
            args = args.replace("$", "")
            amount, __, target_currency = args.split()
        else:
            amount, base_currency, __, target_currency = args.split()
        amount = Decimal(amount)
        result = currency_service.exchange(base_currency, target_currency, amount)
        render_exchange_rate(bot, message, target_currency, result)
    except CurrencyNotFound as e:
        logging.exception(e)
        render_error(bot, message, "No currency {0}!".format(e.currency))
    except Exception as e:
        handle_common_error(e, message, bot)


@bot.message_handler(commands=['history'], regexp="[A-Z]{3}\/[A-Z]{3}")
def history(message):
    try:
        base_currency, target_currency = extract_arguments(message.text).split("/")
        render_history(bot, message, currency_service.history(HISTORY_N_DAYS, base_currency, target_currency))
    except NoDataAvailable as e:
        render_error(bot, message, "Could not load data!")
        logging.exception(e)
    except CurrencyNotFound as e:
        logging.exception(e)
        render_error(bot, message, "No currency {0}!".format(e.currency))
    except Exception as e:
        handle_common_error(e, message, bot)


@bot.message_handler()
def handle_default(message):
    try:
        render_help(bot, message, BASE_CURRENCY)
    except Exception as e:
        handle_common_error(e, message, bot)
