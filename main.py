from app import bot
from utils import configure_logger

logger = configure_logger()

if __name__ == "__main__":

    logger.info("Bot started")
    try:
        bot.polling(none_stop=True)
    except Exception as ex:
        logger.error(f" >> WARNING, Bot has crashed. <<")
        raise ex
