import os
import sys
import json
import logging
import random
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import telebot
from telebot import types

# ================= ЛОГИРОВАНИЕ =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= КОНСТАНТЫ И НАСТРОЙКИ =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)

# ========== ПРАВА ДОСТУПА ==========
OWNER_USERNAME = "prostokiril" 
DEFAULT_ADMINS = ["prostokiril", "ll1_what"]

# Список нежелательных слов
BAD_WORDS = ["еблан", "гандон", "пидор", "https//:", "t.me", "хуй"]

# Путь к файлу базы данных
if os.environ.get('RENDER'):
    DATA_FILE = '/tmp/bot_data.json'
else:
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.json")

# ========== РАНГИ ЗА ЗВЕЗДЫ TELEGRAM ==========
RANKS = {
    "bronze": {"name": "🥉 Бронзовый", "stars": 10, "bonus": 1.1, "color": "🟤"},
    "silver": {"name": "🥈 Серебряный", "stars": 25, "bonus": 1.25, "color": "⚪"},
    "gold": {"name": "🥇 Золотой", "stars": 50, "bonus": 1.5, "color": "🟡"},
    "platinum": {"name": "💎 Платиновый", "stars": 100, "bonus": 2.0, "color": "🔵"},
    "legend": {"name": "👑 Легендарный", "stars": 200, "bonus": 3.0, "color": "🔴"}
}

# ========== ПЕРСОНАЖИ ==========
RAPPERS = {
    "cowboy": {"name": "🤠 CowboyClicker", "price": 1000, "income": 5},
    "beatboxer": {"name": "🎤 BeatBoxer", "price": 5000, "income": 30},
    "dj_cloud": {"name": "🎧 DJ Cloud", "price": 15000, "income": 100},
    "electro": {"name": "⚡ Electro-Rapper", "price": 50000, "income": 500},
    "ruha40": {"name": "🔥 Руха 40", "price": 150000, "income": 1200},
    "russiamafia": {"name": "🦾 russiamafiaextra", "price": 300000, "income": 2500},
    "semetary": {"name": "🪓 Semetary", "price": 600000, "income": 6000}
}

# База данных для новых неазартных игр
CAPITALS = {
    "Россия": "Москва", "Франция": "Париж", "Италия": "Рим", "Испания": "Мадрид",
    "Германия": "Берлин", "Япония": "Токио", "Китай": "Пекин", "Великобритания": "Лондон",
    "Египет": "Каир", "Канада": "Оттава", "Бразилия": "Бразилиа", "Казахстан": "Астана"
}

SCRAMBLE_WORDS = ["скрипт", "сервер", "кнопка", "модератор", "профиль", "баланс", "команда", "консоль"]

# ================= СОХРАНЕНИЕ И ЗАГРУЗКА ДАННЫХ =================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "admins" not in data:
                    data["admins"] = DEFAULT_ADMINS
                if "active_quizzes" not in data:
                    data["active_quizzes"] = {}
                if "active_words" not in data:
                    data["active_words"] = {}
                if "active_numbers" not in data:
                    data["active_numbers"] = {}
                if "duel_invites" not in data:
                    data["duel_invites"] = {}
                if "last_daily" not in data:
                    data["last_daily"] = {}
                if "username_to_id" not in data:
                    data["username_to_id"] = {}
                if "active_capitals" not in data:
                    data["active_capitals"] = {}
                if "active_scrambles" not in data:
                    data["active_scrambles"] = {}
                return data
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
    return {
        "warns": {},
        "mutes": {},
        "ranks": {},
        "balance": {},
        "rappers": {},
        "admins": DEFAULT_ADMINS,
        "active_quizzes": {},
        "active_words": {},
        "active_numbers": {},
        "duel_invites": {},
        "last_daily": {},
        "username_to_id": {},
        "active_capitals": {},
        "active_scrambles": {}
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")

db = load_data()
db_lock = threading.Lock()

def update_db(key, user_id, value):
    with db_lock:
        user_str = str(user_id)
        if key not in db:
            db[key] = {}
        db[key][user_str] = value
        save_data(db)

def get_db_val(key, user_id, default):
    user_str = str(user_id)
    return db.get(key, {}).get(user_str, default)

def save_user_by_username(username, user_id):
    if username:
        with db_lock:
            if "username_to_id" not in db:
                db["username_to_id"] = {}
            db["username_to_id"][username.lower().replace("@", "").strip()] = str(user_id)
            save_data(db)

# Поиск ID по логину или прямому ID
def resolve_user_id(input_str):
    clean = input_str.replace("@", "").lower().strip()
    if clean.isdigit():
        return clean
    return db.get("username_to_id", {}).get(clean)

def is_user_admin(chat_id, user_id, username=None):
    if username and username.lower() == OWNER_USERNAME.lower():
        return True
    if username and username.lower() in [a.lower() for a in db.get("admins", [])]:
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

def set_bot_commands():
    try:
        commands = [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("click", "Кликнуть (заработать очки)"),
            types.BotCommand("profile", "Игровой профиль"),
            types.BotCommand("buy_rapper", "Магазин рэперов"),
            types.BotCommand("duel", "Вызвать на музыкальный батл"),
            types.BotCommand("chests", "🎁 Открыть музыкальные кейсы"),
            types.BotCommand("word", "🧩 Собрать слово"),
            types.BotCommand("quiz", "🧮 Викторина (математика)"),
            types.BotCommand("capitals", "🌍 Столицы стран"),
            types.BotCommand("scramble", "🔤 Собрать слово из букв"),
            types.BotCommand("guess", "🎮 Угадать число"),
            types.BotCommand("coin", "🪙 Виртуальная монетка"),
            types.BotCommand("rhythm", "🥁 Ритм-игра на реакцию"),
            types.BotCommand("daily", "🎁 Забрать ежедневный бонус"),
            types.BotCommand("chat", "✉️ Личное сообщение по ID или Юзеру"),
            types.BotCommand("stars", "VIP ранги за звезды"),
            types.BotCommand("ai", "Задать вопрос ИИ"),
            types.BotCommand("admin", "🔐 Админ-панель управления")
        ]
        bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Не удалось установить команды: {e}")

# ================= КОМАНДЫ СОЗДАТЕЛЯ И АДМИНОВ =================
@bot.message_handler(commands=['save'])
def save_command_handler(message):
    username = message.from_user.username
    if not username or username.lower() != OWNER_USERNAME.lower():
        bot.reply_to(message, "❌ Эта команда доступна только Главному Создателю бота (@prostokiril).")
        return
    try:
        with db_lock:
            save_data(db)
        bot.reply_to(message, "💾 **База данных успешно принудительно сохранена!**", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка сохранения базы данных: {e}")

@bot.message_handler(commands=['reset'])
def reset_command_handler(message):
    username = message.from_user.username
    if not is_user_admin(message.chat.id, message.from_user.id, username):
        bot.reply_to(message, "❌ Эта команда доступна только администраторам.")
        return
        
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "✏️ Использование: `/reset [ID или @username]`", parse_mode="Markdown")
        return
        
    target_id = resolve_user_id(args[1])
    if not target_id:
        bot.reply_to(message, "❌ Пользователь не найден в базе данных.")
        return
    
    with db_lock:
        for key in ["balance", "rappers", "ranks", "warns"]:
            if key in db and str(target_id) in db[key]:
                db[key][str(target_id)] = 0 if key in ["balance", "warns"] else ([] if key == "rappers" else "default")
        save_data(db)
        
    bot.reply_to(message, f"🔄 Игровой аккаунт пользователя с ID `{target_id}` был полностью сброшен!", parse_mode="Markdown")

# ================= ФУНКЦИЯ: ОБЩЕНИЕ ПО ID И ЮЗЕРНЕЙМУ (/chat) =================
@bot.message_handler(commands=['chat'])
def chat_command_handler(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(
            message,
            "✉️ **Личные сообщения по ID или Юзернейму!**\n\n"
            "Используйте формат:\n"
            "`/chat [ID или @username] [Ваше сообщение]`",
            parse_mode="Markdown"
        )
        return
        
    target_input = args[1].strip()
    user_msg = args[2]
    sender_name = message.from_user.first_name
    sender_id = message.from_user.id
    
    target_id = resolve_user_id(target_input)
    if not target_id:
        bot.reply_to(message, f"❌ Не удалось найти пользователя `{target_input}` в базе. Он должен активировать бота.", parse_mode="Markdown")
        return
    
    if str(target_id) == str(sender_id):
        bot.reply_to(message, "❌ Нельзя отправлять сообщения самому себе!")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ Ответить", callback_data=f"chat_reply_{sender_id}"))

    try:
        bot.send_message(
            target_id,
            f"✉️ **Новое входящее сообщение!**\n\n"
            f"👤 Отправитель: *{sender_name}* (ID: `{sender_id}`)\n"
            f"💬 Текст:\n«_{user_msg}_»",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ Сообщение успешно доставлено получателю!")
    except Exception:
        bot.reply_to(message, "❌ Не удалось отправить сообщение. Пользователь заблокировал бота.")

# ================= МУЛЬТИПЛЕЕР (МУЗЫКАЛЬНЫЕ ДУЭЛИ) =================
@bot.message_handler(commands=['duel'])
def duel_handler(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    args = message.text.split()
    
    if not message.reply_to_message:
        bot.reply_to(message, "⚔️ **Музыкальный Батл!**\nОтветьте на сообщение друга в чате командой:\n`/duel [ставка]`", parse_mode="Markdown")
        return
        
    target_id = str(message.reply_to_message.from_user.id)
    target_name = message.reply_to_message.from_user.first_name
    
    if target_id == user_id:
        bot.reply_to(message, "❌ Нельзя вызвать самого себя на батл!")
        return
        
    bet = 100
    if len(args) > 1 and args[1].isdigit():
        bet = int(args[1])
        
    if bet < 10:
        bot.reply_to(message, "❌ Минимальная ставка — 10 очков.")
        return
        
    chall_bal = get_db_val("balance", user_id, 0)
    targ_bal = get_db_val("balance", target_id, 0)
    
    if chall_bal < bet:
        bot.reply_to(message, f"❌ У вас недостаточно очков! Ваш баланс: {chall_bal}")
        return
    if targ_bal < bet:
        bot.reply_to(message, f"❌ У игрока {target_name} недостаточно очков для батла с такой ставкой!")
        return
        
    with db_lock:
        if "duel_invites" not in db:
            db["duel_invites"] = {}
        db["duel_invites"][target_id] = {
            "challenger_id": user_id,
            "challenger_name": user_name,
            "bet": bet
        }
        save_data(db)
        
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎤 Принять вызов", callback_data=f"duel_accept_{target_id}"),
        types.InlineKeyboardButton("🛡 Отклонить", callback_data=f"duel_decline_{target_id}")
    )
    
    bot.send_message(
        message.chat.id,
        f"⚔️ **Музыкальный фристайл-батл!**\n\n"
        f"🎙 **{user_name}** вызывает **{target_name}** на рэп-дуэль!\n"
        f"💰 Ставка: **{bet} игровых очков**",
        reply_markup=markup
    )

# ================= ИГРА: РАСШИРЕННЫЕ КЕЙСЫ (/chests) =================
@bot.message_handler(commands=['chests'])
def chests_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🥉 Бронзовый Студийный Кейс (200 очков)", callback_data="chest_open_bronze"),
        types.InlineKeyboardButton("🥈 Серебряный Кейс Рэпера (1000 очков)", callback_data="chest_open_silver"),
        types.InlineKeyboardButton("🥇 Золотой Легендарный Кейс (5000 очков)", callback_data="chest_open_gold")
    )
    bot.reply_to(message, "📦 **Выберите музыкальный кейс для открытия:**", reply_markup=markup)

# ================= ИГРА: УГАДАЙ ЧИСЛО (/guess) =================
@bot.message_handler(commands=['guess'])
def guess_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    if len(args) < 2:
        secret_num = random.randint(1, 100)
        with db_lock:
            if "active_numbers" not in db:
                db["active_numbers"] = {}
            db["active_numbers"][user_id] = secret_num
            save_data(db)
        bot.reply_to(message, "🎮 **Я загадал число от 1 до 100!**\nПиши: `/guess [число]`\n\nКаждая ошибка: **-20 очков**!\nПобеда: **+300 очков**!", parse_mode="Markdown")
        return
        
    active_numbers = db.get("active_numbers", {})
    if user_id not in active_numbers:
        bot.reply_to(message, "❌ У вас нет активной игры. Напишите `/guess` без параметров.")
        return
        
    current_bal = get_db_val("balance", user_id, 0)
    if current_bal < 20:
        bot.reply_to(message, "❌ Нужно минимум 20 очков для попытки!")
        return

    try:
        user_num = int(args[1])
        secret = int(active_numbers[user_id])
        
        if user_num == secret:
            reward = 300
            update_db("balance", user_id, current_bal + reward)
            with db_lock:
                if "active_numbers" in db and user_id in db["active_numbers"]:
                    del db["active_numbers"][user_id]
                    save_data(db)
            bot.reply_to(message, f"🎉 **ПОЗДРАВЛЯЕМ!** Вы угадали число `{secret}`! Награда **+{reward} очков**!")
        elif user_num < secret:
            update_db("balance", user_id, current_bal - 20)
            bot.reply_to(message, f"📈 Моё число **больше**, чем {user_num}!\nСписано **-20 очков**.")
        else:
            update_db("balance", user_id, current_bal - 20)
            bot.reply_to(message, f"📉 Моё число **меньше**, чем {user_num}!\nСписано **-20 очков**.")
    except ValueError:
        bot.reply_to(message, "❌ Пожалуйста, введите целое число.")

# ================= ИГРА: ВИРТУАЛЬНАЯ МОНЕТКА (/coin) =================
@bot.message_handler(commands=['coin'])
def coin_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    if len(args) < 3:
        bot.reply_to(message, "🪙 **Виртуальная монетка!**\nФормат:\n`/coin [орел/решка] [ставка]`")
        return
        
    choice = args[1].lower().strip()
    if choice not in ["орел", "решка"]:
        bot.reply_to(message, "❌ Выберите только `орел` или `решка`!")
        return
        
    try:
        bet = int(args[2])
        if bet < 10:
            bot.reply_to(message, "❌ Минимальная ставка — 10 очков!")
            return
            
        current_bal = get_db_val("balance", user_id, 0)
        if current_bal < bet:
            bot.reply_to(message, f"❌ Недостаточно баланса! Ваш баланс: {current_bal}")
            return
            
        flip_result = random.choice(["орел", "решка"])
        
        if choice == flip_result:
            update_db("balance", user_id, current_bal + bet)
            bot.reply_to(message, f"🪙 Выпало: **{flip_result.upper()}**!\n\n🎉 Вы выиграли **+{bet} очков**!")
        else:
            update_db("balance", user_id, current_bal - bet)
            bot.reply_to(message, f"🪙 Выпало: **{flip_result.upper()}**!\n\n😢 Проигрыш. Списано {bet} очков.")
    except ValueError:
        bot.reply_to(message, "❌ Сумма ставки должна быть целым числом.")

# ================= РИТМ-ИГРА НА РЕАКЦИЮ (/rhythm) =================
@bot.message_handler(commands=['rhythm'])
def rhythm_handler(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔥 СЛОВИТЬ БИТ! 🔥", callback_data=f"rhythm_hit_{user_id}_{int(time.time())}"))
    
    bot.reply_to(
        message, 
        "🥁 **Ритм-игра «Попади в бит»!**\n\n"
        "Нажми на кнопку ниже в течение **1.5 секунд**, чтобы поймать бит!\n"
        "_Внимание: опоздание стоит -100 очков!_" ,
        reply_markup=markup
    )

# ================= ИГРА: УГАДАЙ СЛОВО (/word) =================
@bot.message_handler(commands=['word'])
def word_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    words_pool = ["рэпер", "музыка", "трек", "микрофон", "студия", "гитара", "альбом", "концерт", "сцена", "аккорд", "песня", "ритм", "звук", "сэмпл", "винил", "битмейкер"]
    
    if len(args) < 2:
        word = random.choice(words_pool)
        scrambled = list(word)
        random.shuffle(scrambled)
        scrambled_word = "".join(scrambled).upper()
        
        with db_lock:
            if "active_words" not in db:
                db["active_words"] = {}
            db["active_words"][user_id] = word
            save_data(db)
            
        bot.reply_to(message, f"🧩 **Собери слово из букв:**\n\n👉  `{scrambled_word}`  👈\n\nОтвет: `/word [слово]`", parse_mode="Markdown")
        return
        
    active_words = db.get("active_words", {})
    if user_id not in active_words:
        bot.reply_to(message, "❌ Нет активной игры. Напишите `/word`.")
        return
        
    user_guess = args[1].lower().strip()
    correct_word = active_words[user_id].lower().strip()
    
    if user_guess == correct_word:
        reward = 250
        current_bal = get_db_val("balance", user_id, 0)
        update_db("balance", user_id, current_bal + reward)
        with db_lock:
            if "active_words" in db and user_id in db["active_words"]:
                del db["active_words"][user_id]
                save_data(db)
        bot.reply_to(message, f"🎉 Верно! Слово **{correct_word.upper()}**. Награда **+{reward} очков**!")
    else:
        current_bal = get_db_val("balance", user_id, 0)
        update_db("balance", user_id, max(0, current_bal - 50))
        bot.reply_to(message, "❌ Неверно. Списано **-50 очков**.")

# ================= НОВЫЕ ИГРЫ: СТОЛИЦЫ И СЛОВА =================
@bot.message_handler(commands=['capitals'])
def capitals_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        country = random.choice(list(CAPITALS.keys()))
        with db_lock:
            if "active_capitals" not in db:
                db["active_capitals"] = {}
            db["active_capitals"][user_id] = country
            save_data(db)
        bot.reply_to(message, f"🌍 **Географическая викторина!**\n\nНазовите столицу страны: **{country}**\n\nОтвет отправьте командой: `/capitals [город]`")
        return
        
    active_capitals = db.get("active_capitals", {})
    if user_id not in active_capitals:
        bot.reply_to(message, "❌ У вас нет активного вопроса. Напишите `/capitals` без параметров.")
        return
        
    user_ans = args[1].strip().lower()
    country = active_capitals[user_id]
    correct_ans = CAPITALS[country].lower()
    
    if user_ans == correct_ans:
        reward = 200
        current_bal = get_db_val("balance", user_id, 0)
        update_db("balance", user_id, current_bal + reward)
        with db_lock:
            if "active_capitals" in db and user_id in db["active_capitals"]:
                del db["active_capitals"][user_id]
                save_data(db)
        bot.reply_to(message, f"🎉 Правильно! Столица страны {country} — это **{CAPITALS[country]}**! Получено **+{reward} очков**!")
    else:
        bot.reply_to(message, "❌ Неверно! Попробуйте подумать ещё раз.")

@bot.message_handler(commands=['scramble'])
def scramble_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    if len(args) < 2:
        word = random.choice(SCRAMBLE_WORDS)
        scrambled = list(word)
        random.shuffle(scrambled)
        scrambled_str = "".join(scrambled).upper()
        
        with db_lock:
            if "active_scrambles" not in db:
                db["active_scrambles"] = {}
            db["active_scrambles"][user_id] = word
            save_data(db)
        bot.reply_to(message, f"🔤 **Собери IT-слово:**\n\n👉  `{scrambled_str}`  👈\n\nОтправь ответ: `/scramble [слово]`")
        return
        
    active_scrambles = db.get("active_scrambles", {})
    if user_id not in active_scrambles:
        bot.reply_to(message, "❌ Нет активной игры. Начните заново: `/scramble`")
        return
        
    user_guess = args[1].strip().lower()
    correct = active_scrambles[user_id]
    
    if user_guess == correct:
        reward = 150
        current_bal = get_db_val("balance", user_id, 0)
        update_db("balance", user_id, current_bal + reward)
        with db_lock:
            if "active_scrambles" in db and user_id in db["active_scrambles"]:
                del db["active_scrambles"][user_id]
                save_data(db)
        bot.reply_to(message, f"🎉 Отлично! Ты угадал слово **{correct.upper()}**! Получено **+{reward} очков**!")
    else:
        bot.reply_to(message, "❌ Ошибка. Попробуй переставить буквы иначе!")

# ================= ЕЖЕДНЕВНЫЙ БОНУС (/daily) =================
@bot.message_handler(commands=['daily'])
def daily_handler(message):
    user_id = str(message.from_user.id)
    last_daily = get_db_val("last_daily", user_id, 0)
    current_time = time.time()
    
    if current_time - last_daily < 86400:
        remaining_sec = int(86400 - (current_time - last_daily))
        hours = remaining_sec // 3600
        minutes = (remaining_sec % 3600) // 60
        bot.reply_to(message, f"⏱ Приходите снова через **{hours} ч. {minutes} мин.**")
        return
        
    reward = random.randint(500, 1000)
    current_bal = get_db_val("balance", user_id, 0)
    
    update_db("balance", user_id, current_bal + reward)
    update_db("last_daily", user_id, current_time)
    bot.reply_to(message, f"🎁 **Бонус получен!**\n\nВы получили **+{reward} очков**! 🎉")

# ================= ВИКТОРИНА (/quiz) =================
@bot.message_handler(commands=['quiz'])
def quiz_handler(message):
    user_id = str(message.from_user.id)
    args = message.text.split()
    
    if len(args) < 2:
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        correct_ans = num1 + num2
        
        with db_lock:
            if "active_quizzes" not in db:
                db["active_quizzes"] = {}
            db["active_quizzes"][user_id] = correct_ans
            save_data(db)
        bot.reply_to(message, f"🧮 **Реши пример:**\n\nСколько будет: **{num1} + {num2}**?\n\nОтвет: `/quiz [ответ]`", parse_mode="Markdown")
        return
        
    active_quizzes = db.get("active_quizzes", {})
    if user_id not in active_quizzes:
        bot.reply_to(message, "❌ Нет активного примера. Напишите `/quiz`.")
        return
        
    try:
        user_ans = int(args[1])
        correct_ans = int(active_quizzes[user_id])
        
        if user_ans == correct_ans:
            reward = 200
            current_bal = get_db_val("balance", user_id, 0)
            update_db("balance", user_id, current_bal + reward)
            with db_lock:
                if "active_quizzes" in db and user_id in db["active_quizzes"]:
                    del db["active_quizzes"][user_id]
                    save_data(db)
            bot.reply_to(message, f"🎉 Верно! Вы заработали **+{reward} очков**!")
        else:
            current_bal = get_db_val("balance", user_id, 0)
            update_db("balance", user_id, max(0, current_bal - 150))
            bot.reply_to(message, "❌ Неверный ответ. Списано **-150 очков**.")
    except ValueError:
        bot.reply_to(message, "❌ Ответ должен быть целым числом.")

# ================= КНОПКИ CALLBACK ОБРАБОТЧИКА =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    username = call.from_user.username
    user_id = str(call.from_user.id)
    
    # --- ОБРАБОТКА ПОКУПКИ СТАТУСОВ ЧЕРЕЗ ИНЛАЙН МЕНЮ ---
    if call.data.startswith("buy_rank_inline_"):
        rank_id = call.data.split("_")[3]
        if rank_id not in RANKS:
            bot.answer_callback_query(call.id, "❌ Неверный ранг!", show_alert=True)
            return
            
        prices = [types.LabeledPrice(label=RANKS[rank_id]["name"], amount=RANKS[rank_id]["stars"])]
        try:
            bot.send_invoice(
                call.message.chat.id, 
                title=RANKS[rank_id]["name"], 
                description=f"Приобретение VIP статуса: {RANKS[rank_id]['name']}", 
                invoice_payload=f"buy_rank_{rank_id}_{user_id}", 
                provider_token="", 
                currency="XTR", 
                prices=prices,
                start_parameter="buy-rank"
            )
            bot.answer_callback_query(call.id, "💰 Счет сформирован!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Ошибка: {e}", show_alert=True)
        return

    # --- ОБРАБОТКА ДУЭЛЕЙ ---
    if call.data.startswith("duel_accept_") or call.data.startswith("duel_decline_"):
        target_id = call.data.split("_")[2]
        if user_id != target_id:
            bot.answer_callback_query(call.id, "❌ Этот вызов брошен не вам!", show_alert=True)
            return
            
        invites = db.get("duel_invites", {})
        if target_id not in invites:
            bot.answer_callback_query(call.id, "❌ Вызов устарел.", show_alert=True)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            return
            
        invite_data = invites[target_id]
        chall_id = invite_data["challenger_id"]
        chall_name = invite_data["challenger_name"]
        bet = invite_data["bet"]
        target_name = call.from_user.first_name
        
        if "accept" in call.data:
            chall_bal = get_db_val("balance", chall_id, 0)
            targ_bal = get_db_val("balance", target_id, 0)
            
            if chall_bal < bet:
                bot.send_message(call.message.chat.id, f"❌ Батл отменен. У {chall_name} не хватает очков!")
                with db_lock:
                    if target_id in db["duel_invites"]: del db["duel_invites"][target_id]
                    save_data(db)
                try: bot.delete_message(call.message.chat.id, call.message.message_id)
                except: pass
                bot.answer_callback_query(call.id, "❌ Отменено.")
                return
                
            if targ_bal < bet:
                bot.answer_callback_query(call.id, "❌ У вас не хватает очков!", show_alert=True)
                return
                
            roll_challenger = random.randint(1, 100)
            roll_target = random.randint(1, 100)
            
            battle_text = (
                f"🔥 **Музыкальный батл начался!** 🔥\n\n"
                f"🎤 **{chall_name}** выдает взрывной битбокс...\n"
                f"🎤 **{target_name}** зачитывает мощные рифмы...\n\n"
            )
            
            if roll_challenger > roll_target:
                update_db("balance", chall_id, chall_bal + bet)
                update_db("balance", target_id, targ_bal - bet)
                battle_text += f"🏆 **Победил {chall_name}!** (+{bet} очков)\n😢 {target_name} уступает."
            elif roll_target > roll_challenger:
                update_db("balance", chall_id, chall_bal - bet)
                update_db("balance", target_id, targ_bal + bet)
                battle_text += f"🏆 **Победил {target_name}!** (+{bet} очков)\n😢 {chall_name} уступает."
            else:
                battle_text += f"🤝 **Ничья!** Очки остаются при вас!"
                
            bot.send_message(call.message.chat.id, battle_text)
            bot.answer_callback_query(call.id, "✅ Батл сыгран!")
            with db_lock:
                if target_id in db["duel_invites"]: del db["duel_invites"][target_id]
                save_data(db)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            
        elif "decline" in call.data:
            bot.send_message(call.message.chat.id, f"🛡 **{target_name}** отклонил вызов.")
            bot.answer_callback_query(call.id, "❌ Отклонено.")
            with db_lock:
                if target_id in db["duel_invites"]: del db["duel_invites"][target_id]
                save_data(db)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
        return

    # --- РИТМ-ИГРА ОБРАБОТЧИК ---
    if call.data.startswith("rhythm_hit_"):
        parts = call.data.split("_")
        creator_id = parts[2]
        send_time = int(parts[3])
        
        if str(user_id) != str(creator_id):
            bot.answer_callback_query(call.id, "❌ Это не ваша ритм-игра!", show_alert=True)
            return
            
        time_diff = time.time() - send_time
        if time_diff <= 1.5:
            reward = 150
            current_bal = get_db_val("balance", user_id, 0)
            update_db("balance", user_id, current_bal + reward)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"🥁 **ИДЕАЛЬНО!**\n\nВы попали точно в бит за *{time_diff:.2f} сек.*! Награда **+{reward} очков**!"
            )
        else:
            current_bal = get_db_val("balance", user_id, 0)
            update_db("balance", user_id, max(0, current_bal - 100))
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"😢 **Слишком медленно!** (*{time_diff:.2f} сек.*).\nШтраф **-100 очков**."
            )
        bot.answer_callback_query(call.id, "🥁 Бит обработан!")
        return

    # --- ОТКРЫТИЕ КЕЙСОВ ---
    if call.data.startswith("chest_open_"):
        chest_type = call.data.split("_")[2]
        current_bal = get_db_val("balance", user_id, 0)
        
        if chest_type == "bronze":
            cost, title = 200, "🥉 Бронзовый Студийный Кейс"
        elif chest_type == "silver":
            cost, title = 1000, "🥈 Серебряный Кейс Рэпера"
        else:
            cost, title = 5000, "🥇 Золотой Легендарный Кейс"
            
        if current_bal < cost:
            bot.answer_callback_query(call.id, f"❌ Недостаточно очков! Нужно {cost}.", show_alert=True)
            return
            
        update_db("balance", user_id, current_bal - cost)
        chance = random.randint(1, 100)
        reward_msg = ""
        
        if chest_type == "bronze":
            if chance <= 70:
                reward = random.randint(30, 110)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"📼 Кассета сдана за **{reward} очков**."
            elif chance <= 92:
                reward = random.randint(210, 310)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"🎤 Проводной микрофон продан за **{reward} очков**!"
            else:
                owned = get_db_val("rappers", user_id, [])
                if "cowboy" not in owned:
                    owned.append("cowboy")
                    update_db("rappers", user_id, owned)
                    reward_msg = "🤠 Персонаж **CowboyClicker** присоединился к вам! 🎉"
                else:
                    reward = 500
                    update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                    reward_msg = f"🤠 Дубликат CowboyClicker! Начислено **{reward} очков**!"
                    
        elif chest_type == "silver":
            if chance <= 65:
                reward = random.randint(150, 600)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"🎸 Обычный мерч продан за **{reward} очков**."
            elif chance <= 90:
                reward = random.randint(1100, 1900)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"🎛 Пульт принес **{reward} очков**!"
            else:
                owned = get_db_val("rappers", user_id, [])
                rapper_get = random.choice(["cowboy", "beatboxer"])
                if rapper_get not in owned:
                    owned.append(rapper_get)
                    update_db("rappers", user_id, owned)
                    reward_msg = f"🎤 К вам примкнул **{RAPPERS[rapper_get]['name']}**! 🎉"
                else:
                    reward = 1500
                    update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                    reward_msg = f"👥 Компенсация за дубликат: **{reward} очков**!"
                    
        elif chest_type == "gold":
            if chance <= 60:
                reward = random.randint(1000, 3500)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"🎹 Старый синтезатор ушел за **{reward} очков**."
            elif chance <= 88:
                reward = random.randint(6000, 11000)
                update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                reward_msg = f"💿 Ваш сингл на радио принес **{reward} очков**! 🔥"
            else:
                owned = get_db_val("rappers", user_id, [])
                rapper_get = random.choice(["dj_cloud", "electro", "ruha40", "russiamafia", "semetary"])
                if rapper_get not in owned:
                    owned.append(rapper_get)
                    update_db("rappers", user_id, owned)
                    reward_msg = f"⚡ Мега-выигрыш! Персонаж **{RAPPERS[rapper_get]['name']}** у вас! 👑"
                else:
                    reward = 15000
                    update_db("balance", user_id, get_db_val("balance", user_id, 0) + reward)
                    reward_msg = f"💎 Компенсация за дубликат: **{reward} очков**!"
                    
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📦 **Открытие: {title}**\n\n{reward_msg}\n\n💰 Баланс: *{get_db_val('balance', user_id, 0)} очков*.",
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "📦 Кейс открыт!")
        return

    # --- КЛИЕНТ ЧАТ ОТВЕТА ---
    if call.data.startswith("chat_reply_"):
        sender_id = call.data.split("_")[2]
        msg = bot.send_message(call.message.chat.id, f"✍️ Напишите ответное сообщение для пользователя `{sender_id}`:")
        bot.register_next_step_handler(msg, lambda m: process_quick_reply(m, sender_id))
        bot.answer_callback_query(call.id)
        return

    # --- АДМИН КОЛБЭКИ ---
    if not is_user_admin(call.message.chat.id, call.from_user.id, username):
        bot.answer_callback_query(call.id, "❌ У вас нет прав админа!", show_alert=True)
        return

    action = call.data
    bot.answer_callback_query(call.id) # Моментальное гашение кнопки
    
    if action == "adm_give_money":
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя или @username и сумму очков через пробел:\n`[ID/Логин] [Сумма]`")
        bot.register_next_step_handler(msg, process_admin_money)
    elif action == "adm_give_rank":
        msg = bot.send_message(call.message.chat.id, "Введите ID или @username и ранг (bronze, silver, gold, platinum, legend):\n`[ID/Логин] [ранг]`")
        bot.register_next_step_handler(msg, process_admin_rank)
    elif action == "adm_give_rapper":
        msg = bot.send_message(call.message.chat.id, "Введите ID или @username и код рэпера через пробел:\n`[ID/Логин] [рэпер]`")
        bot.register_next_step_handler(msg, process_admin_rapper)
    elif action == "adm_add_admin":
        if not username or username.lower() != OWNER_USERNAME.lower():
            bot.send_message(call.message.chat.id, "❌ Только Владелец @prostokiril может делать это!")
            return
        msg = bot.send_message(call.message.chat.id, "Введите юзернейм нового администратора (без знака @):")
        bot.register_next_step_handler(msg, process_add_admin)
    elif action == "adm_remove_admin":
        if not username or username.lower() != OWNER_USERNAME.lower():
            bot.send_message(call.message.chat.id, "❌ Только Владелец @prostokiril может делать это!")
            return
        msg = bot.send_message(call.message.chat.id, "Введите юзернейм админа для удаления:")
        bot.register_next_step_handler(msg, process_remove_admin)

def process_quick_reply(message, target_id):
    sender_name = message.from_user.first_name
    sender_id = message.from_user.id
    user_msg = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ Ответить", callback_data=f"chat_reply_{sender_id}"))
    
    try:
        bot.send_message(
            target_id,
            f"✉️ **Входящий ответ!**\n\n"
            f"👤 Отправитель: *{sender_name}* (ID: `{sender_id}`)\n"
            f"💬 Текст:\n«_{user_msg}_»",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        bot.reply_to(message, "✅ Ваш ответ успешно доставлен!")
    except Exception:
        bot.reply_to(message, "❌ Не удалось доставить ответ.")

# ================= АДМИН ВВОД ДАННЫХ (ИСПРАВЛЕННЫЙ) =================
def process_admin_money(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Неверный ввод.")
            return
        target_input, amount = parts[0], parts[1]
        amount = int(amount)
        uid = resolve_user_id(target_input)
        if not uid:
            bot.reply_to(message, f"❌ Пользователь `{target_input}` не найден в БД бота.")
            return
        current = get_db_val("balance", uid, 0)
        update_db("balance", uid, current + amount)
        bot.reply_to(message, f"✅ Баланс игрока `{uid}` увеличен на {amount} очков!", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка ввода: {e}")

def process_admin_rank(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Ошибка ввода.")
            return
        target_input, rank_id = parts[0], parts[1].lower()
        uid = resolve_user_id(target_input)
        if not uid:
            bot.reply_to(message, f"❌ Пользователь `{target_input}` не найден.")
            return
        if rank_id in RANKS:
            update_db("ranks", uid, rank_id)
            bot.reply_to(message, f"✅ Игроку `{uid}` выдан ранг {RANKS[rank_id]['name']}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Такого ранга не существует.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка ввода: {e}")

def process_admin_rapper(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Ошибка ввода.")
            return
        target_input, rapper_id = parts[0], parts[1].lower()
        uid = resolve_user_id(target_input)
        if not uid:
            bot.reply_to(message, f"❌ Пользователь `{target_input}` не найден.")
            return
        if rapper_id in RAPPERS:
            owned = get_db_val("rappers", uid, [])
            if rapper_id not in owned:
                owned.append(rapper_id)
                update_db("rappers", uid, owned)
            bot.reply_to(message, f"✅ Игроку `{uid}` выдан рэпер {RAPPERS[rapper_id]['name']}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Такого рэпера нет в магазине.")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка ввода: {e}")

def process_add_admin(message):
    target = message.text.strip().replace("@", "")
    with db_lock:
        admins = db.get("admins", [])
        if target.lower() not in [a.lower() for a in admins]:
            admins.append(target)
            db["admins"] = admins
            save_data(db)
            bot.reply_to(message, f"👑 Пользователь @{target} добавлен в список админов!")
        else:
            bot.reply_to(message, f"⚠️ Пользователь @{target} уже админ.")

def process_remove_admin(message):
    target = message.text.strip().replace("@", "")
    if target.lower() == OWNER_USERNAME.lower():
        bot.reply_to(message, "❌ Нельзя снять создателя.")
        return
    with db_lock:
        admins = db.get("admins", [])
        filtered = [a for a in admins if a.lower() != target.lower()]
        db["admins"] = filtered
        save_data(db)
        bot.reply_to(message, f"🚫 @{target} исключен из админов.")

# ================= ПАНЕЛЬ УПРАВЛЕНИЯ /admin =================
@bot.message_handler(commands=['admin'])
def admin_panel_handler(message):
    username = message.from_user.username
    if not is_user_admin(message.chat.id, message.from_user.id, username):
        bot.reply_to(message, "❌ Доступ к админ-панели закрыт.")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💰 Выдать деньги себе/игроку", callback_data="adm_give_money"),
        types.InlineKeyboardButton("🎖 Изменить ранг", callback_data="adm_give_rank"),
        types.InlineKeyboardButton("🎤 Выдать рэпера", callback_data="adm_give_rapper")
    )
    
    if username and username.lower() == OWNER_USERNAME.lower():
        markup.add(
            types.InlineKeyboardButton("➕ Назначить Админа", callback_data="adm_add_admin"),
            types.InlineKeyboardButton("➖ Снять Админа", callback_data="adm_remove_admin")
        )
        
    bot.send_message(message.chat.id, "🔐 **Панель управления Ботом**\nВыберите действие ниже:", reply_markup=markup, parse_mode="Markdown")

# ================= ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ =================
@bot.message_handler(commands=['profile'])
def profile_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username
    balance = get_db_val("balance", user_id, 0)
    user_rank_id = get_db_val("ranks", user_id, "default")
    
    if username and username.lower() == OWNER_USERNAME.lower():
        role_status = "👑 Главный Создатель бота"
        rank_color = "👑"
    elif username and username.lower() in [a.lower() for a in db.get("admins", [])]:
        role_status = "👮 Администратор бота"
        rank_color = "👮"
    else:
        role_status = "👤 Игрок чата"
        rank_color = "👤"
        
    rank_name = RANKS[user_rank_id]["name"] if user_rank_id in RANKS else "Обычный"
    owned_rappers = get_db_val("rappers", user_id, [])
    rappers_str = ", ".join([RAPPERS[r]["name"] for r in owned_rappers if r in RAPPERS]) or "Пока нет"
    
    profile_text = (
        f"{rank_color} **Игровой профиль {message.from_user.first_name}**\n\n"
        f"⭐ Роль: `{role_status}`\n"
        f"🏅 VIP ранг: {rank_name}\n"
        f"🆔 Ваш ID: `{user_id}`\n"
        f"💰 Баланс кликера: {balance} очков\n"
        f"🎒 Музыкальная команда: {rappers_str}\n"
    )
    bot.reply_to(message, profile_text, parse_mode="Markdown")

# ================= СТАНДАРТНЫЕ КОМАНДЫ МОДЕРАЦИИ =================
@bot.message_handler(commands=['ban'])
def ban_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    if not message.reply_to_message: return
    try:
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, "👤 Пользователь успешно заблокирован!")
    except Exception as e: bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['mute'])
def mute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    if not message.reply_to_message: return
    args = message.text.split()
    minutes = int(args[1]) if len(args) > 1 and args[1].isdigit() else 15
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=int(time.time() + minutes*60), can_send_messages=False)
        bot.reply_to(message, f"🔇 Ограничение на {minutes} мин. успешно выдано.")
    except Exception as e: bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['unmute'])
def unmute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    if not message.reply_to_message: return
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        bot.reply_to(message, "🔊 Ограничения полностью сняты!")
    except Exception as e: bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['warn'])
def warn_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    if not message.reply_to_message: return
    target_id = message.reply_to_message.from_user.id
    current_warns = get_db_val("warns", target_id, 0) + 1
    update_db("warns", target_id, current_warns)
    if current_warns >= 3:
        bot.restrict_chat_member(message.chat.id, target_id, until_date=int(time.time() + 86400), can_send_messages=False)
        update_db("warns", target_id, 0)
        bot.reply_to(message, "⛔️ 3/3 предупреждений! Игрок отправлен в мут на 24 часа.")
    else:
        bot.reply_to(message, f"⚠️ Выдано предупреждение ({current_warns}/3)!")

# ================= КЛИКЕР И ШОП =================
@bot.message_handler(commands=['start'])
def start_handler(message):
    save_user_by_username(message.from_user.username, message.from_user.id)
    bot.reply_to(
        message, 
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я готов к работе и оптимизирован для Render! 🚀\n\n"
        "🎮 Все игры доступны в синей кнопке 'Меню' слева снизу."
    )

@bot.message_handler(commands=['click'])
def click_handler(message):
    user_id = message.from_user.id
    save_user_by_username(message.from_user.username, user_id)
    
    if random.randint(1, 100) <= 5:
        current_bal = get_db_val("balance", user_id, 0)
        penalty = 100
        update_db("balance", user_id, max(0, current_bal - penalty))
        bot.reply_to(message, f"🎸 **На студии лопнула гитарная струна!**\nСписано **-{penalty} очков**.")
        return

    owned = get_db_val("rappers", user_id, [])
    passive = sum([RAPPERS[item]["income"] for item in owned if item in RAPPERS])
    user_rank = get_db_val("ranks", user_id, "default")
    bonus = RANKS[user_rank]["bonus"] if user_rank in RANKS else 1.0
    
    val = int((2 + passive * 0.1) * bonus)
    new_bal = get_db_val("balance", user_id, 0) + val
    update_db("balance", user_id, new_bal)
    bot.reply_to(message, f"🖱 +{val} очков! Баланс: {new_bal}")

@bot.message_handler(commands=['buy_rapper'])
def buy_rapper_handler(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        text = "🛍 **Магазин рэперов:**\n\n"
        for k, v in RAPPERS.items(): text += f"• `{k}` — {v['name']} (Цена: {v['price']} | Доход: +{v['income']}/клик)\n"
        bot.reply_to(message, text, parse_mode="Markdown")
        return
    rapper_key = args[1].lower()
    if rapper_key in RAPPERS:
        bal = get_db_val("balance", user_id, 0)
        price = RAPPERS[rapper_key]["price"]
        if bal >= price:
            owned = get_db_val("rappers", user_id, [])
            if rapper_key not in owned:
                owned.append(rapper_key)
                update_db("balance", user_id, bal - price)
                update_db("rappers", user_id, owned)
                bot.reply_to(message, "🎉 Успешно куплено!")
            else: bot.reply_to(message, "⚠️ Уже есть в команде.")
        else: bot.reply_to(message, f"❌ Недостаточно очков (требуется {price}).")

@bot.message_handler(commands=['dice'])
def dice_handler(message): bot.send_dice(message.chat.id, emoji="🎲")

@bot.message_handler(commands=['rsp'])
def rsp_handler(message):
    args = message.text.split()
    if len(args) < 2: return
    choices = ["камень", "ножницы", "бумага"]
    user = args[1].lower()
    if user not in choices: return
    bot_c = random.choice(choices)
    if user == bot_c: res = "Ничья!"
    elif (user == "камень" and bot_c == "ножницы") or (user == "ножницы" and bot_c == "бумага") or (user == "бумага" and bot_c == "камень"):
        res = "Победа! +50 очков."
        update_db("balance", message.from_user.id, get_db_val("balance", message.from_user.id, 0) + 50)
    else: res = "Бот победил."
    bot.reply_to(message, f"Ваш выбор: {user}\nБот выбор: {bot_c}\n\n{res}")

# ================= СИСТЕМА STARS =================
@bot.message_handler(commands=['stars'])
def stars_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    text = "🌟 **VIP Статусы за Telegram Stars!** 🌟\n\n"
    for k, v in RANKS.items(): 
        text += f"• **{v['name']}** — {v['stars']} Stars ⭐\n"
        markup.add(types.InlineKeyboardButton(f"Купить {v['name']} за {v['stars']} ⭐", callback_data=f"buy_rank_inline_{k}"))
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query): 
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("buy_rank_"):
        parts = payload.split("_")
        rank_id = parts[2]
        user_id = int(parts[3])
        update_db("ranks", user_id, rank_id)
        bot.reply_to(message, f"🎉 Оплата прошла! Ранг: **{RANKS[rank_id]['name']}**!")

@bot.message_handler(commands=['ai'])
def ai_handler(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return
    msg_waiting = bot.reply_to(message, "🤖 *ИИ думает...*", parse_mode="Markdown")
    responses = [
        "🤖 Отличная мысль! Оптимизация проекта — залог успеха.",
        "🤖 Интересный вопрос. В нашем кликере пассивный доход решает любые проблемы!",
        "🤖 Мои нейросети говорят, что 99% серверов Render одобряют этот ход мыслей."
    ]
    bot.edit_message_text(random.choice(responses), chat_id=message.chat.id, message_id=msg_waiting.message_id)

# ================= АВТО-МОДЕРАЦИЯ И СВЯЗКА ДАННЫХ =================
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def auto_moderation(message):
    # Сохраняем связку логина и ID
    save_user_by_username(message.from_user.username, message.from_user.id)

    # ИСПРАВЛЕНО: УДАЛЕНО МЕШАЮЩЕЕ УВЕДОМЛЕНИЕ О ТОМ, ЧТО АДМИН НА СВЯЗИ
    if is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        return

    text_lower = message.text.lower()
    
    # 1. Реклама
    if "t.me/" in text_lower or "telegram.me/" in text_lower:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 1800), can_send_messages=False)
            bot.send_message(message.chat.id, f"🤫 {message.from_user.first_name} в муте за рекламу!")
        except: pass
        return
        
    # 2. Нежелательные слова
    for word in BAD_WORDS:
        if word in text_lower:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 300), can_send_messages=False)
                bot.send_message(message.chat.id, f"🤐 {message.from_user.first_name} в муте за нежелательные слова!")
            except: pass
            return

# ================= ВЕБ-СЕРВЕР HEALTH CHECK =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Бот работает!".encode('utf-8'))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = ThreadingHTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    set_bot_commands()
    threading.Thread(target=run_health_server, daemon=True).start()
    bot.remove_webhook()
    logger.info("Бот запущен!")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            logger.error(f"Ошибка Polling: {e}. Ожидание перезапуска...")
            time.sleep(5)