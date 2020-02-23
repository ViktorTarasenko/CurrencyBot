from datetime import datetime
import io

import imgkit

import seaborn as sns
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('currency_bot', 'templates'))


def render_error(bot, original_message, error_message):
    response_html = render_template("error.html", error_message=error_message)
    bot.send_message(original_message.chat.id, response_html, parse_mode="HTML")


def render_help(bot, original_message, base_currency):
    response_html = render_template("help.html", base_currency=base_currency)
    bot.send_message(original_message.chat.id, response_html)


def render_currency_list(bot, original_message, rates):
    response_html = render_template("currency_list.html", rates=rates)
    bot.send_photo(photo=imgkit.from_string(response_html, output_path=None), chat_id=original_message.chat.id)


def render_exchange_rate(bot, original_message, target_currency, amount):
    if target_currency == "USD":
        bot.reply_to(original_message, "{0:.2f}$".format(amount))
    else:
        bot.reply_to(original_message, "{0:.2f} {1:s}".format(amount, target_currency))


def render_history(bot, original_message, rates):
    dates = [datetime.strptime(key, "%Y-%m-%d").strftime("%b,%d") for key in rates.keys()]
    rates = [float(round(value[list(value.keys())[0]], 2)) for value in rates.values()]
    plot_data = {"x": dates, "y": rates}
    figure = sns.lineplot(data=plot_data, x="x", y="y").figure
    file = io.BytesIO()
    figure.savefig(file, format='png')
    file.seek(0)
    bot.send_photo(photo=file, chat_id=original_message.chat.id)


def render_template(path, **kwargs):
    template = env.get_template(path)
    rendered = template.render(kwargs)
    return rendered
