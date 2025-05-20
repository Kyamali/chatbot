import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import random
from datetime import datetime
from pytz import timezone

TOKEN = os.getenv("TOKEN") or "8030675619:AAH_h5GdxathZSlU9hZZ8ZQe1Um19Rnj9gE"

bot = telebot.TeleBot(TOKEN)


questions = {
    "легкий": [
        {
            "question": "Сколько дней в неделе?",
            "options": ["5", "6", "7", "8"],
            "answer": "7",
            "hint": "Это число дней между понедельником и воскресеньем."
        },
        {
            "question": "Какой цвет получается при смешивании синего и жёлтого?",
            "options": ["зелёный", "красный", "оранжевый", "фиолетовый"],
            "answer": "зелёный",
            "hint": "Это цвет травы."
        },
        {
            "question": "Сколько пальцев на одной руке у человека?",
            "options": ["4", "5", "6", "7"],
            "answer": "5",
            "hint": "На каждой руке одинаковое количество пальцев."
        }
    ],
    "средний": [
        {
            "question": "Кто написал 'Война и мир'?",
            "options": ["Достоевский", "Толстой", "Чехов", "Пушкин"],
            "answer": "Толстой",
            "hint": "Фамилия начинается на 'Т'."
        }
    ],
    "сложный": [
        {
            "question": "Как называется самый длинный нерв в теле человека?",
            "options": ["седалищный", "блуждающий", "лицевой", "спинномозговой"],
            "answer": "седалищный",
            "hint": "Он проходит от поясницы к ноге."
        }
    ]
}

# Состояния пользователей
user_data = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        "score": 0,
        "hints": 3,
        "call_used": False,
        "index": 0,
        "questions": []
    }

    all_qs = []
    for level in ["легкий", "средний", "сложный"]:
        random.shuffle(questions[level])
        all_qs.extend(questions[level])
    random.shuffle(all_qs)
    user_data[chat_id]["questions"] = all_qs

    bot.send_message(chat_id, f"Привет! 🎮 Начинаем игру!")
    send_question(chat_id)

# Отправка текущего вопроса
def send_question(chat_id):
    data = user_data[chat_id]
    if data["index"] >= len(data["questions"]):
        bot.send_message(chat_id, f"🏁 Игра окончена! Вы набрали {data['score']} очков.")
        return

    q = data["questions"][data["index"]]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(KeyboardButton(q["options"][0]), KeyboardButton(q["options"][1]))
    markup.row(KeyboardButton(q["options"][2]), KeyboardButton(q["options"][3]))
    markup.row(KeyboardButton("💡 Подсказка"), KeyboardButton("📞 Звонок другу"))

    bot.send_message(chat_id, q["question"], reply_markup=markup)

# Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id)

    if not data:
        bot.send_message(chat_id, "Сначала введите /start чтобы начать игру.")
        return

    text = message.text.strip()

    if text == "💡 Подсказка":
        use_hint(chat_id)
    elif text == "📞 Звонок другу":
        use_call(chat_id)
    else:
        check_answer(chat_id, text)

# Проверка ответа
def check_answer(chat_id, answer_text):
    data = user_data[chat_id]
    current_q = data["questions"][data["index"]]

    if answer_text.lower() == current_q["answer"].lower():
        data["score"] += 10
        bot.send_message(chat_id, "✅ Правильно!")
    else:
        bot.send_message(chat_id, f"❌ Неправильно. Верный ответ: {current_q['answer']}")

    data["index"] += 1
    send_question(chat_id)

# Использование подсказки
def use_hint(chat_id):
    data = user_data[chat_id]
    if data["hints"] > 0:
        q = data["questions"][data["index"]]
        data["hints"] -= 1
        bot.send_message(chat_id, f"💡 Подсказка: {q['hint']} (Осталось: {data['hints']})")
    else:
        bot.send_message(chat_id, "❗ У вас закончились подсказки.")

# Использование звонка другу
def use_call(chat_id):
    data = user_data[chat_id]
    if data["call_used"]:
        bot.send_message(chat_id, "📵 Вы уже использовали звонок другу.")
        return

    data["call_used"] = True
    q = data["questions"][data["index"]]
    correct = q["answer"]
    options = q["options"]

    # 70% вероятность правильного ответа
    if random.random() < 0.7:
        guess = correct
        confidence = "уверен"
    else:
        guess = random.choice([o for o in options if o != correct])
        confidence = "не уверен, но думаю"

    bot.send_message(chat_id, f"📞 Друг говорит: Я {confidence}, что это — {guess}.")

# Запуск бота
if __name__ == "__main__":
    tz = timezone("Europe/Moscow")
    print(f"[{datetime.now(tz)}] ✅ Бот запущен")
    bot.polling(none_stop=True)
