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

# ========== АДМИНЫ ==========
ADMINS = ["prostokiril", "ll1_what"]
MAIN_ADMIN = "prostokiril"

# Защищенный список плохих слов
BAD_WORDS = ["хуй", "пизда", "ебал", "бля", "сука", "гандон", "мудак", "пидор", "чмо", "долбоёб", "еблан"]

# Путь к файлу базы данных (адаптировано для Render)
if os.environ.get('RENDER'):
    DATA_FILE = '/tmp/bot_data.json'
else:
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.json")

# ========== РАНГИ ЗА ЗВЕЗДЫ TELEGRAM ==========
RANKS = {
    "bronze": {
        "name": "🥉 Бронзовый",
        "stars": 10,
        "bonus": 1.1,
        "color": "🟤",
        "perks": ["+10% к доходу", "Бронзовый статус в профиле"]
    },
    "silver": {
        "name": "🥈 Серебряный",
        "stars": 25,
        "bonus": 1.25,
        "color": "⚪",
        "perks": ["+25% к доходу", "Серебряный статус", "x1.2 к удаче"]
    },
    "gold": {
        "name": "🥇 Золотой",
        "stars": 50,
        "bonus": 1.5,
        "color": "🟡",
        "perks": ["+50% к доходу", "Золотой статус", "VIP доступ"]
    },
    "platinum": {
        "name": "💎 Платиновый",
        "stars": 100,
        "bonus": 2.0,
        "color": "🔵",
        "perks": ["+100% к доходу", "Платиновый статус", "Эксклюзивные функции"]
    },
    "legend": {
        "name": "👑 Легендарный",
        "stars": 200,
        "bonus": 3.0,
        "color": "🔴",
        "perks": ["+200% к доходу", "Легендарный статус", "Имя в топе"]
    }
}

# ========== ПЕРСОНАЖИ ==========
RAPPERS = {
    "cowboy": {"name": "🤠 CowboyClicker", "price": 1000, "income": 5},
    "beatboxer": {"name": "🎤 BeatBoxer", "price": 5000, "income": 30},
    "dj_cloud": {"name": "🎧 DJ Cloud", "price": 15000, "income": 100},
    "electro": {"name": "⚡ Electro-Rapper", "price": 50000, "income": 500}
}

# ================= СОХРАНЕНИЕ И ЗАГРУЗКА ДАННЫХ =================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
    return {
        "warns": {},
        "mutes": {},
        "ranks": {},
        "balance": {},
        "rappers": {},
        "last_click": {}
    }

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")

# Инициализируем данные
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

# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================
def is_user_admin(chat_id, user_id, username=None):
    if username in ADMINS:
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

# Настройка меню команд (синяя кнопка "Меню")
def set_bot_commands():
    try:
        commands = [
            types.BotCommand("start", "Запустить бота и получить приветствие"),
            types.BotCommand("click", "Заработать очки в кликере"),
            types.BotCommand("profile", "Посмотреть свой игровой профиль"),
            types.BotCommand("buy_rapper", "Купить рэпера в команду"),
            types.BotCommand("dice", "Испытать удачу (кости)"),
            types.BotCommand("rsp", "Сыграть в Камень, Ножницы, Бумага"),
            types.BotCommand("quiz", "Математическая викторина"),
            types.BotCommand("stars", "Информация о VIP рангах"),
            types.BotCommand("buy_rank", "Купить VIP ранг за звезды"),
            types.BotCommand("ai", "Задать вопрос ИИ"),
            types.BotCommand("ban", "Забанить пользователя (админ)"),
            types.BotCommand("mute", "Замутить пользователя (админ)"),
            types.BotCommand("unmute", "Размутить пользователя (админ)"),
            types.BotCommand("warn", "Выдать варн пользователю (админ)")
        ]
        bot.set_my_commands(commands)
        logger.info("Синяя кнопка 'Меню' с командами успешно настроена!")
    except Exception as e:
        logger.error(f"Не удалось установить команды меню: {e}")

# ================= МОДЕРАЦИЯ ЧАТА =================

# Команда Бан
@bot.message_handler(commands=['ban'])
def ban_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ Эта команда доступна только администраторам.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте этой командой на сообщение пользователя, которого нужно забанить.")
        return
    
    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    try:
        bot.ban_chat_member(message.chat.id, target_id)
        bot.reply_to(message, f"👤 Пользователь {target_name} успешно заблокирован!")
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось заблокировать пользователя: {e}")

# Команда Мут
@bot.message_handler(commands=['mute'])
def mute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте на сообщение нарушителя.")
        return

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    args = message.text.split()
    minutes = 15
    if len(args) > 1 and args[1].isdigit():
        minutes = int(args[1])
        
    until_date = int(time.time() + minutes * 60)
    
    try:
        bot.restrict_chat_member(
            message.chat.id, 
            target_id, 
            until_date=until_date,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False
        )
        bot.reply_to(message, f"🔇 Пользователь {target_name} отправлен в мут на {minutes} минут.")
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось выдать мут: {e}")

# Команда Размут
@bot.message_handler(commands=['unmute'])
def unmute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ У вас нет прав.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте на сообщение пользователя.")
        return

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    try:
        bot.restrict_chat_member(
            message.chat.id,
            target_id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        bot.reply_to(message, f"🔊 Пользователь {target_name} размучен!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка размута: {e}")

# Команда Варн (Предупреждение)
@bot.message_handler(commands=['warn'])
def warn_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ Эта команда только для админов.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте на сообщение нарушителя.")
        return

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    current_warns = get_db_val("warns", target_id, 0) + 1
    update_db("warns", target_id, current_warns)
    
    if current_warns >= 3:
        until_date = int(time.time() + 24 * 3600)
        try:
            bot.restrict_chat_member(message.chat.id, target_id, until_date=until_date, can_send_messages=False)
            update_db("warns", target_id, 0)
            bot.reply_to(message, f"⛔️ {target_name} получил 3/3 предупреждений и отправлен в мут на 24 часа!")
        except Exception as e:
            bot.reply_to(message, f"❌ Не удалось применить ограничение: {e}")
    else:
        bot.reply_to(message, f"⚠️ Пользователю {target_name} выдано предупреждение ({current_warns}/3)!")

# ================= РАЗДЕЛ: ИИ ФУНКЦИЯ (/ai) =================
@bot.message_handler(commands=['ai'])
def ai_handler(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "🤖 Пожалуйста, напишите ваш вопрос после команды.\nПример: `/ai почему небо синее?`", parse_mode="Markdown")
        return
        
    user_query = args[1]
    msg_waiting = bot.reply_to(message, "🤖 *ИИ думает...* Пожалуйста, подождите.", parse_mode="Markdown")
    
    # Имитируем умные ИИ-ответы на базе встроенных текстовых шаблонов
    responses = [
        f"🤖 Проанализировав ваш запрос '{user_query}', могу сказать, что это отличная мысль! Всё указывает на то, что оптимизация — ключ к успеху любого проекта.",
        f"🤖 Хм, интересный вопрос! Что касается '{user_query}', здесь важно учитывать баланс сил. Например, в нашем кликере пассивный доход всегда решает проблемы быстрее!",
        f"🤖 База данных ИИ подсказывает: '{user_query}' — это тема, требующая детального изучения. Но помните, что лучший ответ всегда кроется в практике и хорошем коде!",
        f"🤖 Мои нейронные сети обработали запрос по поводу '{user_query}'. Статистика говорит, что 99% ботов на Render одобряют такой ход мыслей!"
    ]
    
    final_response = random.choice(responses)
    
    # Изменяем сообщение на готовый ответ от "ИИ"
    try:
        bot.edit_message_text(final_response, chat_id=message.chat.id, message_id=msg_waiting.message_id)
    except Exception as e:
        logger.error(f"Ошибка изменения сообщения ИИ: {e}")

# ================= СТАРТ И КЛИКЕР ФУНКЦИИ =================
@bot.message_handler(commands=['start'])
def start_handler(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я весёлый игровой и модераторский бот! 🎉\n"
        "Нажмите на синюю кнопку **'Меню'** в левом нижнем углу чата, чтобы увидеть все доступные команды!\n\n"
        "🖱 `/click` — наш фирменный кликер! Зарабатывай очки!\n"
        "🎒 `/profile` — твой игровой инвентарь и баланс.\n"
        "🤖 `/ai [ваш вопрос]` — спросить нашего встроенного ИИ!\n"
        "🌟 Также у нас доступны VIP-ранги за Telegram Stars! Наберите `/stars`"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['click'])
def click_handler(message):
    user_id = message.from_user.id
    owned = get_db_val("rappers", user_id, [])
    passive_income = sum([RAPPERS[item]["income"] for item in owned if item in RAPPERS])
            
    user_rank = get_db_val("ranks", user_id, "default")
    bonus = RANKS[user_rank]["bonus"] if user_rank in RANKS else 1.0
        
    click_value = int((10 + passive_income * 0.1) * bonus)
    new_balance = get_db_val("balance", user_id, 0) + click_value
    update_db("balance", user_id, new_balance)
    
    bot.reply_to(message, f"🖱 Клик! Вы получили +{click_value} очков!\n💰 Твой баланс: {new_balance} очков.")

@bot.message_handler(commands=['profile'])
def profile_handler(message):
    user_id = message.from_user.id
    balance = get_db_val("balance", user_id, 0)
    user_rank_id = get_db_val("ranks", user_id, "default")
    
    rank_name = RANKS[user_rank_id]["name"] if user_rank_id in RANKS else "Обычный игрок"
    rank_color = RANKS[user_rank_id]["color"] if user_rank_id in RANKS else "👤"
        
    owned_rappers = get_db_val("rappers", user_id, [])
    rappers_str = ", ".join([RAPPERS[r]["name"] for r in owned_rappers if r in RAPPERS]) or "Пока нет"
    
    profile_text = (
        f"{rank_color} **Профиль игрока {message.from_user.first_name}**\n\n"
        f"🏅 Статус: {rank_name}\n"
        f"💰 Баланс кликера: {balance} очков\n"
        f"🎒 Твоя музыкальная команда: {rappers_str}\n"
    )
    bot.reply_to(message, profile_text, parse_mode="Markdown")

@bot.message_handler(commands=['buy_rapper'])
def buy_rapper_handler(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        shop_text = "🛍 **Магазин весёлых рэперов:**\n\n"
        for key, info in RAPPERS.items():
            shop_text += f"• **{info['name']}** (`{key}`)\n   Цена: {info['price']} | Доход: +{info['income']} очков/клик\n\n"
        shop_text += "Чтобы купить, напиши: `/buy_rapper [название]`"
        bot.reply_to(message, shop_text, parse_mode="Markdown")
        return

    rapper_key = args[1].lower()
    if rapper_key not in RAPPERS:
        bot.reply_to(message, "❌ Такого исполнителя нет.")
        return
        
    price = RAPPERS[rapper_key]["price"]
    balance = get_db_val("balance", user_id, 0)
    
    if balance < price:
        bot.reply_to(message, f"❌ Недостаточно очков! Нужно {price} очков.")
        return
        
    owned = get_db_val("rappers", user_id, [])
    if rapper_key in owned:
        bot.reply_to(message, "🤠 Этот рэпер уже в твоей команде!")
        return
        
    owned.append(rapper_key)
    update_db("balance", user_id, balance - price)
    update_db("rappers", user_id, owned)
    bot.reply_to(message, f"🎉 Ты нанял **{RAPPERS[rapper_key]['name']}**!")

@bot.message_handler(commands=['dice'])
def dice_handler(message):
    bot.send_dice(message.chat.id, emoji="🎲")

@bot.message_handler(commands=['rsp'])
def rsp_handler(message):
    args = message.text.split()
    choices = ["камень", "ножницы", "бумага"]
    if len(args) < 2 or args[1].lower() not in choices:
        bot.reply_to(message, "✊✌️ Использование: `/rsp камень`, `/rsp ножницы` или `/rsp бумага`")
        return
    user_choice = args[1].lower()
    bot_choice = random.choice(choices)
    emojis = {"камень": "🪨", "ножницы": "✂️", "бумага": "📄"}
    
    if user_choice == bot_choice:
        result = "🤝 У нас ничья!"
    elif (user_choice == "камень" and bot_choice == "ножницы") or \
         (user_choice == "ножницы" and bot_choice == "бумага") or \
         (user_choice == "бумага" and bot_choice == "камень"):
        result = "🎉 Ты победил! Получаешь +50 очков!"
        update_db("balance", message.from_user.id, get_db_val("balance", message.from_user.id, 0) + 50)
    else:
        result = "😜 Бот победил!"
    bot.reply_to(message, f"Твой выбор: {emojis[user_choice]}\nМой выбор: {emojis[bot_choice]}\n\n*{result}*", parse_mode="Markdown")

@bot.message_handler(commands=['quiz'])
def quiz_handler(message):
    num1, num2 = random.randint(1, 20), random.randint(1, 20)
    correct_ans = num1 + num2
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, f"🧮 Сколько будет: **{num1} + {num2}**?\nНапиши ответ: `/quiz [ответ]`", parse_mode="Markdown")
        return
    try:
        if int(args[1]) == correct_ans:
            update_db("balance", message.from_user.id, get_db_val("balance", message.from_user.id, 0) + 200)
            bot.reply_to(message, "🎉 Верно! +200 очков!")
        else:
            bot.reply_to(message, "❌ Неверно!")
    except:
        bot.reply_to(message, "❌ Введите число.")

@bot.message_handler(commands=['stars'])
def stars_handler(message):
    text = "🌟 **VIP Статусы за Telegram Stars!** 🌟\n\n"
    for r_id, info in RANKS.items():
        text += f"{info['color']} **{info['name']}** (`/buy_rank {r_id}`)\n Цена: {info['stars']} Stars ⭐\n\n"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['buy_rank'])
def buy_rank_handler(message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() not in RANKS:
        bot.reply_to(message, "❌ Напишите: `/buy_rank [имя_ранга]`")
        return
    rank_id = args[1].lower()
    prices = [types.LabeledPrice(label=RANKS[rank_id]["name"], amount=RANKS[rank_id]["stars"])]
    bot.send_invoice(message.chat.id, title=RANKS[rank_id]["name"], description="Покупка VIP ранга", invoice_payload=f"buy_rank_{rank_id}_{message.from_user.id}", provider_token="", currency="XTR", prices=prices)

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("buy_rank_"):
        parts = payload.split("_")
        update_db("ranks", int(parts[3]), parts[2])
        bot.reply_to(message, f"🎉 Вы получили ранг {RANKS[parts[2]]['name']}!")

# ================= АВТО-МОДЕРАЦИЯ (СПАМ И ПЛОХИЕ СЛОВА) =================
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def auto_moderation(message):
    if is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        return

    text_lower = message.text.lower()
    if "t.me/" in text_lower or "telegram.me/" in text_lower:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 1800), can_send_messages=False)
            bot.send_message(message.chat.id, f"🤫 {message.from_user.first_name} в муте на 30 мин за рекламу!")
        except Exception as e: logger.error(e)
        return

    for word in BAD_WORDS:
        if word in text_lower:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 300), can_send_messages=False)
                bot.send_message(message.chat.id, f"🤐 {message.from_user.first_name} в муте на 5 мин за маты!")
            except Exception as e: logger.error(e)
            return

# ================= ВЕБ-СЕРВЕР =================
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
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            time.sleep(5)
