import io

import imgkit


import seaborn as sns
from jinja2 import Environment, PackageLoader


def render_currency_list(bot, original_message, response_data):
    response_html = render_template("currency_list.html", rates=response_data["rates"])
    bot.send_photo(photo=imgkit.from_string(response_html, output_path=None), chat_id=original_message.chat.id)


def render_exchange_rate(bot, original_message, target_currency, response_data):
    bot.reply_to(original_message, "{0:d} {1:s}".format(response_data, target_currency))


def render_history(bot, original_message, response_data):
    dates = [key for key in response_data["rates"].keys()]
    rates = [value[list(value.keys())[0]] for value in response_data["rates"].values()]
    plot_data = {"x": dates, "y": rates}
    figure = sns.lineplot(data=plot_data, x="x", y="y").figure
    file = io.BytesIO()
    figure.savefig(file, format='png')
    file.seek(0)
    bot.send_photo(photo=file, chat_id=original_message.chat.id)


def render_template(path, **kwargs):
    env = Environment(loader=PackageLoader('currency_bot', 'templates'))
    template = env.get_template(path)
    rendered = template.render(kwargs)
    return rendered
