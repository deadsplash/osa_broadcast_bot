import telebot

from ._constants import TOKEN, YANDEX_LINK, WELCOME_TEXT, TG_MESSAGE
from utils import configure_logger

logger = configure_logger()
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def func(message):
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT.format(
            message.from_user, YANDEX_LINK
        ),
        parse_mode="html",
    )
    # bot.send_message(
    #     message.chat.id,
    #     YANDEX_LINK,
    #     parse_mode="html",
    # )
    bot.send_message(
        message.chat.id,
        TG_MESSAGE,
        parse_mode="html",
    )


@bot.message_handler(content_types=["text"])
def ccccc(message):
    bot.send_message(
        message.chat.id,
        "все пока я спать".format(message.from_user, bot.get_me()),
        parse_mode="html",
    )
