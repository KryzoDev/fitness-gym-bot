import os
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

users = {}

# Вправи за днями
workouts = {
    "monday": {
        "beginner": [
            ("Присідання з вагою тіла", "https://www.youtube.com/watch?v=aclHkVaku9U"),
            ("Жим ногами в тренажері", "https://www.youtube.com/watch?v=IZxyjW7MPJQ"),
            ("Гіперекстензії", "https://www.youtube.com/watch?v=G5l1f1U5fek"),
            ("Підйом на носки", "https://www.youtube.com/watch?v=YMmgqO8Jo-k")
        ],
        "experienced": [
            ("Присідання зі штангою", "https://www.youtube.com/watch?v=ultWZbUMPL8"),
            ("Жим ногами", "https://www.youtube.com/watch?v=IZxyjW7MPJQ"),
            ("Станова тяга на прямих ногах", "https://www.youtube.com/watch?v=RZqoUYbS-7w"),
            ("Випади з гантелями", "https://www.youtube.com/watch?v=QF0BQS2W80k")
        ]
    },
    "wednesday": {
        "beginner": [
            ("Жим на тренажері", "https://www.youtube.com/watch?v=6JtP6ju0IMw"),
            ("Тяга верхнього блоку", "https://www.youtube.com/watch?v=CAwf7n6Luuc"),
            ("Гантелі лежачи", "https://www.youtube.com/watch?v=VmB1G1K7v94"),
            ("Розведення рук у тренажері", "https://www.youtube.com/watch?v=eozdVDA78K0")
        ],
        "experienced": [
            ("Жим штанги лежачи", "https://www.youtube.com/watch?v=rT7DgCr-3pg"),
            ("Тяга штанги в нахилі", "https://www.youtube.com/watch?v=vT2GjY_Umpw"),
            ("Пуловер з гантеллю", "https://www.youtube.com/watch?v=2-LAMcpzODU"),
            ("Тяга верхнього блока", "https://www.youtube.com/watch?v=CAwf7n6Luuc")
        ]
    },
    "friday": {
        "beginner": [
            ("Підйом гантелей сидячи", "https://www.youtube.com/watch?v=ykJmrZ5v0Oo"),
            ("Розгинання рук на блоці", "https://www.youtube.com/watch?v=vB5OHsJ3EME"),
            ("Молотки з гантелями", "https://www.youtube.com/watch?v=zC3nLlEvin4"),
            ("Віджимання від лавки", "https://www.youtube.com/watch?v=0326dy_-CzM")
        ],
        "experienced": [
            ("Підйом штанги на біцепс", "https://www.youtube.com/watch?v=kwG2ipFRgfo"),
            ("Французький жим", "https://www.youtube.com/watch?v=vB5OHsJ3EME"),
            ("Концентрований підйом", "https://www.youtube.com/watch?v=soxrZlIl35U"),
            ("Віджимання на брусах", "https://www.youtube.com/watch?v=2z8JmcrW-As")
        ]
    }
}

# Кнопки
def day_selection_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Понеділок", "Середа", "Пʼятниця")
    return kb

def exercise_options(index):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🔁 Інша вправа", callback_data=f"replace_{index}"),
        InlineKeyboardButton("🎥 Пояснення", callback_data=f"explain_{index}")
    )
    return kb

# Обробка команд
@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    users[cid] = {"step": "name"}
    bot.send_message(cid, "Привіт! Як тебе звати?")

@bot.message_handler(func=lambda msg: True)
def handle_all(msg):
    cid = msg.chat.id
    text = msg.text.strip().lower()

    if cid not in users:
        users[cid] = {"step": "name"}

    user = users[cid]

    if user["step"] == "name":
        user["name"] = msg.text.strip()
        user["step"] = "experience"
        bot.send_message(cid, f"Радий знайомству, {user['name']}! Маєш досвід тренувань у залі? (Так/Ні)")

    elif user["step"] == "experience":
        user["experienced"] = text == "так"
        user["step"] = "choose_day"
        bot.send_message(cid, "Оберіть день тренування:", reply_markup=day_selection_keyboard())

    elif user["step"] == "choose_day":
        day_map = {
            "понеділок": "monday",
            "середа": "wednesday",
            "пʼятниця": "friday",
            "пятниця": "friday"
        }
        if text in day_map:
            day_key = day_map[text]
            level = "experienced" if user["experienced"] else "beginner"
            user["current_day"] = day_key
            user["current_list"] = workouts[day_key][level][:]
            send_exercises(cid, user)
        else:
            bot.send_message(cid, "Будь ласка, вибери: Понеділок, Середа або Пʼятниця.", reply_markup=day_selection_keyboard())

def send_exercises(cid, user):
    exercises = user["current_list"]
    for i, (name, link) in enumerate(exercises):
        bot.send_message(
            cid,
            f"💪 {name}\n🔁 3 підходи по 12 разів",
            reply_markup=exercise_options(i)
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    cid = call.message.chat.id
    data = call.data
    user = users[cid]

    if data.startswith("replace_"):
        index = int(data.split("_")[1])
        alt = "Альтернативна вправа (наприклад, присідання на одній нозі)"
        bot.edit_message_text(f"🔁 Заміна: {alt}", cid, call.message.message_id)

    elif data.startswith("explain_"):
        index = int(data.split("_")[1])
        name, link = user["current_list"][index]
        bot.send_message(cid, f"🎥 Пояснення до '{name}':\n{link}")

print("Бот запущено ✅")
bot.polling(none_stop=True)
