import telebot

from ._constants import TOKEN
from utils import configure_logger

logger = configure_logger()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def func(message):
    bot.send_message(
        message.chat.id,
        "Здарова, {0.first_name} сейчас скину ссылку на яндекс диск".format(
            message.from_user, bot.get_me()
        ),
        parse_mode="html",
    )
    bot.send_message(
        message.chat.id,
        "ссылка ".format(message.from_user, bot.get_me()),
        parse_mode="html",
    )
    bot.send_message(
        message.chat.id,
        "А также ты должен подписаться на телеграм канал Осы \nссылка на тг канал".format(
            message.from_user, bot.get_me()
        ),
        parse_mode="html",
    )


@bot.message_handler(content_types=["text"])
def ccccc(message):
    bot.send_message(
        message.chat.id,
        "все пока я спать".format(message.from_user, bot.get_me()),
        parse_mode="html",
    )
