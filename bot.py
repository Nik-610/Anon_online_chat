import telebot
from telebot import types

BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)

users = {}
freeid = None
    
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_gen(message):
    bot.reply_to(message, "Привет! Используй или /find")

# Обработчик команды /find
@bot.message_handler(commands=['find'])
def find(message: types.Message):
    global freeid

    if message.chat.id not in users:
        bot.send_message(message.chat.id, 'Поиск...')

        if freeid is None:
            freeid = message.chat.id
        else:
            # Question:
            # Is there any way to simplify this like `bot.send_message([message.chat.id, freeid], 'Founded!')`?
            bot.send_message(message.chat.id, 'Найдено!')
            bot.send_message(freeid, 'Найдено!')

            users[freeid] = message.chat.id
            users[message.chat.id] = freeid
            freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'Shut up!')


# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop(message: types.Message):
    global freeid

    if message.chat.id in users:
        bot.send_message(message.chat.id, 'Остановка...')
        bot.send_message(users[message.chat.id], 'Твой собеседник вышел -_-`...')

        del users[users[message.chat.id]]
        del users[message.chat.id]
        
        print(users, freeid) # Debug purpose, you can remove that line
    elif message.chat.id == freeid:
        bot.send_message(message.chat.id, 'Остановка...')
        freeid = None

        print(users, freeid) # Debug purpose, you can remove that line
    else:
        bot.send_message(message.chat.id, 'You are not in search!')



@bot.message_handler(content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text', 'venue', 'video', 'video_note', 'voice'])
def chatting(message: types.Message):
    if message.chat.id in users:
        bot.copy_message(users[message.chat.id], users[users[message.chat.id]], message.id)
    else:
        bot.send_message(message.chat.id, 'No one can hear you...')

# Запуск бота
bot.polling()
