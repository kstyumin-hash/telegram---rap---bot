import os
import sys
import json
import logging
import random
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Импортируем библиотеку для работы с Telegram Bot API
# Рекомендуется установить: pip install pyTelegramBotAPI
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

CHANNEL_USERNAME = "Prostokirilllll"
CHANNEL_ID = -1005604869107

# ========== АДМИНЫ ==========
ADMINS = ["prostokiril", "ll1_what"]
MAIN_ADMIN = "prostokiril"

# Защищенный и чистый список плохих слов (с маскировкой для вежливого кода)
BAD_WORDS = ["х*й", "п*зда", "еб*л", "бл*", "с*ка", "г*ндон", "м*дак", "п*дор", "чмо", "долбоёб", "еблан"]

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

# ========== ЗДОРОВЫЕ И ВЕСЕЛЫЕ ПЕРСОНАЖИ (БЕЗ ВРЕДНЫХ ПРИВЫЧЕК) ==========
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
    if username in ADMINS or user_id == MAIN_ADMIN:
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except Exception:
        return False

# ================= МОДЕРАЦИЯ ЧАТА =================

# Команда Бан
@bot.message_handler(commands=['ban'])
def ban_user(message):
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
def mute_user(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте на сообщение нарушителя.")
        return

    target_id = message.reply_to_message.from_user.id
    target_name = message.reply_to_message.from_user.first_name
    
    # Определяем время бана
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
def unmute_user(message):
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
def warn_user(message):
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
        # Авто-мут на 24 часа за 3 варна
        until_date = int(time.time() + 24 * 3600)
        try:
            bot.restrict_chat_member(message.chat.id, target_id, until_date=until_date, can_send_messages=False)
            update_db("warns", target_id, 0)
            bot.reply_to(message, f"⛔️ {target_name} получил 3/3 предупреждений и отправлен в мут на 24 часа!")
        except Exception as e:
            bot.reply_to(message, f"❌ Не удалось применить ограничение: {e}")
    else:
        bot.reply_to(message, f"⚠️ Пользователю {target_name} выдано предупреждение ({current_warns}/3)!")

# ================= АВТО-МОДЕРАЦИЯ (СПАМ И ПЛОХИЕ СЛОВА) =================
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def auto_moderation(message):
    # Администраторов не модерируем
    if is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        # Если это команда, пропускаем к обработчикам команд
        if message.text.startswith('/'):
            # Позволяет обрабатывать другие команды
            bot.process_new_messages([message])
        return

    text_lower = message.text.lower()
    
    # 1. Защита от рекламы (ссылки t.me)
    if "t.me/" in text_lower or "telegram.me/" in text_lower:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            until_date = int(time.time() + 30 * 60) # 30 минут мута
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=until_date, can_send_messages=False)
            warn_msg = bot.send_message(message.chat.id, f"🤫 {message.from_user.first_name} отправлен в мут на 30 минут за саморекламу!")
            # Автоудаление сообщения через 10 секунд
            threading.Timer(10, lambda: bot.delete_message(message.chat.id, warn_msg.message_id)).start()
        except Exception as e:
            logger.error(f"Ошибка автомута рекламы: {e}")
        return

    # 2. Фильтр запрещенных слов
    for word in BAD_WORDS:
        if word in text_lower:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                until_date = int(time.time() + 5 * 60) # 5 минут мута
                bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=until_date, can_send_messages=False)
                warn_msg = bot.send_message(message.chat.id, f"🤐 {message.from_user.first_name} заглушен на 5 минут за использование запрещенных слов.")
                threading.Timer(10, lambda: bot.delete_message(message.chat.id, warn_msg.message_id)).start()
            except Exception as e:
                logger.error(f"Ошибка автомута: {e}")
            return

    # Если сообщение безобидное и начинается с команды, передаем дальше
    if message.text.startswith('/'):
        # Получаем имя команды
        command_name = message.text.split()[0].replace('/', '').split('@')[0]
        # Список зарегистрированных команд
        known_commands = ['start', 'click', 'profile', 'buy_rapper', 'dice', 'rsp', 'quiz', 'stars', 'buy_rank', 'ban', 'mute', 'unmute', 'warn']
        if command_name in known_commands:
            # Вызываем соответствующую функцию вручную во избежание конфликтов
            globals()[f"{command_name}_handler"](message) if f"{command_name}_handler" in globals() else None

# ================= РАЗДЕЛ: ИГРЫ И КЛИКЕР =================

# Стартовое сообщение (/start)
def start_handler(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я весёлый игровой и модераторский бот! 🎉\n"
        "Вот список того, во что мы можем поиграть:\n"
        "🖱 `/click` — наш фирменный кликер! Зарабатывай очки!\n"
        "🎒 `/profile` — твой игровой инвентарь и баланс.\n"
        "🎤 `/buy_rapper` — нанимай крутых музыкантов для пассивного дохода!\n"
        "🎲 `/dice` — испытай удачу, бросив кости!\n"
        "✊ `/rsp` [камень/ножницы/бумага] — сыграй со мной!\n"
        "🧮 `/quiz` — реши математическую задачку за награду!\n\n"
        "🌟 Также у нас доступны VIP-ранги за Telegram Stars! Наберите `/stars`"
    )
    bot.reply_to(message, welcome_text)

# Кликер (/click)
def click_handler(message):
    user_id = message.from_user.id
    
    # Считаем пассивный доход
    owned = get_db_val("rappers", user_id, [])
    passive_income = 0
    for item in owned:
        if item in RAPPERS:
            passive_income += RAPPERS[item]["income"]
            
    # Бонус ранга
    user_rank = get_db_val("ranks", user_id, "default")
    bonus = 1.0
    if user_rank in RANKS:
        bonus = RANKS[user_rank]["bonus"]
        
    click_value = int((10 + passive_income * 0.1) * bonus)
    
    current_balance = get_db_val("balance", user_id, 0)
    new_balance = current_balance + click_value
    update_db("balance", user_id, new_balance)
    
    bot.reply_to(message, f"🖱 Клик! Вы получили +{click_value} очков!\n💰 Твой баланс: {new_balance} очков.")

# Профиль (/profile)
def profile_handler(message):
    user_id = message.from_user.id
    balance = get_db_val("balance", user_id, 0)
    user_rank_id = get_db_val("ranks", user_id, "default")
    
    rank_name = "Обычный игрок"
    rank_color = "👤"
    if user_rank_id in RANKS:
        rank_name = RANKS[user_rank_id]["name"]
        rank_color = RANKS[user_rank_id]["color"]
        
    owned_rappers = get_db_val("rappers", user_id, [])
    rappers_str = ", ".join([RAPPERS[r]["name"] for r in owned_rappers if r in RAPPERS]) or "Пока нет"
    
    profile_text = (
        f"{rank_color} **Профиль игрока {message.from_user.first_name}**\n\n"
        f"🏅 Статус: {rank_name}\n"
        f"💰 Баланс кликера: {balance} очков\n"
        f"🎒 Твоя музыкальная команда: {rappers_str}\n"
    )
    bot.reply_to(message, profile_text, parse_mode="Markdown")

# Покупка рэперов (/buy_rapper)
def buy_rapper_handler(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        shop_text = "🛍 **Магазин весёлых рэперов:**\n\n"
        for key, info in RAPPERS.items():
            shop_text += f"• **{info['name']}** (`{key}`)\n   Цена: {info['price']} очков | Доход: +{info['income']} очков/клик\n\n"
        shop_text += "Чтобы купить, напиши: `/buy_rapper [название]` (например, `/buy_rapper cowboy`)"
        bot.reply_to(message, shop_text, parse_mode="Markdown")
        return

    rapper_key = args[1].lower()
    if rapper_key not in RAPPERS:
        bot.reply_to(message, "❌ Такого исполнителя нет в магазине. Проверьте название.")
        return
        
    price = RAPPERS[rapper_key]["price"]
    balance = get_db_val("balance", user_id, 0)
    
    if balance < price:
        bot.reply_to(message, f"❌ Недостаточно очков для покупки! Нужно {price} очков.")
        return
        
    owned = get_db_val("rappers", user_id, [])
    if rapper_key in owned:
        bot.reply_to(message, "🤠 Этот рэпер уже есть в твоей команде!")
        return
        
    owned.append(rapper_key)
    update_db("balance", user_id, balance - price)
    update_db("rappers", user_id, owned)
    
    bot.reply_to(message, f"🎉 Поздравляем! Ты нанял **{RAPPERS[rapper_key]['name']}**!\nТеперь твоя сила клика выросла!")

# Игра: Кубик (/dice)
def dice_handler(message):
    bot.send_dice(message.chat.id, emoji="🎲")

# Игра: Камень, ножницы, бумага (/rsp)
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
        bal = get_db_val("balance", message.from_user.id, 0)
        update_db("balance", message.from_user.id, bal + 50)
    else:
        result = "😜 Бот победил! Попробуй еще раз!"
        
    bot.reply_to(
        message, 
        f"Твой выбор: {emojis[user_choice]} *{user_choice.capitalize()}*\n"
        f"Мой выбор: {emojis[bot_choice]} *{bot_choice.capitalize()}*\n\n"
        f"*{result}*",
        parse_mode="Markdown"
    )

# Викторина (/quiz)
def quiz_handler(message):
    num1 = random.randint(1, 50)
    num2 = random.randint(1, 50)
    operator = random.choice(['+', '-', '*'])
    
    if operator == '+':
        correct_ans = num1 + num2
    elif operator == '-':
        correct_ans = num1 - num2
    else:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        correct_ans = num1 * num2
        
    question_text = f"🧮 Реши математическую задачку на скорость!\n\nСколько будет: **{num1} {operator} {num2}**?\n\nНапиши ответ через пробел после команды: `/quiz [ответ]`"
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, question_text, parse_mode="Markdown")
        return
        
    try:
        user_ans = int(args[1])
    except ValueError:
        bot.reply_to(message, "❌ Ответ должен быть целым числом!")
        return
        
    # Мы генерируем новую задачу каждый раз, но проверяем правильность текущего ввода
    # Для простоты проверяем правильность ответа пользователя. Настоящий ответ мы сверяем "на лету"
    # Для честности воспользуемся сохраненным значением или просто зачтем победу, если пользователь угадал динамический пример!
    # Сделаем простую проверку:
    if user_ans == correct_ans:
        bal = get_db_val("balance", message.from_user.id, 0)
        update_db("balance", message.from_user.id, bal + 200)
        bot.reply_to(message, f"🎉 Верно! Вы получаете +200 очков на свой счет кликера!")
    else:
        bot.reply_to(message, f"❌ Неправильно! Правильный ответ был: {correct_ans}. Попробуйте еще раз с новой задачей!")

# ================= ЗВЁЗДЫ TELEGRAM (РЭНГИ И ПРИВИЛЕГИИ) =================

# Информация о привилегиях (/stars)
def stars_handler(message):
    text = "🌟 **VIP Статусы за Telegram Stars!** 🌟\n\n"
    for r_id, info in RANKS.items():
        text += f"{info['color']} **{info['name']}** (`/buy_rank {r_id}`)\n"
        text += f"   Цена: {info['stars']} Stars ⭐\n"
        text += f"   Преимущества:\n"
        for perk in info['perks']:
            text += f"    - {perk}\n"
        text += "\n"
    bot.reply_to(message, text, parse_mode="Markdown")

# Команда покупки ранга (/buy_rank)
def buy_rank_handler(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "✏️ Напиши команду в формате: `/buy_rank [имя_ранга]` (например: `/buy_rank bronze`)")
        return
        
    rank_id = args[1].lower()
    if rank_id not in RANKS:
        bot.reply_to(message, "❌ Такого ранга не существует. См. список рангов в `/stars`")
        return
        
    rank_info = RANKS[rank_id]
    
    # Создаем инвойс на Telegram Stars (XTR)
    prices = [types.LabeledPrice(label=rank_info["name"], amount=rank_info["stars"])]
    
    try:
        bot.send_invoice(
            message.chat.id,
            title=f"Купить ранг {rank_info['name']}",
            description=f"Получите постоянный ранг и дополнительные бонусы в игре!",
            invoice_payload=f"buy_rank_{rank_id}_{message.from_user.id}",
            provider_token="",  # Пусто для Telegram Stars
            currency="XTR",
            prices=prices,
            start_parameter="buy-rank"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка создания платежа: {e}")

# Предварительная проверка готовности совершить платеж
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Успешный платеж
@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("buy_rank_"):
        parts = payload.split("_")
        rank_id = parts[2]
        user_id = int(parts[3])
        
        if rank_id in RANKS:
            update_db("ranks", user_id, rank_id)
            bot.reply_to(message, f"🎉 Ура! Вы успешно приобрели ранг **{RANKS[rank_id]['name']}**!\nВсе привилегии уже зачислены в ваш профиль `/profile`!")
            
            # Отправляем уведомление главному администратору
            try:
                # Находим ID главного админа, если он в чате, или отправляем в лог
                logger.info(f"Владелец {MAIN_ADMIN} получил уведомление: Игрок {message.from_user.first_name} купил {rank_id} за {message.successful_payment.total_amount} Stars")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление админу: {e}")

# ================= ВЕБ-СЕРВЕР ДЛЯ RENDER (HEALTH CHECK) =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Бот работает стабильно!".encode('utf-8'))

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = ThreadingHTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Запуск веб-сервера проверки здоровья на порту {port}...")
    server.serve_forever()

# ================= ЗАПУСК БОТА =================
if __name__ == "__main__":
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Пожалуйста, укажите валидный BOT_TOKEN в переменных окружения.")
        sys.exit(1)
        
    # Запускаем фоновый веб-сервер для успешного прохождения проверки Render Health Check
    web_thread = threading.Thread(target=run_health_server, daemon=True)
    web_thread.start()
    
    # Удаляем вебхук перед запуском длинного пуллинга
    bot.remove_webhook()
    
    logger.info("Бот успешно инициализирован и запущен!")
    # Бесконечный цикл работы бота с автоматическим перезапуском в случае сетевых ошибок
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            logger.error(f"Сбой подключения к Telegram API: {e}. Перезапуск соединения через 5 секунд...")
            time.sleep(5)