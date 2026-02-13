import os
import requests
import time
import random
import datetime
import re
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import defaultdict

# ========== HTTP СЕРВЕР ДЛЯ RENDER ==========
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    try:
        server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
        print("✅ HTTP сервер запущен на порту 10000 для Render")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Ошибка HTTP сервера: {e}")

threading.Thread(target=run_http_server, daemon=True).start()

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN", "8493334113:AAG0xhH5SEZ72APG4WrUjRrBAj1ilUWyZPo")
CHANNEL_USERNAME = "Prostokirilllll"
CHANNEL_ID = -1005604869107
DATA_FILE = "bot_data.json"

# ========== АДМИНЫ ==========
ADMINS = ["prostokiril", "ll1_what"]
MAIN_ADMIN = "prostokiril"
ADDITIONAL_ADMINS = []

# Список плохих слов для авто-мута
BAD_WORDS = ["хуй", "пизда", "ебал", "бля", "сука", "гондон", "мудак", "пидор", "чмо", "долбоёб", "еблан"]

print("=" * 60)
print("🎵 ULTIMATE RAP BOSS + CHAT MODERATOR")
print("=" * 60)
print(f"👑 Главный админ: @{MAIN_ADMIN}")
print(f"👑 Второй админ: @{ADMINS[1]}")
print(f"📢 Канал: @{CHANNEL_USERNAME}")
print(f"🆔 ID канала: {CHANNEL_ID}")
print("=" * 60)

# ========== БАЗЫ ДАННЫХ ==========
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

# ========== РАНГИ ЗА ЗВЕЗДЫ TELEGRAM ==========
RANKS = {
    "bronze": {
        "name": "🥉 Бронзовый",
        "stars": 10,
        "bonus": 1.1,
        "color": "🟤",
        "perks": ["+10% к доходу", "Бронзовый скин в профиле"]
    },
    "silver": {
        "name": "🥈 Серебряный",
        "stars": 25,
        "bonus": 1.25,
        "color": "⚪",
        "perks": ["+25% к доходу", "Серебряный скин", "x1.2 к удаче в играх"]
    },
    "gold": {
        "name": "🥇 Золотой",
        "stars": 50,
        "bonus": 1.5,
        "color": "🟡",
        "perks": ["+50% к доходу", "Золотой скин", "x1.5 к удаче", "VIP доступ к играм"]
    },
    "platinum": {
        "name": "💎 Платиновый",
        "stars": 100,
        "bonus": 2.0,
        "color": "🔵",
        "perks": ["+100% к доходу", "Платиновый скин", "x2 к удаче", "VIP статус", "Эксклюзивные предметы"]
    },
    "legend": {
        "name": "👑 Легендарный",
        "stars": 200,
        "bonus": 3.0,
        "color": "🔴",
        "perks": ["+200% к доходу", "Легендарный скин", "x3 к удаче", "Всё включено", "Имя в зале славы"]
    }
}

# ========== РЭПЕРЫ ==========
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

# ========== ГАНГСТЕРСКИЕ ГРУППИРОВКИ ==========
GANGS = {
    "bloods": {"name": "🔴 Bloods", "bonus": 1.2, "members": []},
    "crips": {"name": "🔵 Crips", "bonus": 1.15, "members": []},
    "mafia": {"name": "⚫ Mafia", "bonus": 1.25, "members": []},
    "yakuza": {"name": "🗡️ Yakuza", "bonus": 1.3, "members": []},
}

# ========== НЕЛЕГАЛЬНЫЙ БИЗНЕС ==========
ILLEGAL_JOBS = {
    "weed": {"name": "🌿 Продажа травы", "min": 1000, "max": 5000, "risk": 0.3},
    "counterfeit": {"name": "💸 Фальшивые деньги", "min": 5000, "max": 20000, "risk": 0.5},
    "hacking": {"name": "💻 Взлом банков", "min": 10000, "max": 50000, "risk": 0.7},
}

# ========== КРИПТОВАЛЮТА ==========
CRYPTO = {
    "bitcoin": {"name": "₿ Bitcoin", "price": 45000, "change": 0.1},
    "ethereum": {"name": "Ξ Ethereum", "price": 3000, "change": 0.15},
    "dogecoin": {"name": "🐕 Dogecoin", "price": 0.15, "change": 0.2},
}

# ========== ПРЕДМЕТЫ ==========
ITEMS = {
    "mic": "🎤 Золотой микрофон",
    "chain": "⛓️ Платиновая цепь",
    "car": "🚗 Роллс-Ройс",
    "house": "🏰 Особняк",
    "jet": "✈️ Частный самолет"
}

# ========== ЗАГРУЗКА И СОХРАНЕНИЕ ==========
def load_data():
    """Загружает данные из файла"""
    global users_db, messages_db, daily_bonus_db, chat_warnings, last_message_time
    global muted_users, banned_users, lottery_jackpot, gangs_db, rap_battles
    global user_stocks, admin_notifications, private_messages, duel_requests
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            users_db = {int(k): v for k, v in data.get('users_db', {}).items()}
            messages_db = data.get('messages_db', {})
            daily_bonus_db = data.get('daily_bonus_db', {})
            chat_warnings = defaultdict(int, data.get('chat_warnings', {}))
            last_message_time = defaultdict(float, {int(k): v for k, v in data.get('last_message_time', {}).items()})
            muted_users = {int(k): v for k, v in data.get('muted_users', {}).items()}
            banned_users = {int(k): v for k, v in data.get('banned_users', {}).items()}
            lottery_jackpot = data.get('lottery_jackpot', 10000)
            gangs_db = data.get('gangs_db', {})
            rap_battles = data.get('rap_battles', [])
            user_stocks = data.get('user_stocks', {})
            admin_notifications = data.get('admin_notifications', [])
            private_messages = data.get('private_messages', {})
            duel_requests = data.get('duel_requests', {})
            
            global ADDITIONAL_ADMINS
            ADDITIONAL_ADMINS = data.get('additional_admins', [])
            
            print(f"✅ Данные загружены: {len(users_db)} пользователей")
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")

def save_data():
    """Сохраняет данные в файл"""
    try:
        data = {
            'users_db': users_db,
            'messages_db': dict(messages_db),
            'daily_bonus_db': daily_bonus_db,
            'chat_warnings': dict(chat_warnings),
            'last_message_time': dict(last_message_time),
            'muted_users': muted_users,
            'banned_users': banned_users,
            'lottery_jackpot': lottery_jackpot,
            'gangs_db': gangs_db,
            'rap_battles': rap_battles,
            'user_stocks': user_stocks,
            'admin_notifications': admin_notifications,
            'private_messages': private_messages,
            'duel_requests': duel_requests,
            'additional_admins': ADDITIONAL_ADMINS,
            'save_time': time.strftime("%d.%m.%Y %H:%M:%S")
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Данные сохранены")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
def send_message(chat_id, text, buttons=None, parse_mode="HTML"):
    """Отправляет сообщение"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def add_admin_notification(text):
    """Добавляет уведомление для админов"""
    admin_notifications.append({
        "text": text,
        "time": time.strftime("%d.%m.%Y %H:%M:%S")
    })
    if len(admin_notifications) > 50:
        admin_notifications.pop(0)

def send_admin_notifications(chat_id):
    """Отправляет уведомления админам"""
    if not admin_notifications:
        send_message(chat_id, "📭 <b>Уведомлений нет</b>")
        return
    
    text = "📬 <b>УВЕДОМЛЕНИЯ ДЛЯ АДМИНОВ</b>\n\n"
    for i, notif in enumerate(admin_notifications[-10:], 1):
        text += f"{i}. {notif['time']}\n   {notif['text']}\n\n"
    
    buttons = [[{"text": "🗑️ ОЧИСТИТЬ", "callback_data": "clear_notifications"}]]
    send_message(chat_id, text, buttons)

def check_subscription(user_id):
    """Проверяет подписку на канал"""
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember"
    data = {"chat_id": CHANNEL_ID, "user_id": user_id}
    
    try:
        response = requests.post(url, json=data, timeout=10).json()
        if response.get("ok"):
            status = response["result"]["status"]
            return status in ["member", "administrator", "creator"]
    except:
        pass
    return False

def get_user_data(user_id, username="", first_name="Игрок"):
    """Получает/создает данные пользователя"""
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
                "id": user_id,
                "username": username,
                "name": first_name,
                "balance": 999999,
                "rappers": list(RAPPERS.keys()),
                "level": 100,
                "xp": 999999,
                "rank": f"{badge} {rank}",
                "purchased_rank": "legend",
                "stars_spent": 9999,
                "admin": True,
                "admin_index": admin_index,
                "join_date": time.strftime("%d.%m.%Y"),
                "messages": [],
                "items": list(ITEMS.keys()),
                "wins": 50,
                "losses": 0,
                "gang": "mafia",
                "stocks": {"bitcoin": 10, "ethereum": 50, "dogecoin": 1000},
                "daily_streak": 99
            }
        else:
            users_db[user_id] = {
                "id": user_id,
                "username": username,
                "name": first_name,
                "balance": 5000,
                "rappers": [],
                "level": 1,
                "xp": 0,
                "rank": "👤 НОВИЧОК",
                "purchased_rank": None,
                "stars_spent": 0,
                "admin": False,
                "admin_index": -1,
                "join_date": time.strftime("%d.%m.%Y"),
                "messages": [],
                "items": [],
                "wins": 0,
                "losses": 0,
                "gang": None,
                "stocks": {},
                "daily_streak": 0
            }
    
    return users_db[user_id]

def find_user_by_username(username):
    """Ищет пользователя по username"""
    if not username:
        return None
    username_lower = username.lower().lstrip('@')
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    return None

def get_user_from_telegram(username):
    """Получает пользователя из Telegram API"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChat"
        params = {"chat_id": f"@{username}"}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data["result"]
    except:
        pass
    return None

def find_user_by_username_or_get_from_telegram(username):
    """Ищет пользователя, если нет - получает из Telegram"""
    if not username:
        return None
    
    username_lower = username.lower().lstrip('@')
    
    # Сначала ищем в базе
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    
    # Получаем из Telegram
    tg_user = get_user_from_telegram(username_lower)
    if tg_user:
        return get_user_data(tg_user["id"], username_lower, tg_user.get("first_name", ""))
    
    return None

# ========== НАЗНАЧЕНИЕ АДМИНОВ ==========
def handle_set_admin(chat_id, user_data, params):
    """Назначение админа"""
    if user_data.get("admin_index", -1) not in [0, 1]:
        send_message(chat_id, "❌ Только владельцы могут назначать админов!")
        return
    
    parts = params.strip().split()
    if len(parts) < 1:
        send_message(chat_id, "❌ Использование: /setadmin @username")
        return
    
    username = parts[0].lstrip('@')
    target = find_user_by_username_or_get_from_telegram(username)
    
    if target:
        if target.get("admin", False):
            send_message(chat_id, f"✅ @{username} уже админ!")
            return
        
        target["admin"] = True
        target["admin_index"] = 2
        target["rank"] = "⚡ АДМИН"
        target["balance"] = 999999
        target["rappers"] = list(RAPPERS.keys())
        target["level"] = 100
        target["xp"] = 999999
        target["items"] = list(ITEMS.keys())
        target["wins"] = 50
        target["gang"] = "mafia"
        target["stocks"] = {"bitcoin": 10, "ethereum": 50, "dogecoin": 1000}
        target["daily_streak"] = 99
        target["purchased_rank"] = "legend"
        
        ADDITIONAL_ADMINS.append(username.lower())
        
        notification = f"🔔 Назначен новый админ: @{username}"
        add_admin_notification(notification)
        
        try:
            send_message(target["id"], 
                f"🎉 <b>ТЫ СТАЛ АДМИНОМ!</b>\n\n"
                f"⚡ Тебе доступна админ-панель\n"
                f"💰 Баланс: 999,999 монет\n"
                f"🎤 Все рэперы разблокированы\n"
                f"⭐ Уровень: 100\n\n"
                f"Напиши /admin для доступа к панели"
            )
        except:
            pass
        
        send_message(chat_id, f"✅ @{username} назначен админом!")
    else:
        send_message(chat_id, f"❌ Пользователь @{username} не найден!")

def handle_remove_admin(chat_id, user_data, params):
    """Снятие админа"""
    if user_data.get("admin_index", -1) not in [0, 1]:
        send_message(chat_id, "❌ Только владельцы могут снимать админов!")
        return
    
    parts = params.strip().split()
    if len(parts) < 1:
        send_message(chat_id, "❌ Использование: /removeadmin @username")
        return
    
    username = parts[0].lstrip('@')
    
    if username.lower() in [a.lower() for a in ADMINS]:
        send_message(chat_id, "❌ Нельзя снять владельца!")
        return
    
    target = find_user_by_username(username)
    
    if target:
        if not target.get("admin", False):
            send_message(chat_id, f"✅ @{username} не админ!")
            return
        
        target["admin"] = False
        target["admin_index"] = -1
        target["rank"] = "👤 НОВИЧОК"
        target["balance"] = 5000
        target["rappers"] = []
        target["level"] = 1
        target["xp"] = 0
        target["items"] = []
        target["wins"] = 0
        target["losses"] = 0
        target["gang"] = None
        target["stocks"] = {}
        target["daily_streak"] = 0
        target["purchased_rank"] = None
        
        if username.lower() in [a.lower() for a in ADDITIONAL_ADMINS]:
            ADDITIONAL_ADMINS[:] = [a for a in ADDITIONAL_ADMINS if a.lower() != username.lower()]
        
        notification = f"🔔 Снят админ: @{username}"
        add_admin_notification(notification)
        
        send_message(chat_id, f"✅ @{username} снят с должности админа!")
    else:
        send_message(chat_id, f"❌ Пользователь @{username} не найден!")

# ========== МАГАЗИН РЭПЕРОВ ==========
def handle_shop(chat_id, user_data):
    """Магазин рэперов"""
    buttons = []
    for rapper_id, rapper in RAPPERS.items():
        owned = rapper_id in user_data["rappers"]
        text = f"{rapper['name']} - {rapper['price']:,} монет{' ✅' if owned else ''}"
        buttons.append([{"text": text, "callback_data": f"view_{rapper_id}" if owned else f"buy_{rapper_id}"}])
    
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id,
        f"🛒 <b>МАГАЗИН РЭПЕРОВ</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,} монет\n"
        f"🎤 Куплено: {len(user_data['rappers'])}/{len(RAPPERS)}",
        buttons
    )

def handle_buy_rapper(chat_id, user_data, rapper_id):
    """Покупка рэпера"""
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
    
    send_message(chat_id,
        f"🎉 <b>ПОКУПКА УСПЕШНА!</b>\n\n"
        f"{rapper['name']}\n"
        f"💵 Стоимость: {rapper['price']:,} монет\n"
        f"💰 Остаток: {user_data['balance']:,} монет"
    )

# ========== ИНВЕНТАРЬ ==========
def handle_inventory(chat_id, user_data):
    """Инвентарь"""
    items = user_data.get("items", [])
    
    if not items:
        text = "🎒 <b>ИНВЕНТАРЬ ПУСТ</b>"
    else:
        text = f"🎒 <b>ИНВЕНТАРЬ</b>\n\n📦 Предметов: {len(items)}\n\n"
        for item_id in items:
            text += f"• {ITEMS.get(item_id, item_id)}\n"
    
    buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    send_message(chat_id, text, buttons)

# ========== ГАНГСТЕРСКИЕ ГРУППИРОВКИ ==========
def handle_gangs(chat_id, user_data):
    """Гангстерские группировки"""
    user_gang = user_data.get("gang")
    
    if user_gang:
        gang = GANGS[user_gang]
        members_count = len(gang["members"])
        bonus = int((gang["bonus"] - 1) * 100)
        
        text = f"⚫ <b>ТВОЯ ГРУППИРОВКА</b>\n\n"
        text += f"{gang['name']}\n"
        text += f"⚡ Бонус дохода: +{bonus}%\n"
        text += f"👥 Участников: {members_count}\n\n"
        
        if members_count > 0:
            text += "<b>Топ участников:</b>\n"
            for i, member_id in enumerate(gang["members"][:5], 1):
                member = users_db.get(member_id)
                if member:
                    text += f"{i}. @{member['username']} - {member['level']} ур.\n"
        
        buttons = [[{"text": "🔙 НАЗАД", "callback_data": "back"}]]
    else:
        text = "⚫ <b>ВЫБОР ГАНГСТЕРСКОЙ ГРУППИРОВКИ</b>\n\n"
        text += "<i>Вступи в банду для получения бонуса к доходу:</i>\n\n"
        
        buttons = []
        for gang_id, gang in GANGS.items():
            bonus = int((gang["bonus"] - 1) * 100)
            members = len(gang["members"])
            buttons.append([{"text": f"{gang['name']} (+{bonus}%, 👥{members})", "callback_data": f"join_{gang_id}"}])
        
        buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id, text, buttons)

def handle_join_gang(chat_id, user_data, gang_id):
    """Вступление в банду"""
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

# ========== НЕЛЕГАЛЬНЫЙ БИЗНЕС ==========
def handle_illegal_jobs(chat_id, user_data):
    """Нелегальный бизнес"""
    text = "⚫ <b>НЕЛЕГАЛЬНЫЙ БИЗНЕС</b>\n\n⚠️ <i>Высокий риск, высокая награда!</i>\n\n"
    
    for job_id, job in ILLEGAL_JOBS.items():
        risk_percent = int(job["risk"] * 100)
        text += f"<b>{job['name']}</b>\n"
        text += f"💰 Доход: {job['min']:,}-{job['max']:,} монет\n"
        text += f"☠️ Риск: {risk_percent}%\n\n"
    
    buttons = [
        [{"text": "🌿 ТОРГОВАТЬ ТРАВОЙ", "callback_data": "job_weed"}],
        [{"text": "💸 ПЕЧАТАТЬ ДЕНЬГИ", "callback_data": "job_counterfeit"}],
        [{"text": "💻 ВЗЛАМЫВАТЬ БАНКИ", "callback_data": "job_hacking"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_illegal_job(chat_id, user_data, job_id):
    """Выполнение нелегальной работы"""
    if job_id not in ILLEGAL_JOBS:
        send_message(chat_id, "❌ Такой работы нет!")
        return
    
    job = ILLEGAL_JOBS[job_id]
    
    if random.random() < job["risk"]:
        fine = random.randint(job["min"], job["max"]) // 2
        user_data["balance"] = max(0, user_data["balance"] - fine)
        
        notification = f"🚓 @{user_data['username']} пойман за {job['name']}, штраф {fine:,}"
        add_admin_notification(notification)
        
        send_message(chat_id,
            f"🚓 <b>ТЕБЯ ПОЙМАЛА ПОЛИЦИЯ!</b>\n\n"
            f"⚠️ {job['name']} - опасно!\n"
            f"💸 Штраф: {fine:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,} монет"
        )
    else:
        earnings = random.randint(job["min"], job["max"])
        user_data["balance"] += earnings
        
        send_message(chat_id,
            f"✅ <b>УСПЕШНАЯ ОПЕРАЦИЯ!</b>\n\n"
            f"💰 {job['name']}\n"
            f"💵 Заработано: {earnings:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,} монет"
        )

# ========== КРИПТОВАЛЮТНЫЙ ТРЕЙДИНГ ==========
def handle_crypto_trading(chat_id, user_data):
    """Криптовалютный трейдинг"""
    user_stocks = user_data.get("stocks", {})
    
    text = "₿ <b>КРИПТОВАЛЮТНЫЙ ТРЕЙДИНГ</b>\n\n<i>Купи дешево, продай дорого!</i>\n\n"
    
    total_value = 0
    for crypto_id, crypto in CRYPTO.items():
        amount = user_stocks.get(crypto_id, 0)
        value = amount * crypto["price"]
        total_value += value
        
        text += f"{crypto['name']}\n"
        text += f"💰 Цена: ${crypto['price']:,.2f}\n"
        text += f"📦 У тебя: {amount} шт.\n"
        text += f"💵 Стоимость: ${value:,.2f}\n\n"
    
    text += f"💰 <b>Общая стоимость:</b> ${total_value:,.2f}\n"
    
    buttons = [
        [{"text": "💰 КУПИТЬ", "callback_data": "crypto_buy"}],
        [{"text": "💸 ПРОДАТЬ", "callback_data": "crypto_sell"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def update_crypto_prices():
    """Обновление цен криптовалюты"""
    for crypto_id, crypto in CRYPTO.items():
        change = random.uniform(-crypto["change"], crypto["change"])
        crypto["price"] = max(1, crypto["price"] * (1 + change))

# ========== ТОП ИГРОКОВ ==========
def handle_top_command(chat_id, user_data):
    """Топ игроков"""
    if not users_db:
        send_message(chat_id, "📊 <b>ТОП ИГРОКОВ</b>\n\n<i>Ещё нет игроков!</i>")
        return
    
    sorted_users = sorted(users_db.values(), key=lambda x: x.get("balance", 0), reverse=True)[:10]
    
    text = "📊 <b>ТОП ИГРОКОВ ПО БАЛАНСУ</b>\n\n"
    
    for i, user in enumerate(sorted_users, 1):
        username = user.get("username", "без имени")
        if not username:
            username = user.get("name", f"Игрок {user['id']}")
        
        rank_bonus = ""
        if user.get("purchased_rank"):
            rank_bonus = f" {RANKS[user['purchased_rank']]['color']}"
        
        badge = ""
        if user.get("admin", False):
            admin_index = user.get("admin_index", -1)
            badge = "👑" if admin_index in [0, 1] else "⚡"
        
        text += f"{i}. {badge}{rank_bonus} @{username}\n"
        text += f"   💰 {user.get('balance', 0):,} монет | "
        text += f"⭐ {user.get('level', 1)} ур. | "
        text += f"🎤 {len(user.get('rappers', []))}\n"
    
    text += f"\n📈 Всего игроков: {len(users_db)}"
    
    buttons = [
        [{"text": "💰 ПО БАЛАНСУ", "callback_data": "top_balance"}],
        [{"text": "⭐ ПО УРОВНЮ", "callback_data": "top_level"}],
        [{"text": "🏆 ПО ПОБЕДАМ", "callback_data": "top_wins"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_top_balance(chat_id):
    """Топ по балансу"""
    if not users_db:
        send_message(chat_id, "📊 <b>ТОП ПО БАЛАНСУ</b>\n\n<i>Ещё нет игроков!</i>")
        return
    
    sorted_users = sorted(users_db.values(), key=lambda x: x.get("balance", 0), reverse=True)[:15]
    
    text = "💰 <b>ТОП ПО БАЛАНСУ</b>\n\n"
    for i, user in enumerate(sorted_users, 1):
        username = user.get("username", "без имени")
        text += f"{i}. @{username} - {user.get('balance', 0):,} монет\n"
    
    send_message(chat_id, text)

def handle_top_level(chat_id):
    """Топ по уровню"""
    if not users_db:
        send_message(chat_id, "⭐ <b>ТОП ПО УРОВНЮ</b>\n\n<i>Ещё нет игроков!</i>")
        return
    
    sorted_users = sorted(users_db.values(), key=lambda x: x.get("level", 0), reverse=True)[:15]
    
    text = "⭐ <b>ТОП ПО УРОВНЮ</b>\n\n"
    for i, user in enumerate(sorted_users, 1):
        username = user.get("username", "без имени")
        text += f"{i}. @{username} - {user.get('level', 1)} ур.\n"
    
    send_message(chat_id, text)

def handle_top_wins(chat_id):
    """Топ по победам"""
    if not users_db:
        send_message(chat_id, "🏆 <b>ТОП ПО ПОБЕДАМ</b>\n\n<i>Ещё нет игроков!</i>")
        return
    
    sorted_users = sorted(users_db.values(), key=lambda x: x.get("wins", 0), reverse=True)[:15]
    
    text = "🏆 <b>ТОП ПО ПОБЕДАМ</b>\n\n"
    for i, user in enumerate(sorted_users, 1):
        username = user.get("username", "без имени")
        wins = user.get("wins", 0)
        losses = user.get("losses", 0)
        text += f"{i}. @{username} - {wins} побед ({losses} поражений)\n"
    
    send_message(chat_id, text)

# ========== КОМАНДА /ASK ==========
def handle_ask_command(chat_id, user_data):
    """Вопрос админам"""
    buttons = [
        [{"text": "👑 ГЛАВНЫЙ АДМИН", "url": f"https://t.me/{ADMINS[0]}"}],
        [{"text": "👑 ВТОРОЙ АДМИН", "url": f"https://t.me/{ADMINS[1]}"}],
        [{"text": "📢 КАНАЛ", "url": f"https://t.me/{CHANNEL_USERNAME}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id,
        f"❓ <b>ВОПРОС К АДМИНАМ</b>\n\n"
        f"👑 <b>Владельцы бота:</b>\n"
        f"• @{ADMINS[0]} - Главный админ\n"
        f"• @{ADMINS[1]} - Со-владелец\n\n"
        f"📢 <b>Наш канал:</b> @{CHANNEL_USERNAME}",
        buttons
    )

# ========== РАНГИ ЗА ЗВЕЗДЫ ==========
def handle_ranks_menu(chat_id, user_data):
    """Меню рангов"""
    text = "⭐ <b>РАНГИ ЗА ЗВЕЗДЫ TELEGRAM</b>\n\n"
    text += "<i>Покупай ранги за настоящие звезды Telegram!</i>\n"
    text += f"<i>Звезды приходят @{MAIN_ADMIN}</i>\n\n"
    
    current_rank = user_data.get("purchased_rank")
    if current_rank:
        text += f"🎁 <b>Твой текущий ранг:</b> {RANKS[current_rank]['name']}\n"
        text += f"💰 Бонус: +{int((RANKS[current_rank]['bonus']-1)*100)}%\n\n"
    
    text += "<b>Доступные ранги:</b>\n\n"
    
    buttons = []
    for rank_id, rank in RANKS.items():
        if rank_id != current_rank:
            text += f"{rank['color']} <b>{rank['name']}</b>\n"
            text += f"   💰 {rank['stars']} ⭐ | +{int((rank['bonus']-1)*100)}%\n"
            text += f"   • {', '.join(rank['perks'][:2])}\n\n"
            buttons.append([{"text": f"⭐ КУПИТЬ {rank['name']}", "callback_data": f"buy_rank_{rank_id}"}])
    
    if current_rank:
        buttons.append([{"text": "📊 МОЙ РАНГ", "callback_data": "my_rank"}])
    
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id, text, buttons)

def create_stars_invoice(chat_id, user_data, rank_id):
    """Создает счет на оплату звездами"""
    rank = RANKS[rank_id]
    stars_amount = rank["stars"]
    
    text = f"⭐ <b>ПОКУПКА РАНГА {rank['name']}</b>\n\n"
    text += f"💰 <b>Цена:</b> {stars_amount} ⭐ Telegram Stars\n"
    text += f"🎁 <b>Бонус:</b> +{int((rank['bonus']-1)*100)}% к доходу\n\n"
    text += f"<b>Преимущества:</b>\n"
    for perk in rank["perks"]:
        text += f"• {perk}\n"
    
    text += f"\n<i>Для оплаты отправь {stars_amount} ⭐ на @{MAIN_ADMIN}</i>\n"
    text += f"<i>После оплаты нажми 'Я оплатил'</i>"
    
    buttons = [
        [{"text": f"⭐ Отправить {stars_amount} звезд", "url": f"https://t.me/{MAIN_ADMIN}"}],
        [{"text": "✅ Я оплатил", "callback_data": f"confirm_rank_{rank_id}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "ranks"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_confirm_rank(chat_id, user_data, rank_id):
    """Подтверждение покупки ранга"""
    if rank_id not in RANKS:
        send_message(chat_id, "❌ Ранг не найден!")
        return
    
    text = f"⭐ <b>ЗАПРОС НА ПОКУПКУ РАНГА</b>\n\n"
    text += f"👤 Пользователь: @{user_data['username']}\n"
    text += f"🎁 Ранг: {RANKS[rank_id]['name']}\n"
    text += f"💰 Цена: {RANKS[rank_id]['stars']} ⭐\n\n"
    text += f"<i>Проверь получение звезд и подтверди:</i>"
    
    buttons = [
        [{"text": "✅ ПОДТВЕРДИТЬ", "callback_data": f"approve_rank_{rank_id}_{user_data['id']}"}],
        [{"text": "❌ ОТКАЗАТЬ", "callback_data": f"reject_rank_{user_data['id']}"}]
    ]
    
    for admin_username in ADMINS:
        admin = find_user_by_username(admin_username)
        if admin:
            send_message(admin["id"], text, buttons)
    
    send_message(chat_id, "✅ Запрос отправлен админу! Ожидай подтверждения.")

def handle_approve_rank(chat_id, admin_data, rank_id, target_id):
    """Админ подтверждает покупку ранга"""
    target = users_db.get(int(target_id))
    if not target:
        send_message(chat_id, "❌ Пользователь не найден!")
        return
    
    target["purchased_rank"] = rank_id
    target["stars_spent"] = target.get("stars_spent", 0) + RANKS[rank_id]["stars"]
    
    notification = f"⭐ @{admin_data['username']} выдал ранг {RANKS[rank_id]['name']} @{target['username']}"
    add_admin_notification(notification)
    
    try:
        send_message(target["id"],
            f"🎉 <b>ПОЗДРАВЛЯЮ!</b>\n\n"
            f"Тебе выдан ранг {RANKS[rank_id]['name']}!\n"
            f"💰 Бонус к доходу: +{int((RANKS[rank_id]['bonus']-1)*100)}%\n\n"
            f"Спасибо за поддержку! ❤️"
        )
    except:
        pass
    
    send_message(chat_id, f"✅ Ранг {RANKS[rank_id]['name']} выдан @{target['username']}")

def handle_reject_rank(chat_id, admin_data, target_id):
    """Админ отклоняет покупку ранга"""
    target = users_db.get(int(target_id))
    if target:
        try:
            send_message(target["id"], "❌ К сожалению, твой запрос на покупку ранга отклонен. Проверь, отправил ли ты звезды.")
        except:
            pass
    
    send_message(chat_id, f"✅ Запрос отклонен")

def handle_my_rank(chat_id, user_data):
    """Информация о текущем ранге"""
    rank_id = user_data.get("purchased_rank")
    if not rank_id:
        send_message(chat_id, "❌ У тебя пока нет ранга! Купи в /ranks")
        return
    
    rank = RANKS[rank_id]
    text = f"📊 <b>ТВОЙ РАНГ: {rank['name']}</b>\n\n"
    text += f"💰 Бонус к доходу: +{int((rank['bonus']-1)*100)}%\n"
    text += f"⭐ Потрачено звезд: {user_data.get('stars_spent', 0)}\n\n"
    text += f"<b>Преимущества:</b>\n"
    for perk in rank["perks"]:
        text += f"• {perk}\n"
    
    send_message(chat_id, text)

# ========== ЛИЧНЫЕ СООБЩЕНИЯ ==========
def handle_send_message(chat_id, user_data, params):
    """Отправка личного сообщения"""
    if not params:
        send_message(chat_id, "❌ Использование: /to @username текст")
        return
    
    parts = params.strip().split()
    if len(parts) < 2:
        send_message(chat_id, "❌ Использование: /to @username текст")
        return
    
    username = parts[0].lstrip('@')
    message_text = " ".join(parts[1:])
    
    target = find_user_by_username(username)
    if not target:
        tg_user = get_user_from_telegram(username)
        if tg_user:
            target = get_user_data(tg_user["id"], username, tg_user.get("first_name", ""))
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
            return
    
    msg_data = {
        "from_id": user_data["id"],
        "from_username": user_data["username"],
        "to_id": target["id"],
        "to_username": target["username"],
        "text": message_text,
        "time": time.strftime("%d.%m.%Y %H:%M:%S"),
        "read": False
    }
    
    private_messages[target["id"]].append(msg_data)
    
    try:
        send_message(target["id"],
            f"📨 <b>НОВОЕ СООБЩЕНИЕ</b>\n\n"
            f"От: @{user_data['username']}\n"
            f"Время: {msg_data['time']}\n\n"
            f"{message_text}\n\n"
            f"<i>Напиши /inbox для просмотра</i>"
        )
    except:
        pass
    
    send_message(chat_id, f"✅ Сообщение отправлено @{target['username']}")

def handle_inbox(chat_id, user_data):
    """Просмотр личных сообщений"""
    messages = private_messages.get(user_data["id"], [])
    
    if not messages:
        send_message(chat_id, "📭 <b>Сообщений нет</b>")
        return
    
    text = "📬 <b>ЛИЧНЫЕ СООБЩЕНИЯ</b>\n\n"
    
    unread = 0
    for i, msg in enumerate(messages[-10:], 1):
        if not msg.get("read", True):
            unread += 1
        msg["read"] = True
        text += f"{i}. 📨 От @{msg['from_username']} ({msg['time']}):\n"
        text += f"   {msg['text'][:50]}...\n\n"
    
    text += f"📊 Всего: {len(messages)}, Новых: {unread}"
    
    buttons = [[{"text": "🗑️ ОЧИСТИТЬ", "callback_data": "clear_inbox"}]]
    send_message(chat_id, text, buttons)

def handle_clear_inbox(chat_id, user_data):
    """Очистка сообщений"""
    private_messages[user_data["id"]] = []
    send_message(chat_id, "🗑️ Все сообщения удалены")

# ========== ДУЭЛИ С ЗАПРОСАМИ ==========
def handle_duel_command(chat_id, user_data, params):
    """Отправка запроса на дуэль"""
    if not params:
        send_message(chat_id, "❌ Использование: /duel @username [ставка]")
        return
    
    parts = params.strip().split()
    username = parts[0].lstrip('@')
    bet = 100
    
    if len(parts) > 1:
        try:
            bet = int(parts[1])
            if bet < 100:
                send_message(chat_id, "❌ Минимальная ставка 100 монет!")
                return
            if bet > user_data["balance"]:
                send_message(chat_id, "❌ У тебя недостаточно монет!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма ставки!")
            return
    
    target = find_user_by_username(username)
    if not target:
        tg_user = get_user_from_telegram(username)
        if tg_user:
            target = get_user_data(tg_user["id"], username, tg_user.get("first_name", ""))
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
            return
    
    if target["id"] == user_data["id"]:
        send_message(chat_id, "❌ Нельзя вызвать на дуэль самого себя!")
        return
    
    if target.get("admin", False):
        send_message(chat_id, "❌ Нельзя вызвать админа на дуэль!")
        return
    
    request_id = f"{user_data['id']}_{int(time.time())}"
    duel_requests[target["id"]].append({
        "id": request_id,
        "from_id": user_data["id"],
        "from_username": user_data["username"],
        "bet": bet,
        "time": time.time()
    })
    
    text = f"⚔️ <b>ВЫЗОВ НА ДУЭЛЬ!</b>\n\n"
    text += f"👤 @{user_data['username']} вызывает тебя на дуэль!\n"
    text += f"💰 Ставка: {bet} монет\n\n"
    text += f"<i>Примешь вызов?</i>"
    
    buttons = [
        [{"text": "✅ ПРИНЯТЬ", "callback_data": f"accept_duel_{request_id}"}],
        [{"text": "❌ ОТКЛОНИТЬ", "callback_data": f"reject_duel_{request_id}"}]
    ]
    
    send_message(target["id"], text, buttons)
    send_message(chat_id, f"✅ Запрос на дуэль отправлен @{target['username']}")

def handle_accept_duel(chat_id, user_data, request_id):
    """Принятие дуэли"""
    request = None
    for req in duel_requests.get(user_data["id"], []):
        if req["id"] == request_id:
            request = req
            break
    
    if not request:
        send_message(chat_id, "❌ Запрос устарел или не найден!")
        return
    
    from_user = users_db.get(request["from_id"])
    if not from_user:
        send_message(chat_id, "❌ Отправитель не найден!")
        return
    
    if from_user["balance"] < request["bet"]:
        send_message(chat_id, f"❌ @{from_user['username']} недостаточно монет!")
        duel_requests[user_data["id"]].remove(request)
        return
    
    if user_data["balance"] < request["bet"]:
        send_message(chat_id, "❌ У тебя недостаточно монет!")
        duel_requests[user_data["id"]].remove(request)
        return
    
    from_user["balance"] -= request["bet"]
    user_data["balance"] -= request["bet"]
    
    from_power = from_user["level"] * 10 + len(from_user.get("rappers", [])) * 5
    to_power = user_data["level"] * 10 + len(user_data.get("rappers", [])) * 5
    
    from_rank = from_user.get("purchased_rank")
    to_rank = user_data.get("purchased_rank")
    if from_rank:
        from_power = int(from_power * RANKS[from_rank]["bonus"])
    if to_rank:
        to_power = int(to_power * RANKS[to_rank]["bonus"])
    
    from_chance = from_power / (from_power + to_power) * 0.7 + random.random() * 0.3
    
    if from_chance > 0.5:
        winner = from_user
        loser = user_data
    else:
        winner = user_data
        loser = from_user
    
    win_amount = int(request["bet"] * 2 * 0.9)
    winner["balance"] += win_amount
    
    winner["wins"] = winner.get("wins", 0) + 1
    loser["losses"] = loser.get("losses", 0) + 1
    
    result = f"⚔️ <b>РЕЗУЛЬТАТ ДУЭЛИ</b>\n\n"
    result += f"👤 @{from_user['username']} vs @{user_data['username']}\n"
    result += f"💰 Ставка: {request['bet']} монет\n\n"
    result += f"🏆 <b>ПОБЕДИТЕЛЬ: @{winner['username']}!</b>\n"
    result += f"💵 Выигрыш: {win_amount} монет"
    
    send_message(from_user["id"], result)
    send_message(user_data["id"], result)
    
    duel_requests[user_data["id"]].remove(request)

def handle_reject_duel(chat_id, user_data, request_id):
    """Отклонение дуэли"""
    for req in duel_requests.get(user_data["id"], []):
        if req["id"] == request_id:
            from_user = users_db.get(req["from_id"])
            if from_user:
                send_message(from_user["id"], f"❌ @{user_data['username']} отклонил вызов на дуэль")
            duel_requests[user_data["id"]].remove(req)
            break
    
    send_message(chat_id, "✅ Вызов отклонен")

# ========== МИНИ-ИГРЫ ==========
def handle_games_menu(chat_id):
    """Меню игр"""
    buttons = [
        [{"text": "🎲 КОСТИ", "callback_data": "game_dice"}],
        [{"text": "🎰 СЛОТЫ", "callback_data": "game_slots"}],
        [{"text": "🪙 ОРЁЛ/РЕШКА", "callback_data": "game_coin"}],
        [{"text": "🪨 КАМЕНЬ/НОЖНИЦЫ", "callback_data": "game_rps"}],
        [{"text": "🃏 БЛЭКДЖЕК", "callback_data": "game_blackjack"}],
        [{"text": "🎰 ЛОТЕРЕЯ", "callback_data": "lottery"}],
        [{"text": "💰 ЗАРАБОТОК", "callback_data": "earnings"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, "🎮 <b>МИНИ-ИГРЫ</b>\n\nВыбери игру:", buttons)

def handle_extra_earnings(chat_id, user_data):
    """Дополнительный заработок"""
    text = "💰 <b>ДОПОЛНИТЕЛЬНЫЙ ЗАРАБОТОК</b>\n\n"
    
    buttons = [
        [{"text": "⚫ НЕЛЕГАЛЬНЫЙ БИЗНЕС", "callback_data": "illegal"}],
        [{"text": "🎤 РЭП-БАТТЛЫ", "callback_data": "rap_battle"}],
        [{"text": "₿ КРИПТОВАЛЮТА", "callback_data": "crypto"}],
        [{"text": "⚫ ГАНГСТЕРЫ", "callback_data": "gangs"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_game_dice(chat_id, user_data):
    """Игра в кости"""
    if user_data["balance"] < 50:
        send_message(chat_id, "❌ Минимальная ставка - 50 монет!")
        return
    
    buttons = [
        [{"text": "🎲 50", "callback_data": "dice_bet_50"}],
        [{"text": "🎲 100", "callback_data": "dice_bet_100"}],
        [{"text": "🎲 500", "callback_data": "dice_bet_500"}],
        [{"text": "🎲 1000", "callback_data": "dice_bet_1000"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎲 <b>КОСТИ</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,}\n\n"
        f"7 или 11 = x2 | 2,3,12 = проигрыш",
        buttons
    )

def handle_dice_game(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet
    
    d1, d2 = random.randint(1,6), random.randint(1,6)
    total = d1 + d2
    
    text = f"🎲 {d1} + {d2} = {total}\n\n"
    
    if total in [7,11]:
        win = bet * 2
        user_data["balance"] += win
        text += f"🎉 ВЫИГРЫШ! +{win} монет"
    elif total in [2,3,12]:
        text += f"💀 ПРОИГРЫШ! -{bet} монет"
    else:
        user_data["balance"] += bet
        text += f"🤝 НИЧЬЯ! Ставка возвращена"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🎲 ЕЩЁ", "callback_data": f"dice_bet_{bet}"}]]
    send_message(chat_id, text, buttons)

def handle_game_slots(chat_id, user_data):
    """Слоты"""
    if user_data["balance"] < 10:
        send_message(chat_id, "❌ Минимальная ставка - 10 монет!")
        return
    
    buttons = [
        [{"text": "🎰 10", "callback_data": "slots_bet_10"}],
        [{"text": "🎰 50", "callback_data": "slots_bet_50"}],
        [{"text": "🎰 100", "callback_data": "slots_bet_100"}],
        [{"text": "🎰 500", "callback_data": "slots_bet_500"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎰 <b>СЛОТЫ</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,}",
        buttons
    )

def handle_slots_game(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet
    
    symbols = ["🍒", "🍒", "⭐", "💰", "👑", "💎"]
    s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
    
    text = f"┌─────┬─────┬─────┐\n"
    text += f"│  {s1}  │  {s2}  │  {s3}  │\n"
    text += f"└─────┴─────┴─────┘\n\n"
    
    mult = 0
    if s1 == s2 == s3:
        mult = {"🍒":2, "⭐":3, "💰":5, "👑":10, "💎":20}[s1]
    elif s1 == s2 or s2 == s3 or s1 == s3:
        mult = 1.5
    
    if mult > 0:
        win = int(bet * mult)
        user_data["balance"] += win
        text += f"🎉 ВЫИГРЫШ! x{mult} = +{win}"
    else:
        text += f"💀 ПРОИГРЫШ! -{bet}"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🎰 ЕЩЁ", "callback_data": f"slots_bet_{bet}"}]]
    send_message(chat_id, text, buttons)

def handle_game_coin(chat_id, user_data):
    """Орёл/Решка"""
    if user_data["balance"] < 10:
        send_message(chat_id, "❌ Минимальная ставка - 10 монет!")
        return
    
    buttons = [
        [{"text": "🪙 10", "callback_data": "coin_bet_10"}],
        [{"text": "🪙 50", "callback_data": "coin_bet_50"}],
        [{"text": "🪙 100", "callback_data": "coin_bet_100"}],
        [{"text": "🪙 500", "callback_data": "coin_bet_500"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🪙 <b>ОРЁЛ/РЕШКА</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,}",
        buttons
    )

def handle_coin_game(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    buttons = [
        [{"text": "🦅 ОРЁЛ", "callback_data": f"coin_flip_heads_{bet}"}],
        [{"text": "🏁 РЕШКА", "callback_data": f"coin_flip_tails_{bet}"}]
    ]
    
    send_message(chat_id,
        f"🪙 Ставка: {bet}\nВыбери сторону:",
        buttons
    )

def handle_coin_flip(chat_id, user_data, side, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet
    
    coin = random.choice(["heads", "tails"])
    win = (side == "heads" and coin == "heads") or (side == "tails" and coin == "tails")
    
    text = f"🪙 Выпало: {'🦅 Орёл' if coin == 'heads' else '🏁 Решка'}\n\n"
    
    if win:
        win_amount = bet * 2
        user_data["balance"] += win_amount
        text += f"🎉 ВЫИГРЫШ! +{win_amount}"
    else:
        text += f"💀 ПРОИГРЫШ! -{bet}"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🪙 ЕЩЁ", "callback_data": f"coin_bet_{bet}"}]]
    send_message(chat_id, text, buttons)

def handle_game_rps(chat_id, user_data):
    """Камень, ножницы, бумага"""
    if user_data["balance"] < 50:
        send_message(chat_id, "❌ Минимальная ставка - 50 монет!")
        return
    
    buttons = [
        [{"text": "🪨 КАМЕНЬ", "callback_data": "rps_rock"}],
        [{"text": "✂️ НОЖНИЦЫ", "callback_data": "rps_scissors"}],
        [{"text": "📄 БУМАГА", "callback_data": "rps_paper"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🪨 <b>КАМЕНЬ, НОЖНИЦЫ, БУМАГА</b>\n\n"
        f"💰 Ставка: 50 монет\n"
        f"💰 Баланс: {user_data['balance']:,}",
        buttons
    )

def handle_rps_game(chat_id, user_data, choice):
    bet = 50
    
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet
    
    choices = ["rock", "scissors", "paper"]
    emojis = {"rock": "🪨", "scissors": "✂️", "paper": "📄"}
    names = {"rock": "Камень", "scissors": "Ножницы", "paper": "Бумага"}
    
    bot = random.choice(choices)
    
    text = f"👤 Ты: {emojis[choice]} {names[choice]}\n"
    text += f"🤖 Бот: {emojis[bot]} {names[bot]}\n\n"
    
    if choice == bot:
        user_data["balance"] += bet
        text += f"🤝 НИЧЬЯ! Ставка возвращена"
    elif (choice == "rock" and bot == "scissors") or \
         (choice == "scissors" and bot == "paper") or \
         (choice == "paper" and bot == "rock"):
        win = bet * 2
        user_data["balance"] += win
        text += f"🎉 ВЫИГРЫШ! +{win}"
    else:
        text += f"💀 ПРОИГРЫШ! -{bet}"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🪨 ЕЩЁ", "callback_data": "game_rps"}]]
    send_message(chat_id, text, buttons)

def handle_game_blackjack(chat_id, user_data):
    """Блэкджек"""
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Минимальная ставка - 100 монет!")
        return
    
    buttons = [
        [{"text": "🃏 100", "callback_data": "bj_bet_100"}],
        [{"text": "🃏 500", "callback_data": "bj_bet_500"}],
        [{"text": "🃏 1000", "callback_data": "bj_bet_1000"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🃏 <b>БЛЭКДЖЕК (21)</b>\n\n"
        f"💰 Баланс: {user_data['balance']:,}",
        buttons
    )

def handle_blackjack_start(chat_id, user_data, bet):
    if user_data["balance"] < bet:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet
    
    player = random.randint(17, 21)
    dealer = random.randint(16, 21)
    
    text = f"🃏 Твои очки: {player}\n"
    text += f"🃏 Очки дилера: {dealer}\n\n"
    
    if player > 21:
        text += f"💀 ПЕРЕБОР! -{bet}"
    elif dealer > 21 or player > dealer:
        win = bet * 2
        user_data["balance"] += win
        text += f"🎉 ВЫИГРЫШ! +{win}"
    elif player < dealer:
        text += f"💀 ПРОИГРЫШ! -{bet}"
    else:
        user_data["balance"] += bet
        text += f"🤝 НИЧЬЯ! Ставка возвращена"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🃏 ЕЩЁ", "callback_data": f"bj_bet_{bet}"}]]
    send_message(chat_id, text, buttons)

def handle_lottery(chat_id, user_data):
    """Лотерея"""
    global lottery_jackpot
    
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Билет стоит 100 монет!")
        return
    
    buttons = [
        [{"text": "🎫 КУПИТЬ БИЛЕТ", "callback_data": "buy_lottery"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎰 <b>ЛОТЕРЕЯ</b>\n\n"
        f"💰 Джекпот: {lottery_jackpot:,}\n"
        f"🎫 Билет: 100 монет\n"
        f"🎁 Каждый билет +50 к джекпоту",
        buttons
    )

def handle_buy_lottery(chat_id, user_data):
    """Покупка билета"""
    global lottery_jackpot
    
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= 100
    lottery_jackpot += 50
    
    if random.randint(1, 500) == 250:
        win = lottery_jackpot
        user_data["balance"] += win
        lottery_jackpot = 10000
        text = f"🎉 ДЖЕКПОТ! +{win} монет!"
    else:
        text = f"🎫 Билет куплен! Джекпот: {lottery_jackpot}"
    
    text += f"\n\n💰 Баланс: {user_data['balance']:,}"
    
    buttons = [[{"text": "🎫 ЕЩЁ", "callback_data": "buy_lottery"}]]
    send_message(chat_id, text, buttons)

# ========== РЭП-БАТТЛЫ ==========
def handle_rap_battle_menu(chat_id, user_data):
    """Меню рэп-баттлов"""
    text = f"🎤 <b>РЭП-БАТТЛЫ</b>\n\n"
    text += f"💰 Баланс: {user_data['balance']:,} монет\n"
    text += f"🏆 Статистика: {user_data.get('wins', 0)}/{user_data.get('losses', 0)}\n\n"
    
    buttons = [
        [{"text": "⚔️ НАЙТИ ПРОТИВНИКА", "callback_data": "battle_find"}],
        [{"text": "💰 СОЗДАТЬ БАТТЛ", "callback_data": "battle_create"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_create_battle(chat_id, user_data):
    """Создание баттла"""
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Минимальная ставка - 100 монет!")
        return
    
    buttons = [
        [{"text": "💰 100", "callback_data": "bet_100"}],
        [{"text": "💰 500", "callback_data": "bet_500"}],
        [{"text": "💰 1000", "callback_data": "bet_1000"}],
        [{"text": "💰 5000", "callback_data": "bet_5000"}],
        [{"text": "🔙 НАЗАД", "callback_data": "rap_battle"}]
    ]
    
    send_message(chat_id,
        f"💰 <b>СОЗДАНИЕ БАТТЛА</b>\n\n"
        f"Выбери сумму ставки:",
        buttons
    )

def handle_find_opponent(chat_id, user_data, bet_amount=None):
    """Поиск противника"""
    opponents = []
    for opponent_id, opponent_data in users_db.items():
        if opponent_id != user_data["id"] and opponent_data.get("balance", 0) >= (bet_amount or 100):
            opponents.append(opponent_data)
    
    if not opponents:
        send_message(chat_id, "❌ Нет подходящих противников!")
        return
    
    opponent = random.choice(opponents)
    
    text = f"🎤 <b>НАЙДЕН ПРОТИВНИК!</b>\n\n"
    text += f"👤 Противник: @{opponent['username']}\n"
    text += f"⭐ Уровень: {opponent['level']}\n"
    text += f"🎤 Рэперов: {len(opponent.get('rappers', []))}\n"
    if bet_amount:
        text += f"💰 Ставка: {bet_amount} монет\n\n"
    
    buttons = [
        [{"text": "⚔️ ПРИНЯТЬ", "callback_data": f"accept_{opponent['id']}_{bet_amount or 0}"}],
        [{"text": "🔍 ИСКАТЬ ДРУГОГО", "callback_data": f"find_{bet_amount or 0}"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_start_battle(chat_id, player1, player2, bet_amount=0):
    """Начало баттла"""
    if bet_amount > 0:
        if player1["balance"] < bet_amount:
            send_message(chat_id, f"❌ @{player1['username']} недостаточно монет!")
            return
        if player2["balance"] < bet_amount:
            send_message(chat_id, f"❌ @{player2['username']} недостаточно монет!")
            return
        
        player1["balance"] -= bet_amount
        player2["balance"] -= bet_amount
    
    p1_power = player1["level"] * 10 + len(player1.get("rappers", [])) * 5
    p2_power = player2["level"] * 10 + len(player2.get("rappers", [])) * 5
    
    p1_rank = player1.get("purchased_rank")
    p2_rank = player2.get("purchased_rank")
    if p1_rank:
        p1_power = int(p1_power * RANKS[p1_rank]["bonus"])
    if p2_rank:
        p2_power = int(p2_power * RANKS[p2_rank]["bonus"])
    
    p1_chance = p1_power / (p1_power + p2_power) * 0.7 + random.random() * 0.3
    
    if p1_chance > 0.5:
        winner = player1
        loser = player2
    else:
        winner = player2
        loser = player1
    
    if bet_amount > 0:
        win_amount = int(bet_amount * 2 * 0.9)
        winner["balance"] += win_amount
    
    winner["wins"] = winner.get("wins", 0) + 1
    loser["losses"] = loser.get("losses", 0) + 1
    
    bet_text = f"\n💰 Ставка: {bet_amount} монет" if bet_amount > 0 else ""
    win_text = f"\n💵 Выигрыш: {win_amount} монет" if bet_amount > 0 else ""
    
    send_message(chat_id,
        f"🏆 <b>РЕЗУЛЬТАТ БАТТЛА</b>\n\n"
        f"🎤 @{player1['username']} vs @{player2['username']}\n"
        f"{bet_text}"
        f"🥇 <b>ПОБЕДИТЕЛЬ:</b> @{winner['username']}!\n"
        f"{win_text}"
    )

# ========== МОДЕРАЦИЯ ЧАТА ==========
def handle_chat_message(msg):
    """Обработка сообщений в чате для модерации"""
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = msg.get("text", "").lower()
    username = msg["from"].get("username", "")
    
    if user_id in banned_users:
        try:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                        json={"chat_id": chat_id, "message_id": msg["message_id"]}, timeout=5)
        except:
            pass
        return False
    
    for bad_word in BAD_WORDS:
        if bad_word in text:
            chat_warnings[user_id] += 1
            
            if chat_warnings[user_id] >= 3:
                muted_users[user_id] = time.time() + 300
                notification = f"🚫 @{username} получил мут на 5 мин за плохие слова"
                add_admin_notification(notification)
                send_message(chat_id, f"🚫 @{username} получил мут на 5 минут!")
            else:
                send_message(chat_id, f"⚠️ @{username}, предупреждение {chat_warnings[user_id]}/3")
            break
    
    current_time = time.time()
    last_time = last_message_time.get(user_id, 0)
    
    if current_time - last_time < 2:
        spam_count = messages_db.get(user_id, 0) + 1
        messages_db[user_id] = spam_count
        
        if spam_count > 5:
            muted_users[user_id] = current_time + 120
            notification = f"🚫 @{username} получил мут на 2 мин за спам"
            add_admin_notification(notification)
            send_message(chat_id, f"🚫 @{username} получил мут на 2 минуты!")
    else:
        messages_db[user_id] = 1
    
    last_message_time[user_id] = current_time
    
    if user_id in muted_users:
        if current_time < muted_users[user_id]:
            try:
                requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                            json={"chat_id": chat_id, "message_id": msg["message_id"]}, timeout=5)
            except:
                pass
            return False
        else:
            del muted_users[user_id]
            if user_id in chat_warnings:
                chat_warnings[user_id] = max(0, chat_warnings[user_id] - 1)
    
    return True

# ========== АДМИН-КОМАНДЫ (ИСПРАВЛЕННЫЕ) ==========
def handle_admin_command(user_data, chat_id, command, params):
    """Обработка админ-команд"""
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Нет прав!")
        return
    
    parts = params.strip().split()
    
    if command == "/getid":
        send_message(chat_id, f"🆔 <b>ID чата:</b> <code>{chat_id}</code>")
        return
    
    elif command == "/mute":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /mute @username [минуты]")
            return
        
        username = parts[0].lstrip('@')
        minutes = 5
        if len(parts) > 1:
            try:
                minutes = int(parts[1])
                if minutes < 1 or minutes > 1440:
                    send_message(chat_id, "❌ Время от 1 до 1440 минут")
                    return
            except:
                send_message(chat_id, "❌ Неверное время")
                return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
            return
        
        if target.get("admin", False):
            send_message(chat_id, "❌ Нельзя замутить админа!")
            return
        
        muted_users[target["id"]] = time.time() + (minutes * 60)
        notification = f"🚫 @{user_data['username']} замутил @{target['username']} на {minutes} мин"
        add_admin_notification(notification)
        send_message(chat_id, f"✅ @{target['username']} замьючен на {minutes} минут")
    
    elif command == "/unmute":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /unmute @username")
            return
        
        username = parts[0].lstrip('@')
        target = find_user_by_username_or_get_from_telegram(username)
        
        if not target:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
            return
        
        if target["id"] in muted_users:
            del muted_users[target["id"]]
            notification = f"✅ @{user_data['username']} размутил @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ @{target['username']} размьючен")
        else:
            send_message(chat_id, f"✅ @{target['username']} не в муте")
    
    elif command == "/ban":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /ban @username [причина]")
            return
        
        username = parts[0].lstrip('@')
        reason = " ".join(parts[1:]) if len(parts) > 1 else "Нарушение правил"
        
        target = find_user_by_username_or_get_from_telegram(username)
        if not target:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
            return
        
        if target.get("admin", False):
            send_message(chat_id, "❌ Нельзя забанить админа!")
            return
        
        banned_users[target["id"]] = {
            "username": target["username"],
            "admin": user_data["username"],
            "reason": reason,
            "time": time.strftime("%d.%m.%Y %H:%M:%S")
        }
        
        if target["id"] in muted_users:
            del muted_users[target["id"]]
        
        notification = f"⛔ @{user_data['username']} забанил @{target['username']}: {reason}"
        add_admin_notification(notification)
        send_message(chat_id, f"✅ @{target['username']} забанен")
    
    elif command == "/unban":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /unban @username")
            return
        
        username = parts[0].lstrip('@')
        
        target_id = None
        for uid, ban_info in banned_users.items():
            if ban_info.get("username", "").lower() == username.lower():
                target_id = uid
                break
        
        if target_id:
            del banned_users[target_id]
            notification = f"✅ @{user_data['username']} разбанил @{username}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ @{username} разбанен")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден в бане!")
    
    elif command == "/setadmin":
        handle_set_admin(chat_id, user_data, params)
    
    elif command == "/removeadmin":
        handle_remove_admin(chat_id, user_data, params)
    
    elif command == "/give" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount <= 0:
                send_message(chat_id, "❌ Сумма должна быть больше 0!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if target:
            target["balance"] += amount
            notification = f"💰 @{user_data['username']} выдал {amount} монет @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Выдано {amount} монет @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/take" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount <= 0:
                send_message(chat_id, "❌ Сумма должна быть больше 0!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if target:
            if amount > target["balance"]:
                amount = target["balance"]
            target["balance"] -= amount
            notification = f"📉 @{user_data['username']} забрал {amount} монет у @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Забрано {amount} монет у @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/setbalance" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        try:
            amount = int(parts[1])
            if amount < 0:
                send_message(chat_id, "❌ Сумма не может быть отрицательной!")
                return
        except:
            send_message(chat_id, "❌ Неверная сумма!")
            return
        
        target = find_user_by_username_or_get_from_telegram(username)
        if target:
            target["balance"] = amount
            notification = f"🎯 @{user_data['username']} установил баланс {amount} монет @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Баланс установлен {amount} монет @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")

# ========== АДМИН-ПАНЕЛЬ ==========
def handle_admin_panel(chat_id, user_data):
    """Админ панель"""
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Только для админов!")
        return
    
    admin_index = user_data.get("admin_index", -1)
    
    buttons = [
        [{"text": "💰 БАЛАНСЫ", "callback_data": "admin_balance"}, {"text": "📊 УРОВНИ", "callback_data": "admin_levels"}],
        [{"text": "🎤 РЭПЕРЫ", "callback_data": "admin_rappers"}, {"text": "📈 СТАТИСТИКА", "callback_data": "admin_stats"}],
        [{"text": "🔧 МОДЕРАЦИЯ", "callback_data": "admin_mod"}, {"text": "📬 УВЕДОМЛЕНИЯ", "callback_data": "admin_notifications"}],
    ]
    
    if admin_index in [0, 1]:
        buttons.append([{"text": "👑 УПРАВЛЕНИЕ АДМИНАМИ", "callback_data": "admin_manage"}])
    
    buttons.append([{"text": "💾 СОХРАНИТЬ", "callback_data": "admin_save"}])
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    admin_type = "👑 ВЛАДЕЛЕЦ" if admin_index in [0, 1] else "⚡ АДМИН"
    
    send_message(chat_id,
        f"⚡ <b>АДМИН-ПАНЕЛЬ</b> ({admin_type})\n\n"
        f"👤 Админ: @{user_data['username']}\n"
        f"💰 Баланс: {user_data['balance']:,}\n"
        f"📬 Уведомлений: {len(admin_notifications)}\n"
        f"🚫 Забанено: {len(banned_users)}",
        buttons
    )

def handle_admin_balance_panel(chat_id):
    send_message(chat_id,
        "💰 <b>УПРАВЛЕНИЕ БАЛАНСАМИ</b>\n\n"
        "<code>/give @user сумма</code> - выдать\n"
        "<code>/take @user сумма</code> - забрать\n"
        "<code>/setbalance @user сумма</code> - установить"
    )

def handle_admin_levels_panel(chat_id):
    send_message(chat_id,
        "📊 <b>УПРАВЛЕНИЕ УРОВНЯМИ</b>\n\n"
        "<code>/setlevel @user уровень</code>\n"
        "<code>/addexp @user опыт</code>"
    )

def handle_admin_rappers_panel(chat_id):
    send_message(chat_id,
        "🎤 <b>УПРАВЛЕНИЕ РЭПЕРАМИ</b>\n\n"
        "<code>/addrapper @user id</code>\n"
        "<code>/remrapper @user id</code>\n"
        "<code>/allrappers @user</code>\n"
        "<code>/clearrappers @user</code>\n\n"
        "ID: cowboy, smoke, liltrap, cloudy, sadboy, ghost, money, ice, fire, diamond"
    )

def handle_admin_stats_panel(chat_id):
    total_users = len(users_db)
    total_balance = sum(u.get("balance", 0) for u in users_db.values())
    total_rappers = sum(len(u.get("rappers", [])) for u in users_db.values())
    online_users = sum(1 for uid in users_db if time.time() - last_message_time.get(uid, 0) < 3600)
    
    send_message(chat_id,
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🟢 Онлайн: {online_users}\n"
        f"💰 Общий баланс: {total_balance:,}\n"
        f"🎤 Всего рэперов: {total_rappers}\n"
        f"🎰 Джекпот: {lottery_jackpot:,}\n"
        f"🚫 Забанено: {len(banned_users)}"
    )

def handle_admin_mod_panel(chat_id):
    send_message(chat_id,
        "🔧 <b>МОДЕРАЦИЯ</b>\n\n"
        "<code>/mute @user 5</code> - мут на 5 мин\n"
        "<code>/unmute @user</code> - размут\n"
        "<code>/ban @user причина</code> - бан\n"
        "<code>/unban @user</code> - разбан\n"
        "<code>/warn @user</code> - предупреждение"
    )

def handle_admin_manage_panel(chat_id, user_data):
    if user_data.get("admin_index", -1) not in [0, 1]:
        send_message(chat_id, "❌ Только для владельцев!")
        return
    
    text = "👑 <b>УПРАВЛЕНИЕ АДМИНАМИ</b>\n\n"
    text += "<b>Владельцы:</b>\n"
    for i, admin in enumerate(ADMINS, 1):
        text += f"{i}. @{admin}\n"
    
    if ADDITIONAL_ADMINS:
        text += f"\n<b>Доп. админы ({len(ADDITIONAL_ADMINS)}):</b>\n"
        for i, admin in enumerate(ADDITIONAL_ADMINS, 1):
            text += f"{i}. @{admin}\n"
    
    buttons = [
        [{"text": "➕ НАЗНАЧИТЬ", "callback_data": "admin_add"}],
        [{"text": "➖ СНЯТЬ", "callback_data": "admin_remove"}],
        [{"text": "🔙 НАЗАД", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_admin_add_panel(chat_id):
    send_message(chat_id,
        "➕ <b>НАЗНАЧЕНИЕ АДМИНА</b>\n\n"
        "<code>/setadmin @username</code>"
    )

def handle_admin_remove_panel(chat_id):
    send_message(chat_id,
        "➖ <b>СНЯТИЕ АДМИНА</b>\n\n"
        "<code>/removeadmin @username</code>"
    )

# ========== START МЕНЮ ==========
def handle_start(user_data, chat_id):
    """Главное меню"""
    if user_data["id"] in banned_users:
        ban_info = banned_users[user_data["id"]]
        send_message(chat_id,
            f"⛔ <b>ВЫ ЗАБАНЕНЫ</b>\n\n"
            f"Причина: {ban_info.get('reason', 'Не указана')}"
        )
        return
    
    if not user_data.get("admin", False) and not check_subscription(user_data["id"]):
        buttons = [[{"text": "📢 ПОДПИСАТЬСЯ", "url": f"https://t.me/{CHANNEL_USERNAME}"}]]
        send_message(chat_id,
            f"🔒 Подпишись на @{CHANNEL_USERNAME}",
            buttons
        )
        return
    
    rank_bonus = ""
    rank_id = user_data.get("purchased_rank")
    if rank_id:
        rank_bonus = f" ({RANKS[rank_id]['name']} +{int((RANKS[rank_id]['bonus']-1)*100)}%)"
    
    text = f"🎵 <b>RAP BOSS</b>\n\n"
    text += f"👋 Привет, {user_data['name']}!\n"
    text += f"💰 Баланс: {user_data['balance']:,}{rank_bonus}\n"
    text += f"⭐ Уровень: {user_data['level']}\n"
    text += f"🎤 Рэперов: {len(user_data['rappers'])}\n\n"
    text += f"<i>Команды:</i>\n"
    text += f"/shop - магазин\n"
    text += f"/games - игры\n"
    text += f"/duel @user - дуэль\n"
    text += f"/to @user - сообщение\n"
    text += f"/inbox - сообщения\n"
    text += f"/ranks - ранги\n"
    text += f"/top - топ игроков\n"
    text += f"/ask - вопрос админу"
    
    buttons = [
        [{"text": "🛒 МАГАЗИН", "callback_data": "shop"}],
        [{"text": "🎮 ИГРЫ", "callback_data": "games"}],
        [{"text": "⭐ РАНГИ", "callback_data": "ranks"}]
    ]
    
    if user_data.get("admin", False):
        buttons.append([{"text": "⚡ АДМИН-ПАНЕЛЬ", "callback_data": "admin_panel"}])
    
    send_message(chat_id, text, buttons)

# ========== MAIN LOOP ==========
def main():
    print("🚀 Загрузка данных...")
    load_data()
    print("✅ Данные загружены!")
    print("🤖 Бот запущен!")
    
    last_save = time.time()
    last_crypto = time.time()
    offset = 0
    
    while True:
        try:
            if time.time() - last_save > 300:
                save_data()
                last_save = time.time()
            
            if time.time() - last_crypto > 300:
                update_crypto_prices()
                last_crypto = time.time()
            
            now = time.time()
            expired = [uid for uid, end in muted_users.items() if now >= end]
            for uid in expired:
                del muted_users[uid]
            
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            response = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for update in data["result"]:
                        offset = update["update_id"] + 1
                        
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            
                            if chat_id < 0:
                                if not handle_chat_message(msg):
                                    continue
                            
                            if "text" in msg:
                                user_id = msg["from"]["id"]
                                text = msg["text"]
                                username = msg["from"].get("username", "")
                                first_name = msg["from"].get("first_name", "Игрок")
                                
                                user_data = get_user_data(user_id, username, first_name)
                                
                                if text == "/start":
                                    handle_start(user_data, chat_id)
                                elif text == "/shop":
                                    handle_shop(chat_id, user_data)
                                elif text == "/inventory":
                                    handle_inventory(chat_id, user_data)
                                elif text == "/games":
                                    handle_games_menu(chat_id)
                                elif text == "/ranks":
                                    handle_ranks_menu(chat_id, user_data)
                                elif text == "/inbox":
                                    handle_inbox(chat_id, user_data)
                                elif text == "/top":
                                    handle_top_command(chat_id, user_data)
                                elif text == "/ask":
                                    handle_ask_command(chat_id, user_data)
                                elif text.startswith("/to "):
                                    handle_send_message(chat_id, user_data, text[4:])
                                elif text.startswith("/duel "):
                                    handle_duel_command(chat_id, user_data, text[6:])
                                elif text == "/admin":
                                    handle_admin_panel(chat_id, user_data)
                                elif user_data.get("admin", False):
                                    if text.startswith("/mute") or text.startswith("/unmute") or \
                                       text.startswith("/ban") or text.startswith("/unban") or \
                                       text.startswith("/give") or text.startswith("/take") or \
                                       text.startswith("/setbalance") or text.startswith("/setadmin") or \
                                       text.startswith("/removeadmin") or text == "/getid" or \
                                       text.startswith("/addrapper") or text.startswith("/remrapper") or \
                                       text.startswith("/allrappers") or text.startswith("/clearrappers"):
                                        parts = text.split(" ", 1)
                                        command = parts[0]
                                        params = parts[1] if len(parts) > 1 else ""
                                        handle_admin_command(user_data, chat_id, command, params)
                        
                        elif "callback_query" in update:
                            call = update["callback_query"]
                            user_id = call["from"]["id"]
                            chat_id = call["message"]["chat"]["id"]
                            data = call["data"]
                            
                            user_data = get_user_data(user_id, 
                                call["from"].get("username", ""),
                                call["from"].get("first_name", ""))
                            
                            try:
                                requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                            json={"callback_query_id": call["id"]})
                            except:
                                pass
                            
                            if data == "back":
                                handle_start(user_data, chat_id)
                            elif data == "shop":
                                handle_shop(chat_id, user_data)
                            elif data == "inventory":
                                handle_inventory(chat_id, user_data)
                            elif data == "games":
                                handle_games_menu(chat_id)
                            elif data == "earnings":
                                handle_extra_earnings(chat_id, user_data)
                            elif data == "illegal":
                                handle_illegal_jobs(chat_id, user_data)
                            elif data == "rap_battle":
                                handle_rap_battle_menu(chat_id, user_data)
                            elif data == "crypto":
                                handle_crypto_trading(chat_id, user_data)
                            elif data == "gangs":
                                handle_gangs(chat_id, user_data)
                            elif data.startswith("join_"):
                                handle_join_gang(chat_id, user_data, data[5:])
                            elif data == "job_weed":
                                handle_illegal_job(chat_id, user_data, "weed")
                            elif data == "job_counterfeit":
                                handle_illegal_job(chat_id, user_data, "counterfeit")
                            elif data == "job_hacking":
                                handle_illegal_job(chat_id, user_data, "hacking")
                            elif data == "battle_create":
                                handle_create_battle(chat_id, user_data)
                            elif data == "battle_find":
                                handle_find_opponent(chat_id, user_data)
                            elif data.startswith("bet_"):
                                bet = int(data[4:])
                                handle_find_opponent(chat_id, user_data, bet)
                            elif data.startswith("accept_"):
                                parts = data.split("_")
                                if len(parts) >= 3:
                                    opp_id = int(parts[1])
                                    bet = int(parts[2]) if len(parts) > 2 else 0
                                    opp = users_db.get(opp_id)
                                    if opp:
                                        handle_start_battle(chat_id, user_data, opp, bet)
                            elif data.startswith("find_"):
                                bet = int(data[5:]) if data[5:] else 0
                                handle_find_opponent(chat_id, user_data, bet)
                            elif data.startswith("buy_"):
                                handle_buy_rapper(chat_id, user_data, data[4:])
                            elif data == "balance":
                                send_message(chat_id, f"💰 Баланс: {user_data['balance']:,}")
                            elif data == "profile":
                                rank_name = RANKS.get(user_data.get("purchased_rank"), {}).get("name", "Нет")
                                gang_name = GANGS.get(user_data.get('gang', ''), {}).get('name', 'Нет')
                                send_message(chat_id,
                                    f"👤 <b>ПРОФИЛЬ</b>\n\n"
                                    f"📛 Имя: {user_data['name']}\n"
                                    f"🔗 @{user_data['username']}\n"
                                    f"💰 Баланс: {user_data['balance']:,}\n"
                                    f"⭐ Уровень: {user_data['level']}\n"
                                    f"🎤 Рэперов: {len(user_data['rappers'])}\n"
                                    f"⚫ Банда: {gang_name}\n"
                                    f"⭐ Ранг: {rank_name}\n"
                                    f"🏆 Побед: {user_data.get('wins', 0)}\n"
                                    f"📅 С: {user_data['join_date']}"
                                )
                            elif data == "ranks":
                                handle_ranks_menu(chat_id, user_data)
                            elif data == "my_rank":
                                handle_my_rank(chat_id, user_data)
                            elif data.startswith("buy_rank_"):
                                handle_confirm_rank(chat_id, user_data, data[9:])
                            elif data.startswith("confirm_rank_"):
                                handle_confirm_rank(chat_id, user_data, data[13:])
                            elif data.startswith("approve_rank_"):
                                parts = data.split("_")
                                if len(parts) == 4:
                                    _, _, rank_id, target_id = parts
                                    handle_approve_rank(chat_id, user_data, rank_id, target_id)
                            elif data.startswith("reject_rank_"):
                                target_id = data[12:]
                                handle_reject_rank(chat_id, user_data, target_id)
                            elif data == "clear_inbox":
                                handle_clear_inbox(chat_id, user_data)
                            elif data.startswith("accept_duel_"):
                                handle_accept_duel(chat_id, user_data, data[12:])
                            elif data.startswith("reject_duel_"):
                                handle_reject_duel(chat_id, user_data, data[12:])
                            elif data == "top":
                                handle_top_command(chat_id, user_data)
                            elif data == "top_balance":
                                handle_top_balance(chat_id)
                            elif data == "top_level":
                                handle_top_level(chat_id)
                            elif data == "top_wins":
                                handle_top_wins(chat_id)
                            elif data == "game_dice":
                                handle_game_dice(chat_id, user_data)
                            elif data.startswith("dice_bet_"):
                                handle_dice_game(chat_id, user_data, int(data[9:]))
                            elif data == "game_slots":
                                handle_game_slots(chat_id, user_data)
                            elif data.startswith("slots_bet_"):
                                handle_slots_game(chat_id, user_data, int(data[10:]))
                            elif data == "game_coin":
                                handle_game_coin(chat_id, user_data)
                            elif data.startswith("coin_bet_"):
                                handle_coin_game(chat_id, user_data, int(data[9:]))
                            elif data.startswith("coin_flip_"):
                                parts = data.split("_")
                                if len(parts) == 4:
                                    _, _, side, bet = parts
                                    handle_coin_flip(chat_id, user_data, side, int(bet))
                            elif data == "game_rps":
                                handle_game_rps(chat_id, user_data)
                            elif data == "rps_rock":
                                handle_rps_game(chat_id, user_data, "rock")
                            elif data == "rps_scissors":
                                handle_rps_game(chat_id, user_data, "scissors")
                            elif data == "rps_paper":
                                handle_rps_game(chat_id, user_data, "paper")
                            elif data == "game_blackjack":
                                handle_game_blackjack(chat_id, user_data)
                            elif data.startswith("bj_bet_"):
                                handle_blackjack_start(chat_id, user_data, int(data[7:]))
                            elif data == "lottery":
                                handle_lottery(chat_id, user_data)
                            elif data == "buy_lottery":
                                handle_buy_lottery(chat_id, user_data)
                            elif data == "admin_panel":
                                handle_admin_panel(chat_id, user_data)
                            elif data == "admin_balance":
                                handle_admin_balance_panel(chat_id)
                            elif data == "admin_levels":
                                handle_admin_levels_panel(chat_id)
                            elif data == "admin_rappers":
                                handle_admin_rappers_panel(chat_id)
                            elif data == "admin_stats":
                                handle_admin_stats_panel(chat_id)
                            elif data == "admin_mod":
                                handle_admin_mod_panel(chat_id)
                            elif data == "admin_notifications":
                                send_admin_notifications(chat_id)
                            elif data == "admin_manage":
                                handle_admin_manage_panel(chat_id, user_data)
                            elif data == "admin_add":
                                handle_admin_add_panel(chat_id)
                            elif data == "admin_remove":
                                handle_admin_remove_panel(chat_id)
                            elif data == "admin_save":
                                save_data()
                                send_message(chat_id, "💾 Данные сохранены!")
                            elif data == "clear_notifications":
                                admin_notifications.clear()
                                send_message(chat_id, "🗑️ Уведомления очищены!")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()