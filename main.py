import telebot
import requests
import json
from config import currency, TOKEN
from extensions import ConvertionException

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    bot.send_message(message.chat.id, f'{message.chat.username}, добро пожаловать в конвертер валют!\nДоступные команды:\n\
/start, /help - показать данную инструкцию;\n/values - показать список доступных валют.\n\
Для конвертации введите сообщение боту в виде:\n\
<имя валюты> <в какую валюту перевести> <количество>\nНапример, \nевро рубль 1000')

@bot.message_handler(commands=['values', ])
def send_values(message):
    text = 'Доступные валюты:'
    for s in currency.keys():
        text = '\n * '.join((text, s))
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text', ])
def currency_convert(message: telebot.types.Message):
    params = message.text.split(' ')
    try:
        if len(params) > 3:
            raise ConvertionException('Слишком много параметров')
        elif len(params) < 3:
            raise ConvertionException('Недостаточно параметров')

        curr_from, curr_to, amount = params

        if curr_from == curr_to:
            raise ConvertionException('Валюты совпадают')

        if curr_from not in currency.keys() or curr_to not in currency.keys():
            raise ConvertionException('Неизвестная валюта')
        try:
            n_amount = float(amount)
        except ValueError:
            raise ConvertionException('Количество валюты должно быть числом')

        r = requests.get(
            f'https://min-api.cryptocompare.com/data/price?fsym={currency[curr_from]}&tsyms={currency[curr_to]}')
        total_sum = json.loads(r.content)[currency[curr_to]] * float(amount)
        text = f'{amount} {currency[curr_from]} = {total_sum:.2f} {currency[curr_to]}'
        bot.reply_to(message, text)

    except ConvertionException as e:
        bot.reply_to(message,f'Ошибка ввода.\n{e}')
    except Exception as e:
        bot.reply_to(message,f'Ошибка!\n{e}')


bot.polling(none_stop=True)

