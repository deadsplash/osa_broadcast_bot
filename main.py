from app import bot
from utils import configure_logger

logger = configure_logger()

if __name__ == "__main__":

    logger.info("Bot started")
    bot.polling(none_stop=True)
