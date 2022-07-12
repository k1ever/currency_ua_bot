import os

from dotenv import load_dotenv
import requests
import telebot
from telebot import types

load_dotenv()


def get_nbu_rates():
    nbu_url = os.getenv('NBU_ENDPOINT')
    response = requests.request("GET", nbu_url)
    nbu_json = response.json()
    nbu_dict = {x.pop('r030'): x for x in nbu_json}

    return nbu_dict


def get_nbu_main_currencies_text(nbu_dict):
    main_currencies = [
        {'code': 840, 'name': 'USD', 'full_name': 'Долар США'},
        {'code': 978, 'name': 'EUR', 'full_name': 'Євро'},
        {'code': 826, 'name': 'GBP', 'full_name': 'Фунт стерлінгів'},
        {'code': 985, 'name': 'PLN', 'full_name': 'Злотий'}
    ]
    txt = 'Курс НБУ: \n\n'
    for cur in main_currencies:
        txt += f"{cur['full_name']}: {nbu_dict.get(cur['code'])['rate']} \n"

    return txt


nbu_rates_dict = get_nbu_rates()

# Bot instance creation
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

currency_type_buttons_callback_text = {
        'nbu': "НБУ",
        'interbank': "Міжбанк",
        'banks': "Курси банкiв",
        'cash': "Готiвковий курс"
    }
currency_type_buttons = \
    [types.InlineKeyboardButton(text=v, callback_data=k) for k, v in currency_type_buttons_callback_text.items()]


# /start function handler
@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*currency_type_buttons)
    bot.send_message(message.chat.id,
                     'Привіт. Я - бот, який допоможе тобі отримати поточні курси валют різних типів. \n'
                     'Обери, будь ласка, тип курсу, який ти бажаєш отримати:', reply_markup=keyboard)


@bot.message_handler(commands=["main"])
def ask_currency_type(message):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*currency_type_buttons)
    bot.send_message(message.chat.id,
                     'Обери будь ласка тип курсу, який ти бажаєш отримати:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "nbu":
        answer = get_nbu_main_currencies_text(nbu_rates_dict)
    else:
        answer = 'Я цього ще не вмію, але працюю над цим :)'
    bot.send_message(call.message.chat.id, answer)


bot.polling(none_stop=True, interval=0)
