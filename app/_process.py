import json
from time import sleep
from threading import Thread

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ._constants import TOKEN, YANDEX_LINK, WELCOME_TEXT, TG_MESSAGE
from utils import configure_logger

logger = configure_logger()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def thread_main(message):
    Thread(target=main_message, args=(message,)).start()
    Thread(target=send_delayed_message, args=(message,)).start()


def main_message(message):
    logger.info(print(f"{'user': {message.from_user}, 'id': {message.chat.id}, 'chat': {message.chat}})"))
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT.format(message.from_user),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Скачать", url=YANDEX_LINK)],
            ],
        ),
    )


def send_delayed_message(message):
    sleep(15)

    bot.send_message(
        message.chat.id,
        TG_MESSAGE,
        parse_mode="html",
    )
