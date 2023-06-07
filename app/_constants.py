import os

TOKEN = os.getenv("TOKEN")

YANDEX_LINK = "https://ya.ru/"
TG_CHANNEL = "t.me/saucyosa"

WELCOME_TEXT = """Салют, {0.first_name}!

Спасибо, что прошел опрос!

Держи свой подарок — Drum-kit """
TG_MESSAGE = (
    f"Залетай в мой телеграм канал {TG_CHANNEL} — следи за новыми "
    f"релизами, новостями и кучей штук, которые я готовлю на этот год"
)
