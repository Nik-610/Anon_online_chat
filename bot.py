import telebot
from telebot import types

BOT_TOKEN = 'YOUR_BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище данных
active_users = {}  # Сопоставление пары собеседников
waiting_user = None  # ID пользователя, который ждет собеседника

# Отправка сообщения об ошибке
def send_error(chat_id, text="Произошла ошибка. Попробуйте снова."):
    bot.send_message(chat_id, text)

# Функция для отправки сообщения пользователю
def send_message_to_user(user_id, text):
    try:
        bot.send_message(user_id, text)
    except telebot.apihelper.ApiException:
        print(f"Ошибка отправки сообщения пользователю {user_id}")

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(
        message,
        "Привет! Используй команду /find, чтобы найти собеседника, "
        "или /stop, чтобы завершить общение."
    )

# Команда /find
@bot.message_handler(commands=['find'])
def handle_find(message):
    global waiting_user
    user_id = message.chat.id

    # Если пользователь уже в активной беседе
    if user_id in active_users:
        bot.send_message(user_id, "Вы уже общаетесь с собеседником. Напишите /stop, чтобы завершить беседу.")
        return

    # Если пользователь уже ожидает
    if waiting_user == user_id:
        bot.send_message(user_id, "Вы уже ожидаете собеседника. Пожалуйста, подождите.")
        return

    # Если есть другой ожидающий пользователь
    if waiting_user is not None:
        partner_id = waiting_user
        active_users[user_id] = partner_id
        active_users[partner_id] = user_id
        waiting_user = None

        send_message_to_user(user_id, "Собеседник найден! Начните общение.")
        send_message_to_user(partner_id, "Собеседник найден! Начните общение.")
    else:
        # Если никого нет в ожидании, добавить текущего пользователя
        waiting_user = user_id
        bot.send_message(user_id, "Поиск собеседника...")

# Команда /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global waiting_user
    user_id = message.chat.id

    # Если пользователь в активной беседе
    if user_id in active_users:
        partner_id = active_users[user_id]
        send_message_to_user(partner_id, "Собеседник завершил общение.")
        send_message_to_user(user_id, "Вы завершили общение.")

        del active_users[user_id]
        del active_users[partner_id]

    # Если пользователь ждет собеседника
    elif waiting_user == user_id:
        bot.send_message(user_id, "Вы прекратили поиск собеседника.")
        waiting_user = None
    else:
        bot.send_message(user_id, "Вы не участвуете в поиске или общении.")

# Пересылка сообщений между собеседниками
@bot.message_handler(content_types=['text', 'photo', 'video', 'voice', 'sticker', 'document', 'location'])
def handle_chat(message):
    user_id = message.chat.id

    # Если пользователь в активной беседе
    if user_id in active_users:
        partner_id = active_users[user_id]
        try:
            bot.copy_message(partner_id, user_id, message.id)
        except telebot.apihelper.ApiException:
            send_message_to_user(user_id, "Не удалось отправить сообщение. Возможно, собеседник недоступен.")
    else:
        bot.send_message(user_id, "Вы пока ни с кем не общаетесь. Напишите /find, чтобы найти собеседника.")

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
