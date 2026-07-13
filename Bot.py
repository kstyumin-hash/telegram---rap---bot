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
# Никнейм главного владельца (без собаки)
OWNER_USERNAME = "prostokiril" 

# Список администраторов (изначально пустой, владелец может добавлять их через /admin)
# Сохраняется в базу данных, чтобы не слетать при перезапуске
# По умолчанию prostokiril и ll1_what уже имеют доступ
DEFAULT_ADMINS = ["prostokiril", "ll1_what"]

# Чистый, безопасный и дружелюбный список нежелательных слов
BAD_WORDS = ["дурак", "глупый", "плохой", "редиска", "какашка", "обидчик"]

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
    "electro": {"name": "⚡ Electro-Rapper", "price": 50000, "income": 500}
}

# ================= СОХРАНЕНИЕ И ЗАГРУЗКА ДАННЫХ =================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "admins" not in data:
                    data["admins"] = DEFAULT_ADMINS
                return data
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
    return {
        "warns": {},
        "mutes": {},
        "ranks": {},
        "balance": {},
        "rappers": {},
        "admins": DEFAULT_ADMINS
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

# Проверка, является ли пользователь админом
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

# Синяя кнопка "Меню"
def set_bot_commands():
    try:
        commands = [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("click", "Кликнуть (заработать очки)"),
            types.BotCommand("profile", "Игровой профиль"),
            types.BotCommand("buy_rapper", "Магазин рэперов"),
            types.BotCommand("dice", "Играть в кости"),
            types.BotCommand("rsp", "Камень, Ножницы, Бумага"),
            types.BotCommand("quiz", "Математическая викторина"),
            types.BotCommand("stars", "VIP ранги за звезды"),
            types.BotCommand("ai", "Задать вопрос ИИ"),
            types.BotCommand("admin", "🔐 Админ-панель управления"),
            types.BotCommand("ban", "Бан (админ)"),
            types.BotCommand("mute", "Мут (админ)"),
            types.BotCommand("unmute", "Размут (админ)"),
            types.BotCommand("warn", "Варн (админ)")
        ]
        bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Не удалось установить команды: {e}")

# ================= АДМИН ПАНЕЛЬ КНОПКИ =================
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
    
    # Кнопки управления админами доступны ТОЛЬКО для OWNER_USERNAME
    if username and username.lower() == OWNER_USERNAME.lower():
        markup.add(
            types.InlineKeyboardButton("➕ Назначить Админа", callback_data="adm_add_admin"),
            types.InlineKeyboardButton("➖ Снять Админа", callback_data="adm_remove_admin")
        )
        
    bot.send_message(message.chat.id, "🔐 **Панель управления Ботом**\nВыберите действие ниже:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    username = call.from_user.username
    # Проверка прав доступа к колбэкам
    if not is_user_admin(call.message.chat.id, call.from_user.id, username):
        bot.answer_callback_query(call.id, "❌ У вас нет прав!", show_alert=True)
        return

    action = call.data
    
    if action == "adm_give_money":
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя и сумму через пробел.\nНапример, чтобы выдать себе (ваш ID указан в профиле):\n`12345678 5000`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_admin_money)
    elif action == "adm_give_rank":
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя и код ранга (bronze, silver, gold, platinum, legend) через пробел:\nПример: `12345678 legend`")
        bot.register_next_step_handler(msg, process_admin_rank)
    elif action == "adm_give_rapper":
        msg = bot.send_message(call.message.chat.id, "Введите ID пользователя и код рэпера (cowboy, beatboxer, dj_cloud, electro) через пробел:\nПример: `12345678 electro`")
        bot.register_next_step_handler(msg, process_admin_rapper)
    
    # Проверка на владельца для кнопок управления админами
    elif action == "adm_add_admin":
        if not username or username.lower() != OWNER_USERNAME.lower():
            bot.answer_callback_query(call.id, "❌ Только Владелец бота @prostokiril может делать это!", show_alert=True)
            return
        msg = bot.send_message(call.message.chat.id, "Введите юзернейм нового админа (без знака @):\nПример: `ll1_what`")
        bot.register_next_step_handler(msg, process_add_admin)
    elif action == "adm_remove_admin":
        if not username or username.lower() != OWNER_USERNAME.lower():
            bot.answer_callback_query(call.id, "❌ Только Владелец бота @prostokiril может делать это!", show_alert=True)
            return
        msg = bot.send_message(call.message.chat.id, "Введите юзернейм админа, которого нужно снять (без @):")
        bot.register_next_step_handler(msg, process_remove_admin)

def process_admin_money(message):
    try:
        uid, amount = message.text.split()
        amount = int(amount)
        current = get_db_val("balance", uid, 0)
        update_db("balance", uid, current + amount)
        bot.reply_to(message, f"✅ Баланс пользователя `{uid}` успешно увеличен на {amount} очков!", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Ошибка ввода. Формат: `[ID] [Количество]`")

def process_admin_rank(message):
    try:
        uid, rank_id = message.text.split()
        rank_id = rank_id.lower()
        if rank_id in RANKS:
            update_db("ranks", uid, rank_id)
            bot.reply_to(message, f"✅ Пользователю `{uid}` выдан ранг {RANKS[rank_id]['name']}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Такого ранга нет.")
    except:
        bot.reply_to(message, "❌ Ошибка ввода. Формат: `[ID] [ранг]`")

def process_admin_rapper(message):
    try:
        uid, rapper_id = message.text.split()
        rapper_id = rapper_id.lower()
        if rapper_id in RAPPERS:
            owned = get_db_val("rappers", uid, [])
            if rapper_id not in owned:
                owned.append(rapper_id)
                update_db("rappers", uid, owned)
            bot.reply_to(message, f"✅ Пользователю `{uid}` выдан рэпер {RAPPERS[rapper_id]['name']}!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Такого рэпера нет.")
    except:
        bot.reply_to(message, "❌ Ошибка ввода. Формат: `[ID] [рэпер]`")

def process_add_admin(message):
    target_username = message.text.strip().replace("@", "")
    with db_lock:
        admins = db.get("admins", [])
        if target_username.lower() not in [a.lower() for a in admins]:
            admins.append(target_username)
            db["admins"] = admins
            save_data(db)
            bot.reply_to(message, f"👑 Пользователь @{target_username} успешно добавлен в список администраторов бота!")
        else:
            bot.reply_to(message, "⚠️ Этот пользователь уже является админом.")

def process_remove_admin(message):
    target_username = message.text.strip().replace("@", "")
    if target_username.lower() == OWNER_USERNAME.lower():
        bot.reply_to(message, "❌ Нельзя снять статус создателя с самого себя!")
        return
    with db_lock:
        admins = db.get("admins", [])
        filtered_admins = [a for a in admins if a.lower() != target_username.lower()]
        if len(filtered_admins) < len(admins):
            db["admins"] = filtered_admins
            save_data(db)
            bot.reply_to(message, f"🚫 Пользователь @{target_username} успешно удален из списка администраторов.")
        else:
            bot.reply_to(message, "❌ Данный пользователь не был найден в списке админов.")

# ================= ПРОФИЛЬ (ОБНОВЛЕН С ОТОБРАЖЕНИЕМ СТАТУСА ВЛАДЕЛЬЦА) =================
@bot.message_handler(commands=['profile'])
def profile_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username
    balance = get_db_val("balance", user_id, 0)
    user_rank_id = get_db_val("ranks", user_id, "default")
    
    # Проверка кастомных глобальных статусов
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
        f"🆔 Ваш ID (нужен для админов): `{user_id}`\n"
        f"💰 Баланс кликера: {balance} очков\n"
        f"🎒 Ваша музыкальная команда: {rappers_str}\n"
    )
    bot.reply_to(message, profile_text, parse_mode="Markdown")

# ================= СТАНДАРТНЫЕ КОМАНДЫ МОДЕРАЦИИ =================
@bot.message_handler(commands=['ban'])
def ban_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ У вас нет админ-прав.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответьте на сообщение нарушителя.")
        return
    try:
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, f"👤 Пользователь заблокирован!")
    except Exception as e: bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['mute'])
def mute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username):
        bot.reply_to(message, "❌ Нет прав.")
        return
    if not message.reply_to_message: return
    args = message.text.split()
    minutes = int(args[1]) if len(args) > 1 and args[1].isdigit() else 15
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=int(time.time() + minutes*60), can_send_messages=False)
        bot.reply_to(message, f"🔇 Мут на {minutes} мин.")
    except Exception as e: bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['unmute'])
def unmute_handler(message):
    if not is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    if not message.reply_to_message: return
    try:
        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        bot.reply_to(message, "🔊 Размучен!")
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
        bot.reply_to(message, "⛔️ 3/3 варнов! Мут на 24 часа.")
    else:
        bot.reply_to(message, f"⚠️ Предупреждение ({current_warns}/3)!")

# ================= ОСТАЛЬНЫЕ ИГРОВЫЕ И ИИ КОМАНДЫ =================
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, f"👋 Привет, {message.from_user.first_name}!\nЯ готов к работе.\nВсе команды доступны в синей кнопке **'Меню'** слева снизу.")

@bot.message_handler(commands=['click'])
def click_handler(message):
    user_id = message.from_user.id
    owned = get_db_val("rappers", user_id, [])
    passive = sum([RAPPERS[item]["income"] for item in owned if item in RAPPERS])
    user_rank = get_db_val("ranks", user_id, "default")
    bonus = RANKS[user_rank]["bonus"] if user_rank in RANKS else 1.0
    val = int((10 + passive * 0.1) * bonus)
    new_bal = get_db_val("balance", user_id, 0) + val
    update_db("balance", user_id, new_bal)
    bot.reply_to(message, f"🖱 +{val} очков! Баланс: {new_bal}")

@bot.message_handler(commands=['buy_rapper'])
def buy_rapper_handler(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        text = "🛍 **Магазин рэперов:**\n\n"
        for k, v in RAPPERS.items(): text += f"• `{k}` — {v['name']} (Цена: {v['price']})\n"
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
        else: bot.reply_to(message, "❌ Недостаточно очков.")

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

@bot.message_handler(commands=['quiz'])
def quiz_handler(message):
    n1, n2 = random.randint(1,20), random.randint(1,20)
    ans = n1 + n2
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, f"🧮 Сколько будет {n1} + {n2}?\nОтвет: `/quiz [число]`", parse_mode="Markdown")
        return
    if args[1].isdigit() and int(args[1]) == ans:
        update_db("balance", message.from_user.id, get_db_val("balance", message.from_user.id, 0) + 200)
        bot.reply_to(message, "🎉 Верно! +200 очков.")
    else: bot.reply_to(message, "❌ Неверно!")

@bot.message_handler(commands=['stars'])
def stars_handler(message):
    text = "🌟 **VIP Статусы за Telegram Stars:**\n\n"
    for k, v in RANKS.items(): text += f"• `{k}` — {v['name']} ({v['stars']} Stars ⭐)\n"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['buy_rank'])
def buy_rank_handler(message):
    args = message.text.split()
    if len(args) < 2 or args[1].lower() not in RANKS: return
    rank_id = args[1].lower()
    prices = [types.LabeledPrice(label=RANKS[rank_id]["name"], amount=RANKS[rank_id]["stars"])]
    bot.send_invoice(message.chat.id, title=RANKS[rank_id]["name"], description="VIP", invoice_payload=f"buy_rank_{rank_id}_{message.from_user.id}", provider_token="", currency="XTR", prices=prices)

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query): bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("buy_rank_"):
        parts = payload.split("_")
        update_db("ranks", int(parts[3]), parts[2])
        bot.reply_to(message, "🎉 Ранг зачислен!")

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

# ================= АВТО-МОДЕРАЦИЯ И ПЛОХИЕ СЛОВА =================
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def auto_moderation(message):
    if is_user_admin(message.chat.id, message.from_user.id, message.from_user.username): return
    text_lower = message.text.lower()
    if "t.me/" in text_lower or "telegram.me/" in text_lower:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 1800), can_send_messages=False)
            bot.send_message(message.chat.id, f"🤫 {message.from_user.first_name} в муте на 30 мин за рекламу!")
        except: pass
        return
    for word in BAD_WORDS:
        if word in text_lower:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time() + 300), can_send_messages=False)
                bot.send_message(message.chat.id, f"🤐 {message.from_user.first_name} в муте на 5 мин за нежелательные слова!")
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
        try: bot.polling(none_stop=True, interval=0, timeout=60)
        except: time.sleep(5)