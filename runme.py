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
    txt = ''
    for cur in main_currencies:
        txt += f"{cur['full_name']}: {nbu_dict.get(cur['code'])['rate']} \n"

    return txt


nbu_rates_dict = get_nbu_rates()

# Bot instance creation
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


#  /start function handler
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Привіт. Я - бот, який допоможе тобі отримати поточні курси валют різних типів. \n'
                                'Обери будь ласка курс, який ти бажаєш отримати:')

    button_names = ["НБУ", "Міжбанк", "Курси банкiв", "Готiвковий курс"]
    keyboard = types.InlineKeyboardMarkup()
    for button_name in button_names:
        keyboard.add(types.InlineKeyboardButton(text=button_name, resize_keyboard=True))


# get user input
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'НБУ':
        answer = get_nbu_main_currencies_text(nbu_rates_dict)
    else:
        answer = 'Я цього ще не вмію, але працюю над цим :)'

    bot.send_message(message.chat.id, answer)


bot.polling(none_stop=True, interval=0)
