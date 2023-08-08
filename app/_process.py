from threading import Thread

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ._constants import SUB_TEXT, WELCOME_TEXT
from ._users import UsersProcess, ALLOWED_USER_TYPES
from utils import configure_logger
from settings import settings

logger = configure_logger()
bot = telebot.TeleBot(settings.BOT_TOKEN)
USERS = UsersProcess()


@bot.message_handler(commands=["start"])
def thread_main(message):
    Thread(target=main_message, args=(message,)).start()


@bot.message_handler(commands=["whoami"])
def thread_whoami(message):
    Thread(target=whoami, args=(message,)).start()


@bot.message_handler(commands=[settings.ADMIN_CODE])
def thread_admin(message):
    Thread(target=admin_panel, args=(message,)).start()


def admin_panel(message):
    if USERS.check_admin(message.chat.id):
        bot.send_message(
            message.chat.id,
            "Салют босс, на какую категорию рассылаем?",
            reply_markup=InlineKeyboardMarkup(
                [
                    InlineKeyboardButton(text=name, callback_data=name)
                    for name in ALLOWED_USER_TYPES + ["all"]
                ],
            ),
        )
    else:
        logger.info(
            f"Invalid admin access attempt by{message.chat.id} - {message.from_user}"
        )


def whoami(message):
    bot.send_message(
        message.chat.id,
        USERS.get_user_type(message.chat.id),
    )


def main_message(message):
    logger.info(f"Message from: {message.from_user} | {message.chat.id}")

    USERS.add_user(chat_id=message.chat.id, user_type="new")
    bot.send_message(
        message.chat.id,
        WELCOME_TEXT.format(message.from_user),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Подписаться", callback_data="do_subscribe"
                    )
                ],
            ],
        ),
    )


@bot.callback_query_handler(func=lambda call: call.data in ALLOWED_USER_TYPES)
def handle_subscribe_callback(call):
    chat_id = call.from_user.id
    ...


@bot.callback_query_handler(func=lambda call: call.data == "do_subscribe")
def handle_subscribe_callback(call):
    # Extract the user's unique identifier from the callback query object
    chat_id = (
        call.from_user.id
    )  # You can use call.message.chat.id if you've stored it in the initial function
    USERS.add_user(chat_id=chat_id, user_type="involved")

    # Send a confirmation message back to the user
    bot.send_message(
        chat_id,
        SUB_TEXT,
    )
