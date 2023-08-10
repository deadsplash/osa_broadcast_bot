from threading import Thread
from typing import List
import pickle

import telebot
from telebot.util import antiflood
from telebot.handler_backends import State, StatesGroup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ._constants import SUB_TEXT, WELCOME_TEXT
from ._users import UsersProcess, ALLOWED_USER_TYPES
from utils import configure_logger
from settings import settings

logger = configure_logger()
bot = telebot.TeleBot(settings.BOT_TOKEN)
USERS = UsersProcess()

authorized_chat_ids = ["104694046"]
broadcast_data = {}


class AnswerState(StatesGroup):
    broadcast_type = State()


class AdminBroadcast:
    def __init__(self, message: Message, broadcast_group: str):
        self.message: Message = message
        self.broadcast_group: str = broadcast_group

        self.broadcast_type: str = self.define_broadcast_type()
        logger.info(f"Init {self.broadcast_type} broadcast")
        self.users_for_broadcast: List[str] = USERS.get_users_for_broadcast(
            broadcast_group
        )

    def _antiflood(self, **kwargs):

        try:
            antiflood(**kwargs)
        except Exception as ex:
            logger.error(f"Error sending data: {ex}")

    def broadcast(self):
        logger.info("Start broadcast...")
        for user in self.users_for_broadcast:

            if self.broadcast_type == "text":
                self._antiflood(
                    function=bot.send_message, chat_id=user, text=self.message.text
                )

            elif self.broadcast_type == "photo":
                with open("ph.pck", "wb") as f:
                    pickle.dump(self.message, f)
                self._antiflood(
                    function=bot.send_photo,
                    chat_id=user,
                    photo=max(self.message.photo, key=lambda x: x.file_size).file_id,
                    caption=self.message.caption,
                )

            elif self.broadcast_type == "video":
                self._antiflood(
                    function=bot.send_video,
                    chat_id=user,
                    video=self.message.photo,
                    caption=self.message.caption,
                )

            elif self.broadcast_type == "voice":
                self._antiflood(
                    function=bot.send_voice, chat_id=user, voice=self.message.voice
                )

            elif self.broadcast_type == "video_note":
                self._antiflood(
                    function=bot.send_video_note,
                    chat_id=user,
                    data=self.message.video_note,
                )

        logger.info("Broadcast finished")

    def define_broadcast_type(self):
        """Define broadcast type for further rules"""

        print(self.message)

        text = self.message.text
        photo = self.message.photo
        video = self.message.video
        voice = self.message.voice
        video_note = self.message.video_note

        if text:
            return "text"

        if photo:
            # if self.message.caption:
            #     return "photo+text"
            return "photo"

        if video:
            # if self.message.caption:
            #     return "video+text"
            return "video"

        if voice:
            return "voice"

        if video_note:
            return "video_note"

    @classmethod
    def run(cls, message: Message, broadcast_group: str):
        etl = AdminBroadcast(message, broadcast_group)
        etl.broadcast()


@bot.message_handler(commands=["start"])
def thread_main(message):
    Thread(target=main_message, args=(message,)).start()


@bot.message_handler(commands=["whoami"])
def thread_whoami(message):
    Thread(target=whoami, args=(message,)).start()


@bot.message_handler(content_types=["text", "photo", "video", "voice", "video_note"])
def thread_admin(message):
    Thread(target=admin_broadcast, args=(message,)).start()


def admin_broadcast(message):
    if USERS.check_admin(message.chat.id):
        broadcast_data[message.chat.id] = message
        bot.send_message(
            message.chat.id,
            "Проверил, всё гуд?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Да, проверил", callback_data="do_broadcast"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Нет, переделаю", callback_data="rm_broadcast"
                        )
                    ],
                ],
            ),
        )
        # AdminBroadcast.run(message, broadcast_group='involved')
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


@bot.callback_query_handler(func=lambda call: call.data == "do_broadcast")
def handle_broadcast_callback(call):
    bot.send_message(
        call.from_user.id,
        "Какой группе рассылаем?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=unit, callback_data=unit)]
                for unit in ALLOWED_USER_TYPES
            ],
            row_width=2,
        ),
    )


@bot.callback_query_handler(func=lambda call: call.data == "rm_broadcast")
def handle_rm_broadcast_callback(call):
    del broadcast_data[call.from_user.id]
    bot.send_message(call.from_user.id, "Ок, удалил у себя прошлую попытку")


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


@bot.callback_query_handler(func=lambda call: str(call.data) in [ALLOWED_USER_TYPES])
def handle_confirmed_broadcast_callback(call):
    print("ыть")

    bot.send_message(call.from_user.id, "Начинаю рассылку")
    AdminBroadcast.run(broadcast_data[call.from_user.id], broadcast_group=call.data)


@bot.callback_query_handler(func=lambda call: True)
def handle_confirmed_broadcast_callback(call):
    if call.data in ALLOWED_USER_TYPES:

        bot.send_message(call.from_user.id, "Начинаю рассылку")
        AdminBroadcast.run(broadcast_data[call.from_user.id], broadcast_group=call.data)
