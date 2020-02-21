import telebot
from telebot.util import extract_arguments

from currency_bot.data import CurrencyService
from currency_bot.view import render_currency_list
from currency_bot.view import render_exchange_rate
from currency_bot.view import render_history
import datetime

API_TOKEN = "1071125423:AAEdrDqmDvz3H08-3qbH4sjXBY_ysaZ21P8"
BASE_CURRENCY = "USD"
HISTORY_N_DAYS = 7

bot = telebot.TeleBot(API_TOKEN)

currency_service = CurrencyService(lambda: datetime.datetime.now())


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['list', 'lst'])
def currency_list(message):
    render_currency_list(bot, message, currency_service.rates_list(BASE_CURRENCY))


@bot.message_handler(commands=['exchange'], regexp="\d+\s[A-Z]{3}\sto\s[A-Z]{3}")
def exchange(message):
    amount, base_currency, __, target_currency = extract_arguments(message.text).split()
    result = currency_service.exchange(base_currency, target_currency, amount)
    render_exchange_rate(bot, message, target_currency, result)


@bot.message_handler(commands=['history'], regexp="[A-Z]{3}\/[A-Z]{3}")
def history(message):
    base_currency, target_currency = extract_arguments(message.text).split("/")
    render_history(bot, message, currency_service.history(HISTORY_N_DAYS, base_currency, target_currency))


def main():
    bot.polling()


if __name__ == '__main__':
    main()