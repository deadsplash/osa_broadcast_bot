import telebot
import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def func(message):
    bot.send_message(message.chat.id,
                     "Здарова, {0.first_name} сейчас скину ссылку на яндекс диск".format(message.from_user,
                                                                                         bot.get_me()),
                     parse_mode='html')
    bot.send_message(message.chat.id, "ссылка ".format(message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id,
                     "А также ты должен подписаться на телеграм канал Осы \n ссылка на тг канал".format(
                         message.from_user, bot.get_me()), parse_mode='html')


@bot.message_handler(content_types=['text'])
def ccccc(message):
    bot.send_message(message.chat.id, "все пока я спать".format(message.from_user, bot.get_me()), parse_mode='html')


bot.polling(none_stop=True)
