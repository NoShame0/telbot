"""
The main logic module of the bot.
"""

import google_api
import telebot
from telebot import types
import datetime
import timechecker
from config import config

bot = telebot.TeleBot('2136810130:AAHO_POj-WV0GuqTOJ1iqU9s38o86ZELX6A')


# Launching a bot for a user and generating chat data in config
@bot.message_handler(commands=['start'])
def start_message(message):

    config[message.chat.id] = {
        'first_name': message.from_user.first_name,
        'start_message': True,
        'start': False,
        'interval': None,
        'time_last_message': None,
    }

    bot.send_message(message.chat.id, f"👋Привет, {message.from_user.first_name}!👋\n"
                                      f"📈Я тестовый бот, который поможет тебе освоить ЯП Python.\n"
                                      '📁Нажми на кнопку "Видеоуроки", чтобы получить доступ к видеоурокам.\n'
                                      '📘Для изучения дополнительных материалов нажми кнопку '
                                      '"Дополнительные материалы".\n'
                                      '🕐Прежде чем начнем работу, укажи, как часто необходимо мне напоминать тебе '
                                      'о занятиях?\n Введи число, обозначающее интервал в часах. Если что, ты всегда '
                                      'можешь поменять его с помощью кнопки "Настройки интервалов напоминания"')


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_info = config[message.chat.id]

    chat_info['start'] = False
    chat_info['interval'] = None
    chat_info['time_last_message'] = None
    chat_info['start_message'] = False

    bot.send_message(message.chat.id, "Надеюсь, мне удалось тебе помочь!\n"
                                      "Если захочешь снова возобновить обучение, напиши команду /start.\n"

                                      "Я буду очень рад с тобой еще поработать!")


# Input Message Handler
@bot.message_handler(content_types=['text'])
def func(message):
    # Relevant when restarting the bot
    if message.chat.id not in config:
        bot.send_message(message.chat.id, 'Для запуска бота введите команду /start')
    else:

        # Checking for chat registration is necessary to prevent a config error without a set reminder interval
        if config[message.chat.id]['start']:

            gs = google_api.GoogleSheet()

            if message.text == "Дополнительные материалы":

                markup_message = types.InlineKeyboardMarkup(row_width=1)

                btns = []
                for title, url in gs.read_data('List!C:D'):
                    btns.append(types.InlineKeyboardButton(title, url=url))
                markup_message.add(*btns)

                bot.send_message(message.chat.id, f"{message.from_user.first_name}, "
                                                  f"здесь ты можешь самостоятельно "
                                                  f"изучить материал и попрактиковаться ⬇️",
                                 reply_markup=markup_message)

            elif message.text == "Видеоуроки":
                markup_message = types.InlineKeyboardMarkup(row_width=1)
                btns = []

                for title, url in gs.read_data('List!A:B'):
                    btns.append(types.InlineKeyboardButton(title, url=url))

                markup_message.add(*btns)
                bot.send_message(message.chat.id,
                                 f"{message.from_user.first_name}, "
                                 f"🎬 переходи по ссылкам ниже для просмотра видеуроков ⬇️",
                                 reply_markup=markup_message)

            elif message.text == "Настройка интервалов напоминания":
                config[message.chat.id]['start'] = False
                bot.send_message(message.chat.id, "Установка нового интервала напоминания.\nВведи новое число часов! 🕐")

            else:
                bot.send_message(message.chat.id, "😢 Прости, я тебя не понимаю. 😢")

            # Setting the time of the last message after which the bot will remind user about the training
            now = datetime.datetime.now()
            config[message.chat.id]['time_last_message'] = now - datetime.timedelta(microseconds=now.microsecond)

        elif config[message.chat.id]['start_message']:
            # Checkin int number
            try:
                interval = int(message.text)
                if interval <= 0:
                    raise ValueError
            except ValueError:
                bot.send_message(message.chat.id, "🧐 Не удалось установить интервал. 🧐\n"
                                                  "Попробуй еще раз! (Введи одно число) ")
            else:

                # Generating main menu after successful converting
                markup_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)

                btn1 = types.KeyboardButton("Видеоуроки")
                btn2 = types.KeyboardButton("Дополнительные материалы")
                btn3 = types.KeyboardButton("Настройка интервалов напоминания")
                markup_main_menu.add(btn1, btn2, btn3)

                bot.send_message(message.chat.id, "📆 Отлично! Теперь ты точно ничего не забудешь! 📆\n"
                                                  f" ✅ Каждые {interval} "
                                                  f"часов я буду напоминать тебе об обучении ✅\n"
                                                  "📊 А теперь давай учиться! 📊\n", reply_markup=markup_main_menu)

                config[message.chat.id]['start'] = True
                config[message.chat.id]['interval'] = interval

            now = datetime.datetime.now()
            config[message.chat.id]['time_last_message'] = now - datetime.timedelta(microseconds=now.microsecond)
        else:
            bot.send_message(message.chat.id, 'Для запуска бота введите команду /start')


timechecker.TimeChecker(bot).start()

bot.polling(none_stop=True, interval=0)
