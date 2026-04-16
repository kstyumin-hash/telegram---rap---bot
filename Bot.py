import os
import sys
import signal
import time
import threading
import logging
import json
import requests
import random
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections import defaultdict

# ================= ЛОГИРОВАНИЕ =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= ПУТЬ К ФАЙЛУ ДАННЫХ =================
if os.environ.get('RENDER'):
    DATA_FILE = '/tmp/bot_data.json'
else:
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.json")

# ================= НАСТРОЙКИ =================
TOKEN = os.environ.get("8493334113:AAG0xhH5SEZ72APG4WrUjRrBAj1ilUWyZPo")
if not TOKEN:
    logger.error("❌ ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"

CHANNEL_USERNAME = "Prostokirilllll"
CHANNEL_ID = -1005604869107

ADMINS = ["prostokiril", "ll1_what"]
MAIN_ADMIN = "prostokiril"
ADDITIONAL_ADMINS = []

BAD_WORDS = ["хуй", "пизда", "ебал", "бля", "сука", "гондон", "мудак", "пидор", "чмо", "долбоёб", "еблан"]

print("=" * 60)
print("🎵 ULTIMATE RAP BOSS + CHAT MODERATOR")
print("=" * 60)
print(f"👑 Главный админ: @{MAIN_ADMIN}")
print(f"👑 Второй админ: @{ADMINS[1]}")
print(f"📢 Канал: @{CHANNEL_USERNAME}")
print(f"🆔 ID канала: {CHANNEL_ID}")
print(f"💾 Файл данных: {DATA_FILE}")
print("=" * 60)

# ================= БАЗЫ ДАННЫХ =================
users_db = {}
messages_db = {}
daily_bonus_db = {}
user_items = defaultdict(list)
chat_warnings = defaultdict(int)
last_message_time = defaultdict(float)
muted_users = {}
banned_users = {}
lottery_jackpot = 10000
gangs_db = defaultdict(dict)
rap_battles = []
duel_requests = defaultdict(list)
user_stocks = defaultdict(dict)
admin_notifications = []
private_messages = defaultdict(list)
active_games = {}

# ================= РАНГИ =================
RANKS = {
    "bronze": {"name": "🥉 Бронзовый", "stars": 10, "bonus": 1.1, "color": "🟤", "perks": ["+10% к доходу", "Бронзовый скин"]},
    "silver": {"name": "🥈 Серебряный", "stars": 25, "bonus": 1.25, "color": "⚪", "perks": ["+25% к доходу", "Серебряный скин"]},
    "gold": {"name": "🥇 Золотой", "stars": 50, "bonus": 1.5, "color": "🟡", "perks": ["+50% к доходу", "Золотой скин"]},
    "platinum": {"name": "💎 Платиновый", "stars": 100, "bonus": 2.0, "color": "🔵", "perks": ["+100% к доходу", "Платиновый скин"]},
    "legend": {"name": "👑 Легендарный", "stars": 200, "bonus": 3.0, "color": "🔴", "perks": ["+200% к доходу", "Легендарный скин"]}
}

# ================= РЭПЕРЫ =================
RAPPERS = {
    "cowboy": {"name": "🐮 CowboyClicker", "price": 10000, "income": 100},
    "smoke": {"name": "💨 SmokeDope", "price": 15000, "income": 150},
    "liltrap": {"name": "🎤 Lil Trap", "price": 8000, "income": 80},
    "cloudy": {"name": "☁️ Cloudy", "price": 12000, "income": 120},
    "sadboy": {"name": "😢 SadBoy", "price": 5000, "income": 50},
    "ghost": {"name": "👻 GhostFace", "price": 20000, "income": 200},
    "money": {"name": "💰 MoneyBag", "price": 25000, "income": 250},
    "ice": {"name": "🧊 IceCold", "price": 18000, "income": 180},
    "fire": {"name": "🔥 FireBoy", "price": 22000, "income": 220},
    "diamond": {"name": "💎 Diamond", "price": 30000, "income": 300},
}

# ================= БАНДЫ =================
GANGS = {
    "bloods": {"name": "🔴 Bloods", "bonus": 1.2, "members": []},
    "crips": {"name": "🔵 Crips", "bonus": 1.15, "members": []},
    "mafia": {"name": "⚫ Mafia", "bonus": 1.25, "members": []},
    "yakuza": {"name": "🗡️ Yakuza", "bonus": 1.3, "members": []},
}

# ================= НЕЛЕГАЛЬНЫЙ БИЗНЕС =================
ILLEGAL_JOBS = {
    "weed": {"name": "🌿 Продажа травы", "min": 1000, "max": 5000, "risk": 0.3},
    "counterfeit": {"name": "💸 Фальшивые деньги", "min": 5000, "max": 20000, "risk": 0.5},
    "hacking": {"name": "💻 Взлом банков", "min": 10000, "max": 50000, "risk": 0.7},
}

# ================= КРИПТОВАЛЮТА =================
CRYPTO = {
    "bitcoin": {"name": "₿ Bitcoin", "price": 45000, "change": 0.1},
    "ethereum": {"name": "Ξ Ethereum", "price": 3000, "change": 0.15},
    "dogecoin": {"name": "🐕 Dogecoin", "price": 0.15, "change": 0.2},
}

# ================= ПРЕДМЕТЫ =================
ITEMS = {
    "mic": "🎤 Золотой микрофон",
    "chain": "⛓️ Платиновая цепь",
    "car": "🚗 Роллс-Ройс",
    "house": "🏰 Особняк",
    "jet": "✈️ Частный самолет"
}

# ================= ЗАГРУЗКА И СОХРАНЕНИЕ =================
def load_data():
    global users_db, messages_db, daily_bonus_db, chat_warnings, last_message_time
    global muted_users, banned_users, lottery_jackpot, gangs_db, rap_battles
    global user_stocks, admin_notifications, private_messages, duel_requests
    global ADDITIONAL_ADMINS, CRYPTO
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            users_db = {}
            for k, v in data.get('users_db', {}).items():
                try:
                    users_db[int(k)] = v
                except:
                    continue
            
            messages_db = data.get('messages_db', {})
            daily_bonus_db = data.get('daily_bonus_db', {})
            chat_warnings = defaultdict(int, {int(k) if str(k).isdigit() else k: v for k, v in data.get('chat_warnings', {}).items()})
            
            last_message_time_data = data.get('last_message_time', {})
            last_message_time = defaultdict(float)
            for k, v in last_message_time_data.items():
                try:
                    last_message_time[int(k)] = float(v)
                except:
                    pass
            
            muted_users = {}
            for k, v in data.get('muted_users', {}).items():
                try:
                    muted_users[int(k)] = v
                except:
                    pass
            
            banned_users = {}
            for k, v in data.get('banned_users', {}).items():
                try:
                    banned_users[int(k)] = v
                except:
                    pass
            
            lottery_jackpot = data.get('lottery_jackpot', 10000)
            gangs_db = data.get('gangs_db', {})
            rap_battles = data.get('rap_battles', [])
            user_stocks = data.get('user_stocks', {})
            admin_notifications = data.get('admin_notifications', [])
            private_messages = data.get('private_messages', {})
            duel_requests = data.get('duel_requests', {})
            ADDITIONAL_ADMINS = data.get('additional_admins', [])
            
            if 'crypto' in data:
                CRYPTO = data['crypto']
            
            logger.info(f"💾 Данные загружены: {len(users_db)} пользователей")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки: {e}")

def save_data():
    try:
        data = {
            'users_db': {str(k): v for k, v in users_db.items()},
            'messages_db': messages_db,
            'daily_bonus_db': daily_bonus_db,
            'chat_warnings': dict(chat_warnings),
            'last_message_time': {str(k): v for k, v in last_message_time.items()},
            'muted_users': {str(k): v for k, v in muted_users.items()},
            'banned_users': {str(k): v for k, v in banned_users.items()},
            'lottery_jackpot': lottery_jackpot,
            'gangs_db': gangs_db,
            'rap_battles': rap_battles,
            'user_stocks': user_stocks,
            'admin_notifications': admin_notifications,
            'private_messages': private_messages,
            'duel_requests': duel_requests,
            'additional_admins': ADDITIONAL_ADMINS,
            'crypto': CRYPTO,
            'save_time': time.strftime("%d.%m.%Y %H:%M:%S")
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Данные сохранены ({time.strftime('%H:%M:%S')})")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения: {e}")

# ================= ОБРАБОТКА СИГНАЛОВ =================
def signal_handler(sig, frame):
    logger.info("🛑 Получен сигнал завершения. Сохраняем данные...")
    save_data()
    logger.info("✅ Данные сохранены. Завершаем работу.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ================= HTTP СЕРВЕР ДЛЯ RENDER =================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Bot is running!')

    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"✅ HTTP сервер для Render запущен на порту {port}")
    server.serve_forever()

http_thread = threading.Thread(target=run_http_server, daemon=True)
http_thread.start()

# ================= АВТОСОХРАНЕНИЕ =================
def auto_save_loop():
    while True:
        time.sleep(60)
        save_data()

auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
auto_save_thread.start()

# ================= ОБНОВЛЕНИЕ КРИПТЫ =================
def crypto_update_loop():
    global CRYPTO
    while True:
        time.sleep(300)
        for crypto_id in CRYPTO:
            change = random.uniform(-0.1, 0.1)
            CRYPTO[crypto_id]["price"] *= (1 + change)
            CRYPTO[crypto_id]["price"] = max(0.01, CRYPTO[crypto_id]["price"])

crypto_thread = threading.Thread(target=crypto_update_loop, daemon=True)
crypto_thread.start()

# ================= ФУНКЦИИ ДЛЯ TELEGRAM =================
def send_message(chat_id, text, buttons=None, parse_mode="HTML"):
    try:
        url = f"{API_URL}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        if buttons:
            data["reply_markup"] = json.dumps({"inline_keyboard": buttons})
        
        response = requests.post(url, json=data, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return None

def answer_callback_query(callback_id, text=""):
    try:
        requests.post(f"{API_URL}/answerCallbackQuery", 
                     json={"callback_query_id": callback_id, "text": text}, timeout=5)
    except:
        pass

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    try:
        resp = requests.get(f"{API_URL}/getUpdates", params=params, timeout=120)
        return resp.json()
    except Exception as e:
        logger.error(f"❌ Ошибка при получении апдейтов: {e}")
        return {"result": []}

def restrict_chat_member(chat_id, user_id, until_date):
    try:
        requests.post(f"{API_URL}/restrictChatMember",
                     json={
                         "chat_id": chat_id,
                         "user_id": user_id,
                         "permissions": {"can_send_messages": False},
                         "until_date": until_date
                     }, timeout=10)
    except Exception as e:
        logger.error(f"❌ Ошибка мута: {e}")

# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================
def add_admin_notification(text):
    admin_notifications.append({"text": text, "time": time.strftime("%d.%m.%Y %H:%M:%S")})
    if len(admin_notifications) > 50:
        admin_notifications.pop(0)

def check_subscription(user_id):
    try:
        url = f"{API_URL}/getChatMember"
        data = {"chat_id": CHANNEL_ID, "user_id": user_id}
        response = requests.post(url, json=data, timeout=10).json()
        if response.get("ok"):
            status = response["result"]["status"]
            return status in ["member", "administrator", "creator"]
    except:
        pass
    return True

def get_user_data(user_id, username="", first_name="Игрок"):
    user_id = int(user_id)
    
    if user_id not in users_db:
        is_admin = username.lower() in [a.lower() for a in ADMINS + ADDITIONAL_ADMINS]
        admin_index = -1
        
        if is_admin:
            if username.lower() == ADMINS[0].lower():
                admin_index = 0
                badge = "👑"
                rank = "ВЛАДЕЛЕЦ"
            elif username.lower() == ADMINS[1].lower():
                admin_index = 1
                badge = "👑"
                rank = "СО-ВЛАДЕЛЕЦ"
            else:
                admin_index = 2
                badge = "⚡"
                rank = "АДМИН"
            
            users_db[user_id] = {
                "id": user_id, "username": username, "name": first_name,
                "balance": 999999, "rappers": list(RAPPERS.keys()),
                "level": 100, "xp": 999999, "rank": f"{badge} {rank}",
                "purchased_rank": "legend", "stars_spent": 9999,
                "admin": True, "admin_index": admin_index,
                "join_date": time.strftime("%d.%m.%Y"),
                "messages": [], "items": list(ITEMS.keys()),
                "wins": 50, "losses": 0, "gang": "mafia",
                "stocks": {"bitcoin": 10, "ethereum": 50, "dogecoin": 1000},
                "daily_streak": 99, "last_collect": 0
            }
        else:
            users_db[user_id] = {
                "id": user_id, "username": username, "name": first_name,
                "balance": 5000, "rappers": [], "level": 1, "xp": 0,
                "rank": "👤 НОВИЧОК", "purchased_rank": None, "stars_spent": 0,
                "admin": False, "admin_index": -1,
                "join_date": time.strftime("%d.%m.%Y"),
                "messages": [], "items": [], "wins": 0, "losses": 0,
                "gang": None, "stocks": {}, "daily_streak": 0, "last_collect": 0
            }
    
    return users_db[user_id]

def find_user_by_username(username):
    if not username:
        return None
    username_lower = username.lower().lstrip('@')
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    return None

def find_user_by_username_or_get_from_telegram(username):
    if not username:
        return None
    
    username_lower = username.lower().lstrip('@')
    
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    
    try:
        url = f"{API_URL}/getChat"
        params = {"chat_id": f"@{username_lower}"}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return get_user_data(data["result"]["id"], username_lower, data["result"].get("first_name", ""))
    except:
        pass
    return None

def get_income_bonus(user_data):
    bonus = 1.0
    gang = user_data.get("gang")
    if gang and gang in GANGS:
        bonus *= GANGS[gang]["bonus"]
    rank_id = user_data.get("purchased_rank")
    if rank_id and rank_id in RANKS:
        bonus *= RANKS[rank_id]["bonus"]
    return bonus

def get_user_power(user_data):
    power = user_data["level"] * 10
    power += len(user_data.get("rappers", [])) * 50
    rank_id = user_data.get("purchased_rank")
    if rank_id and rank_id in RANKS:
        power = int(power * RANKS[rank_id]["bonus"])
    return power

# ================= ГЛАВНОЕ МЕНЮ =================
def handle_start(chat_id, user_data):
    buttons = [
        [{"text": "👤 ПРОФИЛЬ", "callback_data": "profile"}, {"text": "🛒 МАГАЗИН", "callback_data": "shop"}],
        [{"text": "💰 ДОХОД", "callback_data": "collect"}, {"text": "🎮 ИГРЫ", "callback_data": "games"}],
        [{"text": "⚫ БАНДЫ", "callback_data": "gangs"}, {"text": "₿ КРИПТО", "callback_data": "crypto"}],
        [{"text": "⚔️ ДУЭЛИ", "callback_data": "duel_menu"}, {"text": "🎒 ИНВЕНТАРЬ", "callback_data": "inventory"}],
        [{"text": "🏴‍☠️ НЕЛЕГАЛ", "callback_data": "illegal"}, {"text": "⭐ РАНГИ", "callback_data": "ranks"}],
    ]
    if user_data.get("admin", False):
        buttons.append([{"text": "⚡ АДМИН-ПАНЕЛЬ", "callback_data": "admin_panel"}])
    
    send_message(chat_id,
        f"🎵 <b>ULTIMATE RAP BOSS</b>\n\n"
        f"👤 {user_data['name']} (@{user_data.get('username', 'unknown')})\n"
        f"💰 {user_data['balance']:,} монет\n"
        f"⭐ Уровень: {user_data['level']}\n"
        f"🎤 Рэперов: {len(user_data.get('rappers', []))}\n"
        f"{user_data.get('rank', '👤 НОВИЧОК')}",
        buttons
    )

def handle_profile(chat_id, user_data):
    gang_name = "Нет"
    if user_data.get("gang") and user_data["gang"] in GANGS:
        gang_name = GANGS[user_data["gang"]]["name"]
    
    total_income = sum(RAPPERS[r]["income"] for r in user_data.get("rappers", []) if r in RAPPERS)
    bonus = get_income_bonus(user_data)
    total_income = int(total_income * bonus)
    
    power = get_user_power(user_data)
    
    text = f"👤 <b>ПРОФИЛЬ</b>\n\n"
    text += f"📛 Имя: {user_data['name']}\n"
    text += f"📌 Username: @{user_data.get('username', 'unknown')}\n"
    text += f"🆔 ID: <code>{user_data['id']}</code>\n"
    text += f"📊 Ранг: {user_data.get('rank', '👤 НОВИЧОК')}\n"
    text += f"⭐ Уровень: {user_data['level']}\n"
    text += f"✨ Опыт: {user_data.get('xp', 0):,}\n"
    text += f"💰 Баланс: {user_data['balance']:,} монет\n"
    text += f"💵 Доход/час: {total_income:,} монет\n"
    text += f"🎤 Рэперов: {len(user_data.get('rappers', []))}/{len(RAPPERS)}\n"
    text += f"⚔️ Сила: {power}\n"
    text += f"🏆 Побед: {user_data.get('wins', 0)} | Поражений: {user_data.get('losses', 0)}\n"
    text += f"⚫ Банда: {gang_name}\n"
    text += f"📅 В боте с: {user_data.get('join_date', 'N/A')}\n"
    text += f"🔥 Серия бонусов: {user_data.get('daily_streak', 0)} дней"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

def handle_help(chat_id):
    text = "📖 <b>СПРАВКА ПО БОТУ</b>\n\n"
    text += "🎮 <b>Основные команды:</b>\n"
    text += "/start - Главное меню\n"
    text += "/help - Эта справка\n"
    text += "/profile - Твой профиль\n"
    text += "/shop - Магазин рэперов\n"
    text += "/collect - Собрать доход\n"
    text += "/games - Игры\n"
    text += "/gangs - Группировки\n"
    text += "/crypto - Криптовалюта\n"
    text += "/ranks - Ранги за звёзды\n\n"
    text += "⚔️ <b>Дуэли:</b>\n"
    text += "/duel @user ставка - Вызвать на дуэль\n\n"
    text += "🏴‍☠️ <b>Нелегальный бизнес:</b>\n"
    text += "/illegal - Нелегальные заработки\n\n"
    text += "🤖 <b>Помощь:</b>\n"
    text += "/ai вопрос - ИИ-помощник\n"
    text += "/ask текст - Написать админу"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

# ================= БОНУС =================
def handle_daily_bonus(chat_id, user_data):
    today = time.strftime("%d.%m.%Y")
    user_id = user_data["id"]
    
    if daily_bonus_db.get(str(user_id)) == today:
        send_message(chat_id, "🎁 Ты уже получал бонус сегодня! Приходи завтра.")
        return
    
    streak = user_data.get("daily_streak", 0) + 1
    bonus = 1000 * streak
    if bonus > 10000:
        bonus = 10000
    
    user_data["balance"] += bonus
    user_data["daily_streak"] = streak
    user_data["xp"] = user_data.get("xp", 0) + 50
    daily_bonus_db[str(user_id)] = today
    
    send_message(chat_id,
        f"🎁 <b>ЕЖЕДНЕВНЫЙ БОНУС!</b>\n\n"
        f"💰 Получено: {bonus:,} монет\n"
        f"🔥 Серия: {streak} дней\n"
        f"⭐ Опыт: +50"
    )

# ================= ДОХОД =================
def handle_collect(chat_id, user_data):
    now = time.time()
    last = user_data.get("last_collect", 0)
    elapsed = now - last
    
    if elapsed < 3600:
        remaining = int(3600 - elapsed)
        minutes = remaining // 60
        seconds = remaining % 60
        send_message(chat_id, f"⏰ Доход будет доступен через {minutes} мин {seconds} сек")
        return
    
    total_income = sum(RAPPERS[r]["income"] for r in user_data.get("rappers", []) if r in RAPPERS)
    if total_income == 0:
        send_message(chat_id, "❌ У тебя нет рэперов! Купи их в /shop")
        return
    
    bonus = get_income_bonus(user_data)
    hours = int(elapsed // 3600)
    if hours > 24:
        hours = 24
    earned = int(total_income * bonus * hours)
    
    user_data["balance"] += earned
    user_data["last_collect"] = now
    user_data["xp"] = user_data.get("xp", 0) + 20
    
    send_message(chat_id,
        f"💰 <b>ДОХОД СОБРАН!</b>\n\n"
        f"💵 За {hours} ч: +{earned:,} монет\n"
        f"📊 Бонус: x{bonus:.2f}\n"
        f"💰 Баланс: {user_data['balance']:,}"
    )

# ================= МАГАЗИН =================
def handle_shop(chat_id, user_data):
    buttons = []
    for rapper_id, rapper in RAPPERS.items():
        owned = rapper_id in user_data["rappers"]
        status = "✅" if owned else f"{rapper['price']:,}💰"
        btn_type = f"view_{rapper_id}" if owned else f"buy_{rapper_id}"
        buttons.append([{"text": f"{rapper['name']} - {status}", "callback_data": btn_type}])
    
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id,
        f"🛒 <b>МАГАЗИН РЭПЕРОВ</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,} монет\n"
        f"🎤 Куплено: {len(user_data['rappers'])}/{len(RAPPERS)}",
        buttons
    )

def handle_buy_rapper(chat_id, user_data, rapper_id):
    if rapper_id not in RAPPERS:
        send_message(chat_id, "❌ Рэпер не найден!")
        return
    
    rapper = RAPPERS[rapper_id]
    
    if rapper_id in user_data["rappers"]:
        send_message(chat_id, f"✅ У тебя уже есть {rapper['name']}!")
        return
    
    if user_data["balance"] < rapper["price"]:
        send_message(chat_id,
            f"❌ <b>НЕДОСТАТОЧНО МОНЕТ!</b>\n\n"
            f"Нужно: {rapper['price']:,} монет\n"
            f"У тебя: {user_data['balance']:,} монет"
        )
        return
    
    user_data["balance"] -= rapper["price"]
    user_data["rappers"].append(rapper_id)
    user_data["xp"] = user_data.get("xp", 0) + 100
    
    send_message(chat_id,
        f"🎉 <b>ПОКУПКА УСПЕШНА!</b>\n\n"
        f"{rapper['name']}\n"
        f"💵 Стоимость: {rapper['price']:,} монет\n"
        f"💰 Остаток: {user_data['balance']:,} монет\n"
        f"⭐ Опыт: +100"
    )

def handle_view_rapper(chat_id, user_data, rapper_id):
    if rapper_id not in RAPPERS:
        send_message(chat_id, "❌ Рэпер не найден!")
        return
    
    rapper = RAPPERS[rapper_id]
    bonus = get_income_bonus(user_data)
    real_income = int(rapper["income"] * bonus)
    
    text = f"🎤 <b>{rapper['name']}</b>\n\n"
    text += f"💵 Доход: {rapper['income']}/ч\n"
    text += f"📊 С бонусом: {real_income}/ч\n"
    text += f"✅ Статус: Куплен"
    
    buttons = [[{"text": "🔙 В МАГАЗИН", "callback_data": "shop"}]]
    send_message(chat_id, text, buttons)

# ================= ИГРЫ =================
def handle_games(chat_id, user_data):
    buttons = [
        [{"text": "🎲 К О С Т И", "callback_data": "game_dice"}, {"text": "🎰 С Л О Т Ы", "callback_data": "game_slots"}],
        [{"text": "🪙 ОРЁЛ/РЕШКА", "callback_data": "game_coin"}, {"text": "🪨 КНБ", "callback_data": "game_rps"}],
        [{"text": "🃏 21 ОЧКО", "callback_data": "game_21"}, {"text": "🎰 ЛОТЕРЕЯ", "callback_data": "game_lottery"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id,
        f"🎮 <b>ИГРОВЫЙ ЗАЛ</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,} монет\n"
        f"🎰 Джекпот: {lottery_jackpot:,} монет",
        buttons
    )

def handle_game_dice(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    roll = random.randint(2, 12)
    win = roll in [7, 11]
    
    if win:
        user_data["balance"] += bet
        user_data["wins"] = user_data.get("wins", 0) + 1
        user_data["xp"] = user_data.get("xp", 0) + 10
        result = f"🎲 Выпало: {roll}\n\n🎉 <b>ПОБЕДА! +{bet:,} монет</b>"
    else:
        user_data["balance"] -= bet
        user_data["losses"] = user_data.get("losses", 0) + 1
        result = f"🎲 Выпало: {roll}\n\n💔 <b>ПРОИГРЫШ! -{bet:,} монет</b>"
    
    result += f"\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [
        [{"text": f"🎲 ЕЩЁ РАЗ ({bet:,})", "callback_data": f"dice_{bet}"}],
        [{"text": "🔙 К ИГРАМ", "callback_data": "games"}]
    ]
    send_message(chat_id, result, buttons)

def handle_game_slots(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "👑"]
    weights = [25, 20, 18, 15, 10, 8, 4]
    
    spin = random.choices(symbols, weights=weights, k=3)
    result_str = " | ".join(spin)
    
    if spin[0] == spin[1] == spin[2]:
        if spin[0] == "👑":
            mult = 20
        elif spin[0] == "7️⃣":
            mult = 10
        elif spin[0] == "💎":
            mult = 7
        else:
            mult = 5
        win_amount = bet * mult
        user_data["balance"] += win_amount
        user_data["wins"] = user_data.get("wins", 0) + 1
        user_data["xp"] = user_data.get("xp", 0) + 20
        result = f"🎰 {result_str}\n\n🎉 <b>ДЖЕКПОТ x{mult}! +{win_amount:,} монет</b>"
    elif spin[0] == spin[1] or spin[1] == spin[2]:
        win_amount = bet
        user_data["balance"] += win_amount
        user_data["wins"] = user_data.get("wins", 0) + 1
        user_data["xp"] = user_data.get("xp", 0) + 5
        result = f"🎰 {result_str}\n\n✨ <b>ПАРА! +{win_amount:,} монет</b>"
    else:
        user_data["balance"] -= bet
        user_data["losses"] = user_data.get("losses", 0) + 1
        result = f"🎰 {result_str}\n\n💔 <b>ПРОИГРЫШ! -{bet:,} монет</b>"
    
    result += f"\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [
        [{"text": f"🎰 ЕЩЁ РАЗ ({bet:,})", "callback_data": f"slots_{bet}"}],
        [{"text": "🔙 К ИГРАМ", "callback_data": "games"}]
    ]
    send_message(chat_id, result, buttons)

def handle_game_coin(chat_id, user_data, bet, choice):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    result = random.choice(["орёл", "решка"])
    win = result == choice
    
    if win:
        user_data["balance"] += bet
        user_data["wins"] = user_data.get("wins", 0) + 1
        user_data["xp"] = user_data.get("xp", 0) + 5
        text = f"🪙 Выпало: {result}\n\n🎉 <b>ПОБЕДА! +{bet:,} монет</b>"
    else:
        user_data["balance"] -= bet
        user_data["losses"] = user_data.get("losses", 0) + 1
        text = f"🪙 Выпало: {result}\n\n💔 <b>ПРОИГРЫШ! -{bet:,} монет</b>"
    
    text += f"\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [
        [{"text": "🦅 ОРЁЛ", "callback_data": f"coin_{bet}_орёл"}, {"text": "🦅 РЕШКА", "callback_data": f"coin_{bet}_решка"}],
        [{"text": "🔙 К ИГРАМ", "callback_data": "games"}]
    ]
    send_message(chat_id, text, buttons)

def handle_game_rps(chat_id, user_data, bet, choice):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    options = ["камень", "ножницы", "бумага"]
    bot_choice = random.choice(options)
    
    wins = {"камень": "ножницы", "ножницы": "бумага", "бумага": "камень"}
    emojis = {"камень": "🪨", "ножницы": "✂️", "бумага": "📄"}
    
    if choice == bot_choice:
        text = f"{emojis[choice]} vs {emojis[bot_choice]}\n\n🤝 <b>НИЧЬЯ!</b>"
    elif wins[choice] == bot_choice:
        user_data["balance"] += bet
        user_data["wins"] = user_data.get("wins", 0) + 1
        user_data["xp"] = user_data.get("xp", 0) + 5
        text = f"{emojis[choice]} vs {emojis[bot_choice]}\n\n🎉 <b>ПОБЕДА! +{bet:,} монет</b>"
    else:
        user_data["balance"] -= bet
        user_data["losses"] = user_data.get("losses", 0) + 1
        text = f"{emojis[choice]} vs {emojis[bot_choice]}\n\n💔 <b>ПРОИГРЫШ! -{bet:,} монет</b>"
    
    text += f"\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [
        [{"text": "🪨 КАМЕНЬ", "callback_data": f"rps_{bet}_камень"}, {"text": "✂️ НОЖНИЦЫ", "callback_data": f"rps_{bet}_ножницы"}, {"text": "📄 БУМАГА", "callback_data": f"rps_{bet}_бумага"}],
        [{"text": "🔙 К ИГРАМ", "callback_data": "games"}]
    ]
    send_message(chat_id, text, buttons)

def handle_game_21(chat_id, user_data, bet, action=None, current_hand=None):
    if action is None:
        if user_data["balance"] < bet:
            send_message(chat_id, "❌ Недостаточно монет!")
            return
        
        card1 = random.randint(2, 11)
        card2 = random.randint(2, 11)
        hand = [card1, card2]
        total = sum(hand)
        
        if total == 21:
            user_data["balance"] += bet
            user_data["wins"] = user_data.get("wins", 0) + 1
            user_data["xp"] = user_data.get("xp", 0) + 15
            buttons = [[{"text": "🔙 К ИГРАМ", "callback_data": "games"}]]
            send_message(chat_id, f"🃏 {hand} = {total}\n\n🎉 <b>БЛЭКДЖЕК! +{bet:,} монет</b>\n💰 Баланс: {user_data['balance']:,}", buttons)
            return
        
        buttons = [
            [{"text": "📦 ЕЩЁ КАРТУ", "callback_data": f"21_{bet}_hit_{','.join(map(str, hand))}"}],
            [{"text": "✋ СТОП", "callback_data": f"21_{bet}_stand_{','.join(map(str, hand))}"}]
        ]
        send_message(chat_id, f"🃏 Твои карты: {hand} = {total}\n\n📦 Ещё или стоп?", buttons)
        return
    
    hand = list(map(int, current_hand.split(',')))
    
    if action == "hit":
        new_card = random.randint(2, 11)
        hand.append(new_card)
        total = sum(hand)
        
        if total > 21:
            user_data["balance"] -= bet
            user_data["losses"] = user_data.get("losses", 0) + 1
            buttons = [[{"text": "🔙 К ИГРАМ", "callback_data": "games"}]]
            send_message(chat_id, f"🃏 Твои карты: {hand} = {total}\n\n💔 <b>ПЕРЕБОР! -{bet:,} монет</b>\n💰 Баланс: {user_data['balance']:,}", buttons)
        elif total == 21:
            user_data["balance"] += bet
            user_data["wins"] = user_data.get("wins", 0) + 1
            user_data["xp"] = user_data.get("xp", 0) + 15
            buttons = [[{"text": "🔙 К ИГРАМ", "callback_data": "games"}]]
            send_message(chat_id, f"🃏 Твои карты: {hand} = {total}\n\n🎉 <b>21! +{bet:,} монет</b>\n💰 Баланс: {user_data['balance']:,}", buttons)
        else:
            buttons = [
                [{"text": "📦 ЕЩЁ КАРТУ", "callback_data": f"21_{bet}_hit_{','.join(map(str, hand))}"}],
                [{"text": "✋ СТОП", "callback_data": f"21_{bet}_stand_{','.join(map(str, hand))}"}]
            ]
            send_message(chat_id, f"🃏 Твои карты: {hand} = {total}\n\n📦 Ещё или стоп?", buttons)
    
    elif action == "stand":
        player_total = sum(hand)
        bot_hand = []
        bot_total = 0
        
        while bot_total < 17:
            card = random.randint(2, 11)
            bot_hand.append(card)
            bot_total = sum(bot_hand)
        
        if bot_total > 21 or player_total > bot_total:
            user_data["balance"] += bet
            user_data["wins"] = user_data.get("wins", 0) + 1
            user_data["xp"] = user_data.get("xp", 0) + 10
            result = f"🎉 <b>ПОБЕДА! +{bet:,} монет</b>"
        elif player_total == bot_total:
            result = "🤝 <b>НИЧЬЯ!</b>"
        else:
            user_data["balance"] -= bet
            user_data["losses"] = user_data.get("losses", 0) + 1
            result = f"💔 <b>ПРОИГРЫШ! -{bet:,} монет</b>"
        
        buttons = [[{"text": "🔙 К ИГРАМ", "callback_data": "games"}]]
        send_message(chat_id, f"🃏 Твои: {hand} = {player_total}\n🤖 Дилер: {bot_hand} = {bot_total}\n\n{result}\n💰 Баланс: {user_data['balance']:,}", buttons)

def handle_game_lottery(chat_id, user_data):
    ticket_price = 100
    
    if user_data["balance"] < ticket_price:
        send_message(chat_id, f"❌ Нужно {ticket_price} монет за билет!")
        return
    
    user_data["balance"] -= ticket_price
    numbers = sorted(random.sample(range(1, 50), 6))
    winning = sorted(random.sample(range(1, 50), 6))
    matches = len(set(numbers) & set(winning))
    
    prize = 0
    if matches == 6:
        prize = lottery_jackpot
        lottery_jackpot = 10000
    elif matches == 5:
        prize = lottery_jackpot // 10
    elif matches == 4:
        prize = lottery_jackpot // 100
    elif matches == 3:
        prize = 500
    
    user_data["balance"] += prize
    lottery_jackpot += ticket_price // 2
    
    text = f"🎰 <b>ЛОТЕРЕЯ</b>\n\n"
    text += f"🎫 Твои: {' '.join(map(str, numbers))}\n"
    text += f"🏆 Выигрышные: {' '.join(map(str, winning))}\n"
    text += f"✨ Совпадений: {matches}\n\n"
    
    if prize > 0:
        text += f"🎉 <b>ВЫИГРЫШ: {prize:,} монет!</b>\n"
        user_data["wins"] = user_data.get("wins", 0) + 1
    else:
        text += "💔 Не повезло!\n"
        user_data["losses"] = user_data.get("losses", 0) + 1
    
    text += f"\n💰 Баланс: {user_data['balance']:,}\n🎰 Джекпот: {lottery_jackpot:,}"
    
    buttons = [[{"text": "🎫 КУПИТЬ ЕЩЁ (100)", "callback_data": "game_lottery"}, {"text": "🔙 К ИГРАМ", "callback_data": "games"}]]
    send_message(chat_id, text, buttons)

# ================= БАНДЫ =================
def handle_gangs(chat_id, user_data):
    user_gang = user_data.get("gang")
    
    if user_gang and user_gang in GANGS:
        gang = GANGS[user_gang]
        members_count = len(gang["members"])
        bonus = int((gang["bonus"] - 1) * 100)
        
        text = f"⚫ <b>ТВОЯ ГРУППИРОВКА</b>\n\n"
        text += f"{gang['name']}\n"
        text += f"⚡ Бонус дохода: +{bonus}%\n"
        text += f"👥 Участников: {members_count}\n\n"
        
        if members_count > 0:
            text += "<b>Участники:</b>\n"
            for i, member_id in enumerate(gang["members"][:10], 1):
                member = users_db.get(member_id)
                if member:
                    text += f"{i}. @{member.get('username', 'unknown')} - {member.get('level', 1)} ур.\n"
        
        buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    else:
        text = "⚫ <b>ВЫБОР ГАНГСТЕРСКОЙ ГРУППИРОВКИ</b>\n\n"
        text += "<i>Вступи в банду для бонуса к доходу:</i>\n\n"
        
        buttons = []
        for gang_id, gang in GANGS.items():
            bonus = int((gang["bonus"] - 1) * 100)
            members = len(gang["members"])
            buttons.append([{"text": f"{gang['name']} (+{bonus}%, 👥{members})", "callback_data": f"join_{gang_id}"}])
        
        buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id, text, buttons)

def handle_join_gang(chat_id, user_data, gang_id):
    if gang_id not in GANGS:
        send_message(chat_id, "❌ Ошибка!")
        return
    
    if user_data.get("gang"):
        send_message(chat_id, "❌ Ты уже в банде!")
        return
    
    user_data["gang"] = gang_id
    if user_data["id"] not in GANGS[gang_id]["members"]:
        GANGS[gang_id]["members"].append(user_data["id"])
    
    send_message(chat_id, f"✅ Ты вступил в {GANGS[gang_id]['name']}!")

# ================= КРИПТОВАЛЮТА =================
def handle_crypto(chat_id, user_data):
    text = "₿ <b>КРИПТОВАЛЮТА</b>\n\n<i>Цены меняются каждые 5 минут!</i>\n\n"
    
    for crypto_id, crypto in CRYPTO.items():
        owned = user_data.get("stocks", {}).get(crypto_id, 0)
        text += f"<b>{crypto['name']}</b>\n"
        text += f"💰 Цена: ${crypto['price']:,.2f}\n"
        text += f"📦 У тебя: {owned}\n\n"
    
    buttons = [
        [{"text": "₿ Купить Bitcoin", "callback_data": "crypto_buy_bitcoin"}, {"text": "₿ Продать Bitcoin", "callback_data": "crypto_sell_bitcoin"}],
        [{"text": "Ξ Купить Ethereum", "callback_data": "crypto_buy_ethereum"}, {"text": "Ξ Продать Ethereum", "callback_data": "crypto_sell_ethereum"}],
        [{"text": "🐕 Купить Dogecoin", "callback_data": "crypto_buy_dogecoin"}, {"text": "🐕 Продать Dogecoin", "callback_data": "crypto_sell_dogecoin"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    send_message(chat_id, text, buttons)

def handle_crypto_buy(chat_id, user_data, crypto_id, amount=None):
    if crypto_id not in CRYPTO:
        send_message(chat_id, "❌ Валюта не найдена!")
        return
    
    crypto = CRYPTO[crypto_id]
    price = crypto["price"]
    
    if amount is None:
        buttons = [
            [{"text": "1", "callback_data": f"cryptobuy_{crypto_id}_1"}, {"text": "10", "callback_data": f"cryptobuy_{crypto_id}_10"}],
            [{"text": "100", "callback_data": f"cryptobuy_{crypto_id}_100"}, {"text": "Максимум", "callback_data": f"cryptobuy_{crypto_id}_max"}],
            [{"text": "🔙 НАЗАД", "callback_data": "crypto"}]
        ]
        send_message(chat_id, f"₿ <b>КУПИТЬ {crypto['name']}</b>\n\n💰 Цена: ${price:,.2f}\n\nСколько купить?", buttons)
        return
    
    if amount == "max":
        amount = int(user_data["balance"] / price) if price > 0 else 0
    
    amount = int(amount)
    if amount <= 0:
        send_message(chat_id, "❌ Неверное количество!")
        return
    
    cost = int(amount * price)
    if cost > user_data["balance"]:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= cost
    if "stocks" not in user_data:
        user_data["stocks"] = {}
    user_data["stocks"][crypto_id] = user_data["stocks"].get(crypto_id, 0) + amount
    
    send_message(chat_id, f"✅ Куплено {amount} {crypto['name']} за {cost:,} монет")

def handle_crypto_sell(chat_id, user_data, crypto_id, amount=None):
    if crypto_id not in CRYPTO:
        send_message(chat_id, "❌ Валюта не найдена!")
        return
    
    crypto = CRYPTO[crypto_id]
    price = crypto["price"]
    owned = user_data.get("stocks", {}).get(crypto_id, 0)
    
    if owned <= 0:
        send_message(chat_id, "❌ У тебя нет этой валюты!")
        return
    
    if amount is None:
        buttons = [
            [{"text": "1", "callback_data": f"cryptosell_{crypto_id}_1"}, {"text": "10", "callback_data": f"cryptosell_{crypto_id}_10"}],
            [{"text": "Все", "callback_data": f"cryptosell_{crypto_id}_all"}],
            [{"text": "🔙 НАЗАД", "callback_data": "crypto"}]
        ]
        send_message(chat_id, f"₿ <b>ПРОДАТЬ {crypto['name']}</b>\n\n💰 Цена: ${price:,.2f}\n📦 У тебя: {owned}\n\nСколько продать?", buttons)
        return
    
    if amount == "all":
        amount = owned
    
    amount = int(amount)
    if amount <= 0 or amount > owned:
        send_message(chat_id, "❌ Неверное количество!")
        return
    
    earnings = int(amount * price)
    user_data["balance"] += earnings
    user_data["stocks"][crypto_id] -= amount
    
    send_message(chat_id, f"✅ Продано {amount} {crypto['name']} за {earnings:,} монет")

# ================= ДУЭЛИ =================
def handle_duel_menu(chat_id, user_data):
    text = "⚔️ <b>ДУЭЛИ</b>\n\n"
    text += "Вызывай игроков на дуэли!\n"
    text += "Победа зависит от уровня, рэперов и ранга.\n\n"
    text += "<code>/duel @user ставка</code>"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

def handle_duel(chat_id, user_data, target_username, bet):
    if not target_username:
        send_message(chat_id, "❌ Укажи игрока: /duel @user ставка")
        return
    
    target = find_user_by_username(target_username)
    if not target:
        send_message(chat_id, f"❌ Игрок @{target_username} не найден!")
        return
    
    if target["id"] == user_data["id"]:
        send_message(chat_id, "❌ Нельзя драться с собой!")
        return
    
    try:
        bet = int(bet)
        if bet <= 0:
            send_message(chat_id, "❌ Ставка должна быть больше 0!")
            return
    except:
        send_message(chat_id, "❌ Неверная ставка!")
        return
    
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    if target["balance"] < bet:
        send_message(chat_id, f"❌ У @{target_username} недостаточно монет!")
        return
    
    user_power = get_user_power(user_data)
    target_power = get_user_power(target)
    
    total_power = user_power + target_power
    user_chance = user_power / total_power if total_power > 0 else 0.5
    
    if random.random() < user_chance:
        winnings = int(bet * 0.9)
        user_data["balance"] += winnings
        target["balance"] -= bet
        user_data["wins"] = user_data.get("wins", 0) + 1
        target["losses"] = target.get("losses", 0) + 1
        result = f"⚔️ <b>ПОБЕДА!</b>\n\n🏆 Ты победил @{target_username}!\n💰 +{winnings:,} монет (комиссия 10%)"
    else:
        user_data["balance"] -= bet
        target["balance"] += int(bet * 0.9)
        user_data["losses"] = user_data.get("losses", 0) + 1
        target["wins"] = target.get("wins", 0) + 1
        result = f"⚔️ <b>ПРОИГРЫШ!</b>\n\n💔 Ты проиграл @{target_username}!\n💰 -{bet:,} монет"
    
    result += f"\n💰 Баланс: {user_data['balance']:,}"
    send_message(chat_id, result)
    
    try:
        send_message(target["id"], 
            f"⚔️ <b>ДУЭЛЬ С @{user_data.get('username', 'unknown')}</b>\n\n"
            f"💰 Ставка: {bet:,} монет\n"
            f"{'🎉 ТЫ ПОБЕДИЛ!' if 'ПОБЕДА' not in result else '💔 ТЫ ПРОИГРАЛ!'}\n"
            f"💰 Баланс: {target['balance']:,}"
        )
    except:
        pass

# ================= НЕЛЕГАЛЬНЫЙ БИЗНЕС =================
def handle_illegal_jobs(chat_id, user_data):
    text = "🏴‍☠️ <b>НЕЛЕГАЛЬНЫЙ БИЗНЕС</b>\n\n⚠️ <i>Высокий риск, высокая награда!</i>\n\n"
    
    for job_id, job in ILLEGAL_JOBS.items():
        risk_percent = int(job["risk"] * 100)
        text += f"<b>{job['name']}</b>\n"
        text += f"💰 Доход: {job['min']:,}-{job['max']:,} монет\n"
        text += f"☠️ Риск: {risk_percent}%\n\n"
    
    buttons = [
        [{"text": "🌿 ТРАВА", "callback_data": "job_weed"}, {"text": "💸 ФАЛЬШИВКИ", "callback_data": "job_counterfeit"}],
        [{"text": "💻 ВЗЛОМ", "callback_data": "job_hacking"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    send_message(chat_id, text, buttons)

def handle_illegal_job(chat_id, user_data, job_id):
    if job_id not in ILLEGAL_JOBS:
        send_message(chat_id, "❌ Такой работы нет!")
        return
    
    job = ILLEGAL_JOBS[job_id]
    
    risk = job["risk"]
    rank_id = user_data.get("purchased_rank")
    if rank_id and rank_id in RANKS:
        risk = risk / RANKS[rank_id]["bonus"]
    
    if random.random() < risk:
        fine = random.randint(job["min"], job["max"]) // 2
        user_data["balance"] = max(0, user_data["balance"] - fine)
        
        add_admin_notification(f"🚓 @{user_data.get('username', 'unknown')} пойман: {job['name']}")
        
        send_message(chat_id,
            f"🚓 <b>ТЕБЯ ПОЙМАЛА ПОЛИЦИЯ!</b>\n\n"
            f"⚠️ {job['name']}\n"
            f"💸 Штраф: {fine:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,}"
        )
    else:
        earnings = random.randint(job["min"], job["max"])
        user_data["balance"] += earnings
        user_data["xp"] = user_data.get("xp", 0) + 30
        
        send_message(chat_id,
            f"✅ <b>УСПЕШНО!</b>\n\n"
            f"✨ {job['name']}\n"
            f"💰 Заработано: {earnings:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,}"
        )

# ================= РАНГИ =================
def handle_ranks(chat_id, user_data):
    text = "⭐ <b>РАНГИ ЗА ЗВЁЗДЫ TELEGRAM</b>\n\n"
    text += "<i>Покупай ранги у @prostokiril за настоящие звёзды!</i>\n\n"
    
    current_rank = user_data.get("purchased_rank", None)
    
    for rank_id, rank in RANKS.items():
        is_current = rank_id == current_rank
        prefix = "✅ " if is_current else ""
        text += f"{prefix}{rank['name']} ({rank['stars']} ⭐)\n"
        text += f"   {' | '.join(rank['perks'])}\n\n"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

# ================= ИНВЕНТАРЬ =================
def handle_inventory(chat_id, user_data):
    items = user_data.get("items", [])
    
    if not items:
        text = "🎒 <b>ИНВЕНТАРЬ ПУСТ</b>"
    else:
        text = f"🎒 <b>ИНВЕНТАРЬ</b>\n\n📦 Предметов: {len(items)}\n\n"
        for item_id in items:
            text += f"• {ITEMS.get(item_id, item_id)}\n"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

# ================= ИИ-ПОМОЩНИК =================
def handle_ai_mode(chat_id, user_data, params):
    if not params:
        text = "🤖 <b>РЕЖИМ ИИ-ПОМОЩНИКА</b>\n\n"
        text += "Задай мне вопрос о боте!\n\n"
        text += "<b>Примеры:</b>\n"
        text += "• Как заработать монеты?\n"
        text += "• Что такое ранги?\n"
        text += "• Как купить рэпера?\n"
        text += "• Объясни дуэли\n"
        text += "• Какие есть игры?"
        send_message(chat_id, text)
        return
    
    question = params.lower()
    answer = ""
    
    if any(word in question for word in ["заработ", "деньг", "монет", "баланс"]):
        answer = "💰 <b>Как заработать:</b>\n\n• 🎤 Покупай рэперов в /shop\n• 🎮 Играй в /games\n• ⚫ Нелегальный бизнес /illegal\n• ⚔️ Дуэли /duel\n• 💰 Собирай доход /collect\n• 📈 Крипта /crypto"
    
    elif any(word in question for word in ["ранг", "звезд", "бонус", "статус"]):
        answer = "⭐ <b>Ранги за звёзды:</b>\n\nПокупай у @prostokiril\n\n🥉 Бронзовый (10⭐): +10%\n🥈 Серебряный (25⭐): +25%\n🥇 Золотой (50⭐): +50%\n💎 Платиновый (100⭐): +100%\n👑 Легендарный (200⭐): +200%"
    
    elif any(word in question for word in ["рэпер", "купит", "магазин", "шоп"]):
        answer = "🎤 <b>Магазин:</b>\n\nВ /shop покупай рэперов!\nОни приносят пассивный доход каждый час."
    
    elif any(word in question for word in ["дуэл", "битв", "сраж"]):
        answer = "⚔️ <b>Дуэли:</b>\n\n/duel @user ставка\nПобеда зависит от уровня, рэперов и ранга."
    
    elif any(word in question for word in ["игр", "кости", "слот", "лотере"]):
        answer = "🎮 <b>Игры:</b>\n\n• 🎲 Кости\n• 🎰 Слоты\n• 🪙 Орёл/Решка\n• 🪨 КНБ\n• 🃏 21 очко\n• 🎰 Лотерея\n\nНапиши /games"
    
    elif any(word in question for word in ["банда", "ганг"]):
        answer = "⚫ <b>Банды:</b>\n\n• 🔴 Bloods +20%\n• 🔵 Crips +15%\n• ⚫ Mafia +25%\n• 🗡️ Yakuza +30%\n\nНапиши /gangs"
    
    elif any(word in question for word in ["крипт", "биткоин"]):
        answer = "₿ <b>Крипта:</b>\n\nТоргуй криптовалютой!\nЦены меняются каждые 5 мин.\nНапиши /crypto"
    
    else:
        answer = "🤖 Не понял вопрос. Спроси про:\n• Как заработать?\n• Что такое ранги?\n• Как купить рэпера?\n• Какие есть игры?"
    
    send_message(chat_id, answer)

# ================= АДМИН-ПАНЕЛЬ =================
def handle_admin_panel(chat_id, user_data):
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Только для админов!")
        return
    
    admin_index = user_data.get("admin_index", -1)
    
    buttons = [
        [{"text": "💰 БАЛАНСЫ", "callback_data": "admin_balance"}, {"text": "📊 СТАТИСТИКА", "callback_data": "admin_stats"}],
        [{"text": "🔧 МОДЕРАЦИЯ", "callback_data": "admin_mod"}, {"text": "📬 УВЕДОМЛЕНИЯ", "callback_data": "admin_notifications"}],
    ]
    
    if admin_index in [0, 1]:
        buttons.append([{"text": "👑 АДМИНЫ", "callback_data": "admin_manage"}])
    
    buttons.append([{"text": "💾 СОХРАНИТЬ", "callback_data": "admin_save"}])
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    admin_type = "👑 ВЛАДЕЛЕЦ" if admin_index in [0, 1] else "⚡ АДМИН"
    
    send_message(chat_id,
        f"⚡ <b>АДМИН-ПАНЕЛЬ</b> ({admin_type})\n\n"
        f"👤 @{user_data.get('username', 'unknown')}\n"
        f"💰 {user_data['balance']:,}\n"
        f"📬 Уведомлений: {len(admin_notifications)}\n"
        f"🚫 Банов: {len(banned_users)}",
        buttons
    )

def handle_admin_stats(chat_id):
    total_users = len(users_db)
    total_balance = sum(u.get("balance", 0) for u in users_db.values())
    total_rappers = sum(len(u.get("rappers", [])) for u in users_db.values())
    
    send_message(chat_id,
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"💰 Общий баланс: {total_balance:,}\n"
        f"🎤 Рэперов: {total_rappers}\n"
        f"🎰 Джекпот: {lottery_jackpot:,}\n"
        f"🚫 Банов: {len(banned_users)}"
    )

def handle_admin_balance_help(chat_id):
    send_message(chat_id,
        "💰 <b>УПРАВЛЕНИЕ БАЛАНСАМИ</b>\n\n"
        "<code>/give @user сумма</code>\n"
        "<code>/take @user сумма</code>\n"
        "<code>/setbalance @user сумма</code>"
    )

def handle_admin_mod_help(chat_id):
    send_message(chat_id,
        "🔧 <b>МОДЕРАЦИЯ</b>\n\n"
        "<code>/mute @user минуты</code>\n"
        "<code>/unmute @user</code>\n"
        "<code>/ban @user причина</code>\n"
        "<code>/unban @user</code>\n"
        "<code>/reset @user</code>"
    )

def handle_admin_notifications(chat_id):
    if not admin_notifications:
        send_message(chat_id, "📭 Уведомлений нет")
        return
    
    text = "📬 <b>УВЕДОМЛЕНИЯ</b>\n\n"
    for notif in admin_notifications[-10:]:
        text += f"• {notif['time']}\n  {notif['text']}\n\n"
    
    buttons = [[{"text": "🗑️ ОЧИСТИТЬ", "callback_data": "clear_notifications"}, {"text": "🔙 НАЗАД", "callback_data": "admin_panel"}]]
    send_message(chat_id, text, buttons)

def handle_admin_manage(chat_id, user_data):
    if user_data.get("admin_index", -1) not in [0, 1]:
        send_message(chat_id, "❌ Только для владельцев!")
        return
    
    text = "👑 <b>УПРАВЛЕНИЕ АДМИНАМИ</b>\n\n"
    text += "<b>Владельцы:</b>\n"
    for admin in ADMINS:
        text += f"• @{admin}\n"
    
    if ADDITIONAL_ADMINS:
        text += f"\n<b>Доп. админы:</b>\n"
        for admin in ADDITIONAL_ADMINS:
            text += f"• @{admin}\n"
    
    text += f"\n<code>/setadmin @user</code>\n<code>/removeadmin @user</code>"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "admin_panel"}]]
    send_message(chat_id, text, buttons)

# ================= АДМИН-КОМАНДЫ =================
def handle_admin_command(user_data, chat_id, command, params):
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Нет прав!")
        return
    
    parts = params.strip().split() if params else []
    
    if command == "/getid":
        send_message(chat_id, f"🆔 <b>ID чата:</b> <code>{chat_id}</code>")
    
    elif command == "/mute":
        if len(parts) < 1:
            send_message(chat_id, "❌ /mute @user [минуты]")
            return
        
        username = parts[0].lstrip('@')
        minutes = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if target.get("admin", False):
            send_message(chat_id, "❌ Нельзя мутить админа!")
            return
        
        muted_users[target["id"]] = time.time() + (minutes * 60)
        add_admin_notification(f"🚫 @{user_data['username']} замутил @{username} на {minutes} мин")
        send_message(chat_id, f"✅ @{username} замьючен на {minutes} мин")
    
    elif command == "/unmute":
        if len(parts) < 1:
            send_message(chat_id, "❌ /unmute @user")
            return
        
        username = parts[0].lstrip('@')
        target = find_user_by_username_or_get_from_telegram(username)
        
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if target["id"] in muted_users:
            del muted_users[target["id"]]
            add_admin_notification(f"✅ @{user_data['username']} размутил @{username}")
            send_message(chat_id, f"✅ @{username} размьючен")
        else:
            send_message(chat_id, f"❌ @{username} не в муте")
    
    elif command == "/ban":
        if len(parts) < 1:
            send_message(chat_id, "❌ /ban @user [причина]")
            return
        
        username = parts[0].lstrip('@')
        reason = " ".join(parts[1:]) if len(parts) > 1 else "Нарушение"
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if target.get("admin", False):
            send_message(chat_id, "❌ Нельзя банить админа!")
            return
        
        banned_users[target["id"]] = {"username": username, "admin": user_data["username"], "reason": reason, "time": time.strftime("%d.%m.%Y %H:%M:%S")}
        
        if target["id"] in muted_users:
            del muted_users[target["id"]]
        
        add_admin_notification(f"⛔ @{user_data['username']} забанил @{username}: {reason}")
        send_message(chat_id, f"✅ @{username} забанен")
    
    elif command == "/unban":
        if len(parts) < 1:
            send_message(chat_id, "❌ /unban @user")
            return
        
        username = parts[0].lstrip('@')
        
        target_id = None
        for uid, ban_info in banned_users.items():
            if ban_info.get("username", "").lower() == username.lower():
                target_id = uid
                break
        
        if target_id:
            del banned_users[target_id]
            add_admin_notification(f"✅ @{user_data['username']} разбанил @{username}")
            send_message(chat_id, f"✅ @{username} разбанен")
        else:
            send_message(chat_id, f"❌ @{username} не в бане")
    
    elif command == "/setadmin":
        if user_data.get("admin_index", -1) not in [0, 1]:
            send_message(chat_id, "❌ Только владельцы!")
            return
        
        if len(parts) < 1:
            send_message(chat_id, "❌ /setadmin @user")
            return
        
        username = parts[0].lstrip('@')
        target = find_user_by_username_or_get_from_telegram(username)
        
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if target.get("admin", False):
            send_message(chat_id, f"✅ @{username} уже админ!")
            return
        
        target.update({
            "admin": True, "admin_index": 2, "rank": "⚡ АДМИН",
            "balance": 999999, "rappers": list(RAPPERS.keys()),
            "level": 100, "xp": 999999, "items": list(ITEMS.keys()),
            "wins": 50, "gang": "mafia", "stocks": {"bitcoin": 10, "ethereum": 50, "dogecoin": 1000},
            "daily_streak": 99, "purchased_rank": "legend"
        })
        
        ADDITIONAL_ADMINS.append(username.lower())
        add_admin_notification(f"🔔 Новый админ: @{username}")
        send_message(chat_id, f"✅ @{username} назначен админом!")
        
        try:
            send_message(target["id"], f"🎉 <b>ТЫ СТАЛ АДМИНОМ!</b>\n\nНапиши /admin")
        except:
            pass
    
    elif command == "/removeadmin":
        if user_data.get("admin_index", -1) not in [0, 1]:
            send_message(chat_id, "❌ Только владельцы!")
            return
        
        if len(parts) < 1:
            send_message(chat_id, "❌ /removeadmin @user")
            return
        
        username = parts[0].lstrip('@')
        
        if username.lower() in [a.lower() for a in ADMINS]:
            send_message(chat_id, "❌ Нельзя снять владельца!")
            return
        
        target = find_user_by_username(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target.update({
            "admin": False, "admin_index": -1, "rank": "👤 НОВИЧОК",
            "balance": 5000, "rappers": [], "level": 1, "xp": 0,
            "items": [], "wins": 0, "losses": 0, "gang": None,
            "stocks": {}, "daily_streak": 0, "purchased_rank": None
        })
        
        ADDITIONAL_ADMINS[:] = [a for a in ADDITIONAL_ADMINS if a.lower() != username.lower()]
        add_admin_notification(f"🔔 Снят админ: @{username}")
        send_message(chat_id, f"✅ @{username} снят")
    
    elif command == "/give":
        if len(parts) < 2:
            send_message(chat_id, "❌ /give @user сумма")
            return
        
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount <= 0:
                send_message(chat_id, "❌ Сумма > 0!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target["balance"] += amount
        add_admin_notification(f"💰 @{user_data['username']} выдал {amount} @{username}")
        send_message(chat_id, f"✅ Выдано {amount} монет @{username}")
    
    elif command == "/take":
        if len(parts) < 2:
            send_message(chat_id, "❌ /take @user сумма")
            return
        
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount <= 0:
                send_message(chat_id, "❌ Сумма > 0!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        taken = min(amount, target["balance"])
        target["balance"] -= taken
        add_admin_notification(f"📉 @{user_data['username']} забрал {taken} у @{username}")
        send_message(chat_id, f"✅ Забрано {taken} монет у @{username}")
    
    elif command == "/setbalance":
        if len(parts) < 2:
            send_message(chat_id, "❌ /setbalance @user сумма")
            return
        
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount < 0:
                send_message(chat_id, "❌ Сумма >= 0!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target["balance"] = amount
        add_admin_notification(f"🎯 @{user_data['username']} установил баланс {amount} @{username}")
        send_message(chat_id, f"✅ Баланс {amount} монет @{username}")
    
    elif command == "/setlevel":
        if len(parts) < 2:
            send_message(chat_id, "❌ /setlevel @user уровень")
            return
        
        username = parts[0].lstrip('@')
        try:
            level = int(parts[1])
            if level < 1:
                send_message(chat_id, "❌ Уровень > 0!")
                return
        except:
            send_message(chat_id, "❌ Неверный уровень!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target["level"] = level
        target["xp"] = level * 1000
        add_admin_notification(f"⭐ @{user_data['username']} установил уровень {level} @{username}")
        send_message(chat_id, f"✅ Уровень {level} @{username}")
    
    elif command == "/addrapper":
        if len(parts) < 2:
            send_message(chat_id, "❌ /addrapper @user id")
            return
        
        username = parts[0].lstrip('@')
        rapper_id = parts[1]
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if rapper_id not in RAPPERS:
            send_message(chat_id, f"❌ Рэпер {rapper_id} не найден!")
            return
        
        if rapper_id in target["rappers"]:
            send_message(chat_id, f"❌ У @{username} уже есть!")
            return
        
        target["rappers"].append(rapper_id)
        add_admin_notification(f"🎤 @{user_data['username']} добавил рэпера @{username}")
        send_message(chat_id, f"✅ Рэпер добавлен @{username}")
    
    elif command == "/remrapper":
        if len(parts) < 2:
            send_message(chat_id, "❌ /remrapper @user id")
            return
        
        username = parts[0].lstrip('@')
        rapper_id = parts[1]
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        if rapper_id in target["rappers"]:
            target["rappers"].remove(rapper_id)
            send_message(chat_id, f"✅ Рэпер удалён у @{username}")
        else:
            send_message(chat_id, f"❌ Нет такого рэпера!")
    
    elif command == "/allrappers":
        if len(parts) < 1:
            send_message(chat_id, "❌ /allrappers @user")
            return
        
        username = parts[0].lstrip('@')
        target = find_user_by_username_or_get_from_telegram(username)
        
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target["rappers"] = list(RAPPERS.keys())
        send_message(chat_id, f"✅ Все рэперы выданы @{username}")
    
    elif command == "/clearrappers":
        if len(parts) < 1:
            send_message(chat_id, "❌ /clearrappers @user")
            return
        
        username = parts[0].lstrip('@')
        target = find_user_by_username_or_get_from_telegram(username)
        
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target["rappers"] = []
        send_message(chat_id, f"✅ Рэперы очищены у @{username}")
    
    elif command == "/reset":
        if user_data.get("admin_index", -1) not in [0, 1]:
            send_message(chat_id, "❌ Только владельцы!")
            return
        
        if len(parts) < 1:
            send_message(chat_id, "❌ /reset @user")
            return
        
        username = parts[0].lstrip('@')
        
        if username.lower() in [a.lower() for a in ADMINS] or username.lower() in [a.lower() for a in ADDITIONAL_ADMINS]:
            send_message(chat_id, "❌ Нельзя сбросить админа!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ @{username} не найден!")
            return
        
        target.update({
            "balance": 5000, "rappers": [], "level": 1, "xp": 0,
            "rank": "👤 НОВИЧОК", "purchased_rank": None, "stars_spent": 0,
            "admin": False, "admin_index": -1, "items": [],
            "wins": 0, "losses": 0, "gang": None, "stocks": {},
            "daily_streak": 0, "messages": []
        })
        
        if target["id"] in muted_users:
            del muted_users[target["id"]]
        if target["id"] in banned_users:
            del banned_users[target["id"]]
        
        add_admin_notification(f"🔄 @{user_data['username']} сбросил @{username}")
        send_message(chat_id, f"✅ @{username} сброшен!")

# ================= ОБРАБОТКА CALLBACK =================
def handle_callback(callback_query):
    callback_id = callback_query["id"]
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user = callback_query.get("from", {})
    user_id = user.get("id")
    
    if not chat_id or not user_id:
        answer_callback_query(callback_id)
        return
    
    user_data = get_user_data(user_id, user.get("username", ""), user.get("first_name", "Игрок"))
    last_message_time[user_id] = time.time()
    
    # Проверка бана
    if user_id in banned_users:
        answer_callback_query(callback_id, "Ты забанен!")
        return
    
    try:
        if data == "back":
            answer_callback_query(callback_id)
            handle_start(chat_id, user_data)
        
        elif data == "profile":
            answer_callback_query(callback_id)
            handle_profile(chat_id, user_data)
        
        elif data == "shop":
            answer_callback_query(callback_id)
            handle_shop(chat_id, user_data)
        
        elif data.startswith("buy_"):
            rapper_id = data[4:]
            answer_callback_query(callback_id)
            handle_buy_rapper(chat_id, user_data, rapper_id)
        
        elif data.startswith("view_"):
            rapper_id = data[5:]
            answer_callback_query(callback_id)
            handle_view_rapper(chat_id, user_data, rapper_id)
        
        elif data == "collect":
            answer_callback_query(callback_id)
            handle_collect(chat_id, user_data)
        
        elif data == "games":
            answer_callback_query(callback_id)
            handle_games(chat_id, user_data)
        
        elif data.startswith("dice_"):
            bet = int(data[5:])
            handle_game_dice(chat_id, user_data, bet)
        
        elif data.startswith("slots_"):
            bet = int(data[6:])
            handle_game_slots(chat_id, user_data, bet)
        
        elif data.startswith("coin_"):
            parts = data[5:].split("_")
            bet = int(parts[0])
            choice = parts[1]
            handle_game_coin(chat_id, user_data, bet, choice)
        
        elif data.startswith("rps_"):
            parts = data[4:].split("_")
            bet = int(parts[0])
            choice = parts[1]
            handle_game_rps(chat_id, user_data, bet, choice)
        
        elif data.startswith("21_"):
            parts = data[3:].split("_")
            bet = int(parts[0])
            action = parts[1]
            hand = parts[2] if len(parts) > 2 else None
            if hand:
                handle_game_21(chat_id, user_data, bet, action, hand)
            else:
                handle_game_21(chat_id, user_data, bet)
        
        elif data == "game_dice":
            answer_callback_query(callback_id)
            buttons = [
                [{"text": "100", "callback_data": "dice_100"}, {"text": "500", "callback_data": "dice_500"}],
                [{"text": "1000", "callback_data": "dice_1000"}, {"text": "5000", "callback_data": "dice_5000"}],
                [{"text": "🔙", "callback_data": "games"}]
            ]
            send_message(chat_id, "🎲 <b>КОСТИ</b>\n\nВыбери ставку:\nУгадай 7 или 11 для победы (x2)", buttons)
        
        elif data == "game_slots":
            answer_callback_query(callback_id)
            buttons = [
                [{"text": "100", "callback_data": "slots_100"}, {"text": "500", "callback_data": "slots_500"}],
                [{"text": "1000", "callback_data": "slots_1000"}, {"text": "5000", "callback_data": "slots_5000"}],
                [{"text": "🔙", "callback_data": "games"}]
            ]
            send_message(chat_id, "🎰 <b>СЛОТЫ</b>\n\nВыбери ставку:\nТри одинаковых - джекпот до x20!", buttons)
        
        elif data == "game_coin":
            answer_callback_query(callback_id)
            buttons = [
                [{"text": "100", "callback_data": "coin_100_орёл"}, {"text": "500", "callback_data": "coin_500_орёл"}],
                [{"text": "1000", "callback_data": "coin_1000_орёл"}, {"text": "5000", "callback_data": "coin_5000_орёл"}],
                [{"text": "🔙", "callback_data": "games"}]
            ]
            send_message(chat_id, "🪙 <b>ОРЁЛ/РЕШКА</b>\n\nВыбери ставку:", buttons)
        
        elif data == "game_rps":
            answer_callback_query(callback_id)
            buttons = [
                [{"text": "100", "callback_data": "rps_100_камень"}, {"text": "500", "callback_data": "rps_500_камень"}],
                [{"text": "1000", "callback_data": "rps_1000_камень"}, {"text": "5000", "callback_data": "rps_5000_камень"}],
                [{"text": "🔙", "callback_data": "games"}]
            ]
            send_message(chat_id, "🪨 <b>КАМЕНЬ/НОЖНИЦЫ/БУМАГА</b>\n\nВыбери ставку:", buttons)
        
        elif data == "game_21":
            answer_callback_query(callback_id)
            buttons = [
                [{"text": "100", "callback_data": "21_100"}, {"text": "500", "callback_data": "21_500"}],
                [{"text": "1000", "callback_data": "21_1000"}, {"text": "5000", "callback_data": "21_5000"}],
                [{"text": "🔙", "callback_data": "games"}]
            ]
            send_message(chat_id, "🃏 <b>21 ОЧКО</b>\n\nВыбери ставку:", buttons)
        
        elif data == "game_lottery":
            answer_callback_query(callback_id)
            handle_game_lottery(chat_id, user_data)
        
        elif data == "gangs":
            answer_callback_query(callback_id)
            handle_gangs(chat_id, user_data)
        
        elif data.startswith("join_"):
            gang_id = data[5:]
            answer_callback_query(callback_id)
            handle_join_gang(chat_id, user_data, gang_id)
        
        elif data == "crypto":
            answer_callback_query(callback_id)
            handle_crypto(chat_id, user_data)
        
        elif data.startswith("crypto_buy_"):
            crypto_id = data[11:]
            answer_callback_query(callback_id)
            handle_crypto_buy(chat_id, user_data, crypto_id)
        
        elif data.startswith("crypto_sell_"):
            crypto_id = data[12:]
            answer_callback_query(callback_id)
            handle_crypto_sell(chat_id, user_data, crypto_id)
        
        elif data.startswith("cryptobuy_"):
            parts = data[9:].split("_")
            crypto_id = parts[0]
            amount = parts[1] if len(parts) > 1 else None
            handle_crypto_buy(chat_id, user_data, crypto_id, amount)
        
        elif data.startswith("cryptosell_"):
            parts = data[11:].split("_")
            crypto_id = parts[0]
            amount = parts[1] if len(parts) > 1 else None
            handle_crypto_sell(chat_id, user_data, crypto_id, amount)
        
        elif data == "duel_menu":
            answer_callback_query(callback_id)
            handle_duel_menu(chat_id, user_data)
        
        elif data == "inventory":
            answer_callback_query(callback_id)
            handle_inventory(chat_id, user_data)
        
        elif data == "illegal":
            answer_callback_query(callback_id)
            handle_illegal_jobs(chat_id, user_data)
        
        elif data.startswith("job_"):
            job_id = data[4:]
            answer_callback_query(callback_id)
            handle_illegal_job(chat_id, user_data, job_id)
        
        elif data == "ranks":
            answer_callback_query(callback_id)
            handle_ranks(chat_id, user_data)
        
        elif data == "admin_panel":
            answer_callback_query(callback_id)
            handle_admin_panel(chat_id, user_data)
        
        elif data == "admin_stats":
            answer_callback_query(callback_id)
            handle_admin_stats(chat_id)
        
        elif data == "admin_balance":
            answer_callback_query(callback_id)
            handle_admin_balance_help(chat_id)
        
        elif data == "admin_mod":
            answer_callback_query(callback_id)
            handle_admin_mod_help(chat_id)
        
        elif data == "admin_notifications":
            answer_callback_query(callback_id)
            handle_admin_notifications(chat_id)
        
        elif data == "admin_manage":
            answer_callback_query(callback_id)
            handle_admin_manage(chat_id, user_data)
        
        elif data == "admin_save":
            save_data()
            answer_callback_query(callback_id, "Сохранено!")
            send_message(chat_id, "✅ Данные сохранены!")
        
        elif data == "clear_notifications":
            admin_notifications.clear()
            answer_callback_query(callback_id)
            send_message(chat_id, "🗑️ Уведомления очищены")
        
        else:
            answer_callback_query(callback_id)
    
    except Exception as e:
        logger.error(f"❌ Ошибка callback: {e}")
        answer_callback_query(callback_id, "Ошибка!")

# ================= ОБРАБОТКА СООБЩЕНИЙ =================
def process_message(chat_id, user_id, username, first_name, text):
    user_data = get_user_data(user_id, username, first_name)
    last_message_time[user_id] = time.time()
    
    # Проверка бана
    if user_id in banned_users:
        send_message(chat_id, "🚫 Ты забанен!")
        return
    
    # Проверка мута
    if user_id in muted_users:
        if time.time() < muted_users[user_id]:
            remaining = int(muted_users[user_id] - time.time())
            send_message(chat_id, f"🔇 Ты замьючен! Осталось: {remaining // 60} мин")
            return
        else:
            del muted_users[user_id]
    
    # Проверка флуда
    now = time.time()
    if now - last_message_time.get(user_id, 0) < 1:
        return
    last_message_time[user_id] = now
    
    # Проверка плохих слов
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            chat_warnings[user_id] += 1
            if chat_warnings[user_id] >= 3:
                muted_users[user_id] = time.time() + 300
                chat_warnings[user_id] = 0
                send_message(chat_id, "🚫 Автоматический мут на 5 минут за мат!")
                add_admin_notification(f"🚫 Автомут @{username} за мат")
            else:
                send_message(chat_id, f"⚠️ Предупреждение {chat_warnings[user_id]}/3 за мат!")
            return
    
    # Сохраняем сообщение
    if str(user_id) not in messages_db:
        messages_db[str(user_id)] = []
    messages_db[str(user_id)].append({"text": text, "time": time.strftime("%d.%m.%Y %H:%M:%S")})
    if len(messages_db[str(user_id)]) > 100:
        messages_db[str(user_id)] = messages_db[str(user_id)][-50:]
    
    # Опыт за сообщение
    user_data["xp"] = user_data.get("xp", 0) + 1
    new_level = user_data["xp"] // 1000 + 1
    if new_level > user_data["level"]:
        user_data["level"] = new_level
        send_message(chat_id, f"⭐ <b>НОВЫЙ УРОВЕНЬ: {new_level}!</b>")
    
    # Обработка команд
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        params = parts[1] if len(parts) > 1 else ""
        
        if command == "/start":
            handle_start(chat_id, user_data)
        
        elif command == "/help":
            handle_help(chat_id)
        
        elif command == "/profile":
            handle_profile(chat_id, user_data)
        
        elif command == "/shop":
            handle_shop(chat_id, user_data)
        
        elif command == "/collect":
            handle_collect(chat_id, user_data)
        
        elif command == "/bonus":
            handle_daily_bonus(chat_id, user_data)
        
        elif command == "/games":
            handle_games(chat_id, user_data)
        
        elif command == "/gangs":
            handle_gangs(chat_id, user_data)
        
        elif command == "/crypto":
            handle_crypto(chat_id, user_data)
        
        elif command == "/ranks":
            handle_ranks(chat_id, user_data)
        
        elif command == "/inventory":
            handle_inventory(chat_id, user_data)
        
        elif command == "/illegal":
            handle_illegal_jobs(chat_id, user_data)
        
        elif command == "/duel":
            duel_parts = params.split()
            target = duel_parts[0] if duel_parts else ""
            bet = duel_parts[1] if len(duel_parts) > 1 else "100"
            handle_duel(chat_id, user_data, target.lstrip('@'), bet)
        
        elif command == "/ai":
            handle_ai_mode(chat_id, user_data, params)
        
        elif command == "/ask":
            if params:
                add_admin_notification(f"💬 @{username}: {params}")
                send_message(chat_id, "✅ Сообщение отправлено админам!")
            else:
                send_message(chat_id, "❌ /ask текст")
        
        elif command == "/admin":
            handle_admin_panel(chat_id, user_data)
        
        # Админ-команды
        elif command in ["/getid", "/mute", "/unmute", "/ban", "/unban", "/setadmin", "/removeadmin", "/give", "/take", "/setbalance", "/setlevel", "/addrapper", "/remrapper", "/allrappers", "/clearrappers", "/reset"]:
            handle_admin_command(user_data, chat_id, command, params)
        
        else:
            send_message(chat_id, "❓ Неизвестная команда. Напиши /help")

# ================= ОСНОВНОЙ ЦИКЛ =================
def run_bot():
    load_data()
    last_update_id = None
    logger.info("🤖 Бот запущен и готов к работе")
    
    while True:
        try:
            updates = get_updates(offset=last_update_id)
            for update in updates.get("result", []):
                last_update_id = update["update_id"] + 1
                
                # Обработка callback
                if "callback_query" in update:
                    handle_callback(update["callback_query"])
                    continue
                
                # Обработка сообщений
                message = update.get("message")
                if message:
                    chat_id = message["chat"]["id"]
                    user = message.get("from", {})
                    user_id = user.get("id")
                    username = user.get("username", "")
                    first_name = user.get("first_name", "Игрок")
                    text = message.get("text", "")
                    
                    if text:
                        logger.info(f"💬 {username}: {text[:50]}...")
                        process_message(chat_id, user_id, username, first_name, text)
        except Exception as e:
            logger.error(f"❌ Ошибка в основном цикле: {e}")
            time.sleep(5)

# ================= ЗАПУСК =================
if __name__ == "__main__":
    run_bot()