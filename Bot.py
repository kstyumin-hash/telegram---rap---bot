import os
import requests
import time
import random
import datetime
import re
import json
from collections import defaultdict
# ========== ДОБАВЬТЕ ЭТОТ БЛОК ДЛЯ RENDER ==========
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# Запускаем HTTP сервер в отдельном потоке
threading.Thread(target=run_http_server, daemon=True).start()
# ========== КОНЕЦ БЛОКА ДЛЯ RENDER ==========
# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN", "8493334113:AAG0xhH5SEZ72APG4WrUjRrBAj1ilUWyZPo")
CHANNEL_USERNAME = "Prostokirilllll"
CHANNEL_ID = -1005604869107
DATA_FILE = "bot_data.json"  # Файл для сохранения данных

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
banned_users = {}  # Новое: забаненные пользователи
lottery_jackpot = 10000
gangs_db = defaultdict(dict)
rap_battles = []
user_stocks = defaultdict(dict)
admin_notifications = []  # Уведомления для админов

# ========== ЗАГРУЗКА И СОХРАНЕНИЕ ДАННЫХ ==========
def load_data():
    """Загружает данные из файла"""
    global users_db, messages_db, daily_bonus_db, chat_warnings, last_message_time
    global muted_users, banned_users, lottery_jackpot, gangs_db, rap_battles, user_stocks, admin_notifications
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            users_db = data.get('users_db', {})
            # Преобразуем ключи из строк в int
            users_db = {int(k): v for k, v in users_db.items()}
            
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
            
            # Загружаем ADDITIONAL_ADMINS
            global ADDITIONAL_ADMINS
            ADDITIONAL_ADMINS = data.get('additional_admins', [])
            
            print(f"✅ Данные загружены: {len(users_db)} пользователей, {len(banned_users)} забаненных")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")

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
            'additional_admins': ADDITIONAL_ADMINS,
            'save_time': time.strftime("%d.%m.%Y %H:%M:%S")
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Данные сохранены: {len(users_db)} пользователей")
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")

# ========== УВЕДОМЛЕНИЯ ДЛЯ АДМИНОВ ==========
def add_admin_notification(text):
    """Добавляет уведомление для админов"""
    admin_notifications.append({
        "text": text,
        "time": time.strftime("%d.%m.%Y %H:%M:%S")
    })
    
    # Ограничиваем количество уведомлений
    if len(admin_notifications) > 50:
        admin_notifications.pop(0)

def send_admin_notifications(chat_id):
    """Отправляет уведомления админам"""
    if not admin_notifications:
        send_message(chat_id, "📭 <b>Уведомлений нет</b>")
        return
    
    text = "📬 <b>УВЕДОМЛЕНИЯ ДЛЯ АДМИНОВ</b>\n\n"
    
    for i, notif in enumerate(admin_notifications[-10:], 1):
        text += f"{i}. {notif['time']}\n"
        text += f"   {notif['text']}\n\n"
    
    text += f"\nВсего уведомлений: {len(admin_notifications)}"
    
    buttons = [
        [{"text": "🗑️ ОЧИСТИТЬ", "callback_data": "clear_notifications"}],
        [{"text": "🔙 НАЗАД", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id, text, buttons)

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
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

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
    """Получает данные пользователя"""
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
    
    # Сначала ищем в базе данных
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    
    return None

# ФИКС: Новая функция для поиска пользователей даже если они не в базе
def find_user_by_username_or_get_from_telegram(username):
    """Ищет пользователя по username, если нет в базе - получает из Telegram"""
    if not username:
        return None
    
    username_lower = username.lower().lstrip('@')
    
    # Сначала ищем в базе данных
    for user in users_db.values():
        if user.get("username") and user["username"].lower() == username_lower:
            return user
    
    # Если не нашли в базе, пытаемся получить информацию из Telegram
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChat"
        params = {"chat_id": f"@{username_lower}"}
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                user_info = data["result"]
                user_id = user_info["id"]
                
                # Создаем временную запись пользователя
                temp_user = {
                    "id": user_id,
                    "username": username_lower,
                    "name": user_info.get("first_name", "Пользователь"),
                    "balance": 0,
                    "rappers": [],
                    "level": 1,
                    "xp": 0,
                    "rank": "👤 НОВИЧОК",
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
                
                # Сохраняем в базу (если нужно)
                users_db[user_id] = temp_user
                
                return temp_user
    except Exception as e:
        print(f"⚠️ Ошибка получения пользователя из Telegram: {e}")
    
    return None

# ========== НАЗНАЧЕНИЕ АДМИНОВ ==========
def handle_set_admin(chat_id, user_data, params):
    """Назначение админа"""
    if user_data.get("admin_index", -1) not in [0, 1]:  # Только владельцы
        send_message(chat_id, "❌ Только владельцы могут назначать админов!")
        return
    
    parts = params.strip().split()
    if len(parts) < 1:
        send_message(chat_id, "❌ Использование: /setadmin @username")
        return
    
    username = parts[0].lstrip('@')
    
    # Используем улучшенную функцию поиска
    target = find_user_by_username_or_get_from_telegram(username)
    
    if target:
        if target.get("admin", False):
            send_message(chat_id, f"✅ @{username} уже админ!")
            return
        
        # Делаем админом
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
        
        ADDITIONAL_ADMINS.append(username.lower())
        
        # Отправляем уведомление
        notification = f"🔔 Назначен новый админ: @{username}"
        add_admin_notification(notification)
        
        # Отправляем сообщение новому админу
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
        
        send_message(chat_id, 
            f"✅ @{username} назначен админом!\n"
            f"⚡ Уровень доступа: АДМИН"
        )
    else:
        send_message(chat_id, f"❌ Пользователь @{username} не найден!")

def handle_remove_admin(chat_id, user_data, params):
    """Снятие админа"""
    if user_data.get("admin_index", -1) not in [0, 1]:  # Только владельцы
        send_message(chat_id, "❌ Только владельцы могут снимать админов!")
        return
    
    parts = params.strip().split()
    if len(parts) < 1:
        send_message(chat_id, "❌ Использование: /removeadmin @username")
        return
    
    username = parts[0].lstrip('@')
    
    # Нельзя снять владельцев
    if username.lower() in [a.lower() for a in ADMINS]:
        send_message(chat_id, "❌ Нельзя снять владельца!")
        return
    
    # Используем улучшенную функцию поиска
    target = find_user_by_username_or_get_from_telegram(username)
    
    if target:
        if not target.get("admin", False):
            send_message(chat_id, f"✅ @{username} не админ!")
            return
        
        # Снимаем админку
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
        
        # Удаляем из списка доп админов
        if username.lower() in [a.lower() for a in ADDITIONAL_ADMINS]:
            ADDITIONAL_ADMINS[:] = [a for a in ADDITIONAL_ADMINS if a.lower() != username.lower()]
        
        # Отправляем уведомление
        notification = f"🔔 Снят админ: @{username}"
        add_admin_notification(notification)
        
        send_message(chat_id, 
            f"✅ @{username} снят с должности админа!\n"
            f"⚠️ Аккаунт сброшен до начального состояния"
        )
    else:
        send_message(chat_id, f"❌ Пользователь @{username} не найден!")

# ========== МАГАЗИН РЭПЕРОВ ==========
def handle_shop(chat_id, user_data):
    """Магазин рэперов"""
    buttons = []
    
    for rapper_id, rapper in RAPPERS.items():
        owned = rapper_id in user_data["rappers"]
        text = f"{rapper['name']} - {rapper['price']:,} монет"
        
        if owned:
            text += " ✅"
            buttons.append([{"text": text, "callback_data": f"view_{rapper_id}"}])
        else:
            buttons.append([{"text": text, "callback_data": f"buy_{rapper_id}"}])
    
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    send_message(chat_id,
        f"🛒 <b>МАГАЗИН РЭПЕРОВ</b>\n\n"
        f"💰 <b>Баланс:</b> {user_data['balance']:,} монет\n"
        f"🎤 <b>Куплено:</b> {len(user_data['rappers'])}/{len(RAPPERS)}\n\n"
        f"<i>Выбери рэпера:</i>",
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
    
    # Уведомление админам
    if user_data["admin"]:
        notification = f"💰 Админ @{user_data['username']} купил {rapper['name']}"
        add_admin_notification(notification)
    
    send_message(chat_id,
        f"🎉 <b>ПОКУПКА УСПЕШНА!</b>\n\n"
        f"{rapper['name']}\n"
        f"💵 Стоимость: {rapper['price']:,} монет\n"
        f"💰 Остаток: {user_data['balance']:,} монет\n\n"
        f"<i>Рэпер теперь приносит доход!</i>"
    )

# ========== ИНВЕНТАРЬ ==========
def handle_inventory(chat_id, user_data):
    """Инвентарь"""
    items = user_data.get("items", [])
    
    if not items:
        text = "🎒 <b>ИНВЕНТАРЬ ПУСТ</b>\n\n"
        text += "<i>Получай предметы за достижения или покупай в магазине!</i>"
    else:
        text = f"🎒 <b>ИНВЕНТАРЬ</b>\n\n"
        text += f"📦 <b>Предметов:</b> {len(items)}\n\n"
        
        for item_id in items:
            item_name = ITEMS.get(item_id, item_id)
            text += f"• {item_name}\n"
    
    buttons = [
        [{"text": "🛒 МАГАЗИН", "callback_data": "shop"}],
        [{"text": "🎮 ИГРЫ", "callback_data": "games"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
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
        
        buttons = [
            [{"text": "👥 ВСЕ УЧАСТНИКИ", "callback_data": "gang_members"}],
            [{"text": "⚔️ ВОЙНА С БАНДОЙ", "callback_data": "gang_war"}],
            [{"text": "🔙 НАЗАД", "callback_data": "back"}]
        ]
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

# ========== НЕЛЕГАЛЬНЫЙ БИЗНЕС ==========
def handle_illegal_jobs(chat_id, user_data):
    """Нелегальный бизнес"""
    text = "⚫ <b>НЕЛЕГАЛЬНЫЙ БИЗНЕС</b>\n\n"
    text += "⚠️ <i>Высокий риск, высокая награда!</i>\n\n"
    
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
    
    # Проверяем риск
    if random.random() < job["risk"]:
        # Поймали!
        fine = random.randint(job["min"], job["max"]) // 2
        user_data["balance"] = max(0, user_data["balance"] - fine)
        
        # Уведомление админам
        notification = f"🚓 @{user_data['username']} пойман за {job['name']}, штраф {fine:,}"
        add_admin_notification(notification)
        
        send_message(chat_id,
            f"🚓 <b>ТЕБЯ ПОЙМАЛА ПОЛИЦИЯ!</b>\n\n"
            f"⚠️ {job['name']} - опасно!\n"
            f"💸 Штраф: {fine:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n\n"
            f"<i>Будь осторожнее в следующий раз!</i>"
        )
    else:
        # Успех
        earnings = random.randint(job["min"], job["max"])
        user_data["balance"] += earnings
        
        send_message(chat_id,
            f"✅ <b>УСПЕШНАЯ ОПЕРАЦИЯ!</b>\n\n"
            f"💰 {job['name']}\n"
            f"💵 Заработано: {earnings:,} монет\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n\n"
            f"<i>Продолжай в том же духе!</i>"
        )

# ========== ИГРЫ ==========
def handle_game_dice(chat_id, user_data):
    """Игра в кости"""
    if user_data["balance"] < 50:
        send_message(chat_id, "❌ Минимальная ставка - 50 монет!")
        return
    
    buttons = [
        [{"text": "🎲 СТАВКА 50", "callback_data": "dice_bet_50"}],
        [{"text": "🎲 СТАВКА 100", "callback_data": "dice_bet_100"}],
        [{"text": "🎲 СТАВКА 500", "callback_data": "dice_bet_500"}],
        [{"text": "🎲 СТАВКА 1000", "callback_data": "dice_bet_1000"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎲 <b>ИГРА В КОСТИ</b>\n\n"
        f"💰 Твой баланс: {user_data['balance']:,} монет\n\n"
        f"<i>Правила:</i>\n"
        f"• Бросаешь 2 кубика\n"
        f"• Сумма 7 или 11 = x2\n"
        f"• Сумма 2, 3, 12 = проигрыш\n"
        f"• Остальные числа = возврат ставки\n\n"
        f"<b>Выбери ставку:</b>",
        buttons
    )

def handle_dice_game(chat_id, user_data, bet_amount):
    """Игра в кости - процесс"""
    if user_data["balance"] < bet_amount:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet_amount
    
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2
    
    result = f"🎲 <b>БРОСОК КОСТЕЙ</b>\n\n"
    result += f"🎲 Кубик 1: {dice1}\n"
    result += f"🎲 Кубик 2: {dice2}\n"
    result += f"📊 Сумма: <b>{total}</b>\n\n"
    
    if total in [7, 11]:
        win = bet_amount * 2
        user_data["balance"] += win
        result += f"🎉 <b>ВЫИГРЫШ! +{win:,} монет</b>\n"
    elif total in [2, 3, 12]:
        result += f"💀 <b>ПРОИГРЫШ! -{bet_amount:,} монет</b>\n"
    else:
        user_data["balance"] += bet_amount
        result += f"🤝 <b>НИЧЬЯ! Ставка возвращена</b>\n"
    
    result += f"\n💰 <b>Новый баланс:</b> {user_data['balance']:,} монет"
    
    buttons = [
        [{"text": "🎲 ИГРАТЬ ЕЩЁ", "callback_data": f"dice_bet_{bet_amount}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "game_dice"}]
    ]
    
    send_message(chat_id, result, buttons)

def handle_game_slots(chat_id, user_data):
    """Игровые автоматы"""
    if user_data["balance"] < 10:
        send_message(chat_id, "❌ Минимальная ставка - 10 монет!")
        return
    
    buttons = [
        [{"text": "🎰 СТАВКА 10", "callback_data": "slots_bet_10"}],
        [{"text": "🎰 СТАВКА 50", "callback_data": "slots_bet_50"}],
        [{"text": "🎰 СТАВКА 100", "callback_data": "slots_bet_100"}],
        [{"text": "🎰 СТАВКА 500", "callback_data": "slots_bet_500"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎰 <b>ИГРОВЫЕ АВТОМАТЫ</b>\n\n"
        f"💰 Твой баланс: {user_data['balance']:,} монет\n\n"
        f"<i>Символы:</i>\n"
        f"🍒 Вишня = x2\n"
        f"⭐ Звезда = x3\n"
        f"💰 Сундук = x5\n"
        f"👑 Корона = x10\n"
        f"💎 Алмаз = x20\n\n"
        f"<b>Выбери ставку:</b>",
        buttons
    )

def handle_slots_game(chat_id, user_data, bet_amount):
    """Игровые автоматы - процесс"""
    if user_data["balance"] < bet_amount:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet_amount
    
    symbols = ["🍒", "🍒", "🍒", "⭐", "⭐", "💰", "👑", "💎"]
    slot1 = random.choice(symbols)
    slot2 = random.choice(symbols)
    slot3 = random.choice(symbols)
    
    result = f"🎰 <b>ИГРОВЫЕ АВТОМАТЫ</b>\n\n"
    result += f"┌─────┬─────┬─────┐\n"
    result += f"│  {slot1}  │  {slot2}  │  {slot3}  │\n"
    result += f"└─────┴─────┴─────┘\n\n"
    
    # Определяем выигрыш
    if slot1 == slot2 == slot3:
        if slot1 == "🍒":
            multiplier = 2
        elif slot1 == "⭐":
            multiplier = 3
        elif slot1 == "💰":
            multiplier = 5
        elif slot1 == "👑":
            multiplier = 10
        elif slot1 == "💎":
            multiplier = 20
        else:
            multiplier = 1
    elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
        multiplier = 1.5
    else:
        multiplier = 0
    
    if multiplier > 0:
        win = int(bet_amount * multiplier)
        user_data["balance"] += win
        result += f"🎉 <b>ВЫИГРЫШ! x{multiplier}</b>\n"
        result += f"💰 +{win:,} монет\n"
    else:
        result += f"💀 <b>ПРОИГРЫШ! -{bet_amount:,} монет</b>\n"
    
    result += f"\n💰 <b>Новый баланс:</b> {user_data['balance']:,} монет"
    
    buttons = [
        [{"text": "🎰 ИГРАТЬ ЕЩЁ", "callback_data": f"slots_bet_{bet_amount}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "game_slots"}]
    ]
    
    send_message(chat_id, result, buttons)

def handle_game_coin(chat_id, user_data):
    """Орёл или решка"""
    if user_data["balance"] < 10:
        send_message(chat_id, "❌ Минимальная ставка - 10 монет!")
        return
    
    buttons = [
        [{"text": "🪙 СТАВКА 10", "callback_data": "coin_bet_10"}],
        [{"text": "🪙 СТАВКА 50", "callback_data": "coin_bet_50"}],
        [{"text": "🪙 СТАВКА 100", "callback_data": "coin_bet_100"}],
        [{"text": "🪙 СТАВКА 500", "callback_data": "coin_bet_500"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🪙 <b>ОРЁЛ ИЛИ РЕШКА</b>\n\n"
        f"💰 Твой баланс: {user_data['balance']:,} монет\n\n"
        f"<i>Правила:</i>\n"
        f"• Угадай сторону монеты\n"
        f"• Выигрыш = x2 ставки\n\n"
        f"<b>Выбери ставку:</b>",
        buttons
    )

def handle_coin_game(chat_id, user_data, bet_amount):
    """Орёл или решка - выбор стороны"""
    if user_data["balance"] < bet_amount:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    buttons = [
        [{"text": "🦅 ОРЁл", "callback_data": f"coin_side_heads_{bet_amount}"}],
        [{"text": "🏁 РЕШКА", "callback_data": f"coin_side_tails_{bet_amount}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "game_coin"}]
    ]
    
    send_message(chat_id,
        f"🪙 <b>ОРЁЛ ИЛИ РЕШКА</b>\n\n"
        f"💰 Ставка: {bet_amount:,} монет\n"
        f"💵 Выигрыш: {bet_amount * 2:,} монет\n\n"
        f"<b>Выбери сторону:</b>",
        buttons
    )

def handle_coin_flip(chat_id, user_data, side, bet_amount):
    """Орёл или решка - результат"""
    if user_data["balance"] < bet_amount:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= bet_amount
    
    coin = random.choice(["heads", "tails"])
    coin_emoji = "🦅" if coin == "heads" else "🏁"
    chosen_side = "heads" if "heads" in side else "tails"
    
    result = f"🪙 <b>ОРЁЛ ИЛИ РЕШКА</b>\n\n"
    result += f"💰 Ставка: {bet_amount:,} монет\n"
    result += f"👤 Твой выбор: {'Орёл 🦅' if chosen_side == 'heads' else 'Решка 🏁'}\n"
    result += f"🎲 Результат: {coin_emoji} {'Орёл' if coin == 'heads' else 'Решка'}\n\n"
    
    if chosen_side == coin:
        win = bet_amount * 2
        user_data["balance"] += win
        result += f"🎉 <b>ВЫИГРАЛ! +{win:,} монет</b>\n"
    else:
        result += f"💀 <b>ПРОИГРАЛ! -{bet_amount:,} монет</b>\n"
    
    result += f"\n💰 <b>Новый баланс:</b> {user_data['balance']:,} монет"
    
    buttons = [
        [{"text": "🪙 ИГРАТЬ ЕЩЁ", "callback_data": f"coin_bet_{bet_amount}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "game_coin"}]
    ]
    
    send_message(chat_id, result, buttons)

def handle_lottery(chat_id, user_data):
    """Лоттерея"""
    global lottery_jackpot
    
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Билет стоит 100 монет!")
        return
    
    buttons = [
        [{"text": "🎰 КУПИТЬ БИЛЕТ (100)", "callback_data": "buy_lottery_ticket"}],
        [{"text": "🔙 НАЗАД", "callback_data": "games"}]
    ]
    
    send_message(chat_id,
        f"🎰 <b>ЛОТЕРЕЯ</b>\n\n"
        f"💰 Твой баланс: {user_data['balance']:,} монет\n"
        f"🏆 Джекпот: {lottery_jackpot:,} монет\n\n"
        f"<i>Правила:</i>\n"
        f"• Билет = 100 монет\n"
        f"• Каждый билет +50 к джекпоту\n"
        f"• Розыгрыш каждые 24 часа\n"
        f"• Шанс выигрыша: 1 к 1000\n\n"
        f"<b>Купить билет?</b>",
        buttons
    )

def handle_buy_lottery_ticket(chat_id, user_data):
    """Покупка лотерейного билета"""
    global lottery_jackpot
    
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Недостаточно монет!")
        return
    
    user_data["balance"] -= 100
    lottery_jackpot += 50
    
    # Проверяем выигрыш (шанс 1/1000)
    if random.randint(1, 1000) == 777:  # Специальное число для выигрыша
        win_amount = lottery_jackpot
        user_data["balance"] += win_amount
        lottery_jackpot = 10000  # Сбрасываем джекпот
        
        result = f"🎉 <b>ДЖЕКПОТ!</b>\n\n"
        result += f"💰 Вы выиграли {win_amount:,} монет!\n"
        result += f"🎰 Счастливый билет!\n\n"
        result += f"💰 <b>Новый баланс:</b> {user_data['balance']:,} монет"
    else:
        result = f"🎫 <b>БИЛЕТ КУПЛЕН</b>\n\n"
        result += f"💰 Спиcано: 100 монет\n"
        result += f"🏆 Джекпот: {lottery_jackpot:,} монет\n"
        result += f"💰 Остаток: {user_data['balance']:,} монет\n\n"
        result += f"<i>Удачи в следующем розыгрыше!</i>"
    
    buttons = [
        [{"text": "🎰 КУПИТЬ ЕЩЁ", "callback_data": "buy_lottery_ticket"}],
        [{"text": "🔙 НАЗАД", "callback_data": "lottery"}]
    ]
    
    send_message(chat_id, result, buttons)

# ========== КОМАНДА /TOP ==========
def handle_top_command(chat_id, user_data):
    """Топ игроков"""
    if not users_db:
        send_message(chat_id, "📊 <b>ТОП ИГРОКОВ</b>\n\n<i>Ещё нет игроков!</i>")
        return
    
    # Сортируем по балансу
    sorted_users = sorted(users_db.values(), key=lambda x: x.get("balance", 0), reverse=True)[:10]
    
    text = "📊 <b>ТОП ИГРОКОВ ПО БАЛАНСУ</b>\n\n"
    
    for i, user in enumerate(sorted_users, 1):
        username = user.get("username", "без имени")
        if not username:
            username = user.get("name", f"Игрок {user['id']}")
        
        badge = ""
        if user.get("admin", False):
            admin_index = user.get("admin_index", -1)
            badge = "👑" if admin_index in [0, 1] else "⚡"
        
        text += f"{i}. {badge} @{username}\n"
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
        if not username:
            username = user.get("name", f"Игрок {user['id']}")
        
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
        if not username:
            username = user.get("name", f"Игрок {user['id']}")
        
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
        if not username:
            username = user.get("name", f"Игрок {user['id']}")
        
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
        f"📢 <b>Наш канал:</b> @{CHANNEL_USERNAME}\n\n"
        f"<i>Нажми на кнопку, чтобы написать админу напрямую!</i>",
        buttons
    )

# ========== РЭП-БАТТЛЫ С СТАВКАМИ ==========
def handle_rap_battle_menu(chat_id, user_data):
    """Меню рэп-баттлов"""
    # Найти доступных противников
    opponents = []
    for opponent_id, opponent_data in users_db.items():
        if opponent_id != user_data["id"] and opponent_data.get("balance", 0) >= 100:
            opponents.append(opponent_data)
    
    text = f"🎤 <b>РЭП-БАТТЛЫ</b>\n\n"
    text += f"💰 <b>Твой баланс:</b> {user_data['balance']:,} монет\n"
    text += f"🏆 <b>Рекорд:</b> {user_data.get('wins', 0)}/{user_data.get('losses', 0)}\n\n"
    
    if opponents:
        text += "<b>Доступные противники:</b>\n"
        for i, opponent in enumerate(opponents[:5], 1):
            text += f"{i}. @{opponent['username']} - {opponent['level']} ур., {opponent['balance']:,} монет\n"
        
        text += f"\n<i>Всего игроков: {len(opponents)}</i>"
    else:
        text += "😢 <i>Нет доступных противников</i>\n\n"
        text += "<i>Пригласи друзей или подожди!</i>"
    
    buttons = [
        [{"text": "⚔️ НАЙТИ ПРОТИВНИКА", "callback_data": "battle_find"}],
        [{"text": "💰 СОЗДАТЬ БАТТЛ СО СТАВКОЙ", "callback_data": "battle_create"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_create_battle(chat_id, user_data):
    """Создание баттла со ставкой"""
    if user_data["balance"] < 100:
        send_message(chat_id, "❌ Минимальная ставка - 100 монет!")
        return
    
    buttons = [
        [{"text": "💰 СТАВКА 100", "callback_data": "bet_100"}],
        [{"text": "💰 СТАВКА 500", "callback_data": "bet_500"}],
        [{"text": "💰 СТАВКА 1000", "callback_data": "bet_1000"}],
        [{"text": "💰 СТАВКА 5000", "callback_data": "bet_5000"}],
        [{"text": "💎 СТАВКА 10000", "callback_data": "bet_10000"}],
        [{"text": "🔙 НАЗАД", "callback_data": "rap_battle"}]
    ]
    
    send_message(chat_id,
        f"💰 <b>СОЗДАНИЕ БАТТЛА СО СТАВКОЙ</b>\n\n"
        f"🎤 Создатель: @{user_data['username']}\n"
        f"💰 Твой баланс: {user_data['balance']:,} монет\n\n"
        f"<i>Выбери сумму ставки:</i>\n"
        f"• Проигравший теряет ставку\n"
        f"• Победитель забирает 90% (10% комиссия)\n"
        f"• Можно играть с любым игроком",
        buttons
    )

def handle_find_opponent(chat_id, user_data, bet_amount=None):
    """Поиск противника для баттла"""
    # Ищем противника с похожим уровнем
    suitable_opponents = []
    
    for opponent_id, opponent_data in users_db.items():
        if (opponent_id != user_data["id"] and 
            opponent_data.get("balance", 0) >= (bet_amount or 100) and
            abs(opponent_data.get("level", 1) - user_data.get("level", 1)) <= 10):
            suitable_opponents.append(opponent_data)
    
    if not suitable_opponents:
        send_message(chat_id, "❌ Нет подходящих противников!")
        return
    
    opponent = random.choice(suitable_opponents)
    
    # Расчет шансов
    player_power = user_data["level"] * 10 + len(user_data.get("rappers", [])) * 5
    opponent_power = opponent["level"] * 10 + len(opponent.get("rappers", [])) * 5
    win_chance = int((player_power / (player_power + opponent_power)) * 100)
    
    bet_text = f"💰 Ставка: {bet_amount:,} монет\n" if bet_amount else ""
    
    buttons = [
        [{"text": "⚔️ ПРИНЯТЬ ВЫЗОВ", "callback_data": f"accept_{opponent['id']}_{bet_amount or 0}"}],
        [{"text": "🔍 НАЙТИ ДРУГОГО", "callback_data": f"find_{bet_amount or 0}"}],
        [{"text": "🔙 НАЗАД", "callback_data": "rap_battle"}]
    ]
    
    send_message(chat_id,
        f"🎤 <b>НАЙДЕН ПРОТИВНИК!</b>\n\n"
        f"👤 <b>Противник:</b> @{opponent['username']}\n"
        f"⭐ <b>Уровень:</b> {opponent['level']}\n"
        f"🎤 <b>Рэперов:</b> {len(opponent.get('rappers', []))}\n"
        f"🏆 <b>Статистика:</b> {opponent.get('wins', 0)}/{opponent.get('losses', 0)}\n"
        f"{bet_text}"
        f"📊 <b>Ваш шанс на победу:</b> {win_chance}%\n\n"
        f"<i>Готов сразиться?</i>",
        buttons
    )

def handle_start_battle(chat_id, player1, player2, bet_amount=0):
    """Начало баттла"""
    # Проверяем балансы
    if bet_amount > 0:
        if player1["balance"] < bet_amount:
            send_message(chat_id, f"❌ @{player1['username']} недостаточно монет!")
            return
        if player2["balance"] < bet_amount:
            send_message(chat_id, f"❌ @{player2['username']} недостаточно монет!")
            return
        
        # Блокируем ставки
        player1["balance"] -= bet_amount
        player2["balance"] -= bet_amount
    
    # Расчет исхода
    p1_power = player1["level"] * 10 + len(player1.get("rappers", [])) * 5
    p2_power = player2["level"] * 10 + len(player2.get("rappers", [])) * 5
    total_power = p1_power + p2_power
    
    # Добавляем случайность
    p1_chance = (p1_power / total_power) * 0.7 + random.random() * 0.3
    
    if p1_chance > 0.5:
        winner = player1
        loser = player2
    else:
        winner = player2
        loser = player1
    
    # Выплаты
    if bet_amount > 0:
        win_amount = int(bet_amount * 2 * 0.9)  # 10% комиссия
        winner["balance"] += win_amount
    
    winner["wins"] = winner.get("wins", 0) + 1
    loser["losses"] = loser.get("losses", 0) + 1
    
    # Сообщение о результате
    bet_text = f"\n💰 <b>Ставка:</b> {bet_amount:,} монет\n" if bet_amount > 0 else ""
    win_text = f"\n💵 <b>Выигрыш:</b> {win_amount:,} монет" if bet_amount > 0 else ""
    
    send_message(chat_id,
        f"🏆 <b>РЕЗУЛЬТАТ БАТТЛА</b>\n\n"
        f"🎤 @{player1['username']} vs @{player2['username']}\n"
        f"{bet_text}"
        f"🥇 <b>ПОБЕДИТЕЛЬ:</b> @{winner['username']}!\n"
        f"{win_text}\n\n"
        f"📊 <b>Статистика обновлена:</b>\n"
        f"• @{winner['username']}: {winner['wins']} побед\n"
        f"• @{loser['username']}: {loser['losses']} поражений"
    )

# ========== КРИПТОВАЛЮТНЫЙ ТРЕЙДИНГ ==========
def handle_crypto_trading(chat_id, user_data):
    """Криптовалютный трейдинг"""
    user_stocks = user_data.get("stocks", {})
    
    text = "₿ <b>КРИПТОВАЛЮТНЫЙ ТРЕЙДИНГ</b>\n\n"
    text += "<i>Купи дешево, продай дорого!</i>\n\n"
    
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

# ========== ИГРЫ ==========
def handle_games_menu(chat_id):
    """Меню игр"""
    buttons = [
        [{"text": "🎲 КОСТИ", "callback_data": "game_dice"}],
        [{"text": "🎰 СЛОТЫ", "callback_data": "game_slots"}],
        [{"text": "🪙 ОРЁЛ/РЕШКА", "callback_data": "game_coin"}],
        [{"text": "🎰 ЛОТЕРЕЯ", "callback_data": "lottery"}],
        [{"text": "💰 ЗАРАБОТОК", "callback_data": "earnings"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id,
        "🎮 <b>МИНИ-ИГРЫ И ЗАРАБОТОК</b>\n\n"
        "<i>Выбери раздел:</i>\n\n"
        "• 🎮 Классические игры\n"
        "• 💰 Дополнительный заработок\n"
        "• ⚫ Нелегальный бизнес\n"
        "• 🎤 Рэп-баттлы на деньги\n"
        "• ₿ Криптовалютный трейдинг",
        buttons
    )

def handle_extra_earnings(chat_id, user_data):
    """Дополнительные способы заработка"""
    text = "💰 <b>ДОПОЛНИТЕЛЬНЫЙ ЗАРАБОТОК</b>\n\n"
    text += "<i>Выбери способ заработка:</i>\n\n"
    text += "1. ⚫ <b>Нелегальный бизнес</b> - высокий риск/доход\n"
    text += "2. 🎤 <b>Рэп-баттлы</b> - сражения на деньги\n"
    text += "3. ₿ <b>Криптотрейдинг</b> - инвестиции\n"
    text += "4. ⚫ <b>Гангстеры</b> - бонусы от банды\n"
    
    buttons = [
        [{"text": "⚫ НЕЛЕГАЛКА", "callback_data": "illegal"}],
        [{"text": "🎤 РЭП-БАТТЛЫ", "callback_data": "rap_battle"}],
        [{"text": "₿ КРИПТА", "callback_data": "crypto"}],
        [{"text": "⚫ ГАНГСТЕРЫ", "callback_data": "gangs"}],
        [{"text": "🔙 НАЗАД", "callback_data": "back"}]
    ]
    
    send_message(chat_id, text, buttons)

# ========== АДМИН ПАНЕЛЬ - ИСПРАВЛЕНАЯ ==========
def handle_admin_panel(chat_id, user_data):
    """Админ панель"""
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Только для админов!")
        return
    
    admin_index = user_data.get("admin_index", -1)
    
    buttons = [
        [{"text": "💰 БАЛАНСЫ", "callback_data": "admin_balance"}, 
         {"text": "📊 УРОВНИ", "callback_data": "admin_levels"}],
        [{"text": "🎤 РЭПЕРЫ", "callback_data": "admin_rappers"}, 
         {"text": "📈 СТАТИСТИКА", "callback_data": "admin_stats"}],
        [{"text": "🔧 МОДЕРАЦИЯ", "callback_data": "admin_mod"}, 
         {"text": "📬 УВЕДОМЛЕНИЯ", "callback_data": "admin_notifications"}],
    ]
    
    # Кнопки только для владельцев
    if admin_index in [0, 1]:
        buttons.append([{"text": "👑 УПРАВЛЕНИЕ АДМИНАМИ", "callback_data": "admin_manage"}])
    
    buttons.append([{"text": "💾 СОХРАНИТЬ ДАННЫЕ", "callback_data": "admin_save"}])
    buttons.append([{"text": "🔙 НАЗАД", "callback_data": "back"}])
    
    admin_type = "👑 ВЛАДЕЛЕЦ" if admin_index in [0, 1] else "⚡ АДМИН"
    
    send_message(chat_id,
        f"⚡ <b>АДМИН-ПАНЕЛЬ</b> ({admin_type})\n\n"
        f"👤 Админ: @{user_data['username']}\n"
        f"💰 Баланс: {user_data['balance']:,}\n"
        f"🎤 Рэперов: {len(user_data['rappers'])}\n"
        f"📬 Уведомлений: {len(admin_notifications)}\n"
        f"🚫 Забанено: {len(banned_users)}\n\n"
        f"<i>Выбери раздел:</i>",
        buttons
    )

def handle_admin_balance_panel(chat_id):
    """Управление балансами"""
    buttons = [
        [{"text": "💸 ВЫДАТЬ МОНЕТЫ", "callback_data": "admin_give"}],
        [{"text": "📉 ЗАБРАТЬ МОНЕТЫ", "callback_data": "admin_take"}],
        [{"text": "🎯 УСТАНОВИТЬ БАЛАНС", "callback_data": "admin_setbalance"}],
        [{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id,
        "💰 <b>УПРАВЛЕНИЕ БАЛАНСАМИ</b>\n\n"
        "<i>Команды:</i>\n"
        "<code>/give @user сумма</code> - выдать\n"
        "<code>/take @user сумма</code> - забрать\n"
        "<code>/setbalance @user сумма</code> - установить\n\n"
        "<i>Пример:</i>\n"
        "<code>/give @prostokiril 10000</code>",
        buttons
    )

def handle_admin_levels_panel(chat_id):
    """Управление уровнями"""
    buttons = [
        [{"text": "⬆️ ПОВЫСИТЬ УРОВЕНЬ", "callback_data": "admin_lvlup"}],
        [{"text": "🎯 УСТАНОВИТЬ УРОВЕНЬ", "callback_data": "admin_setlvl"}],
        [{"text": "📊 ДОБАВИТЬ ОПЫТ", "callback_data": "admin_addexp"}],
        [{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id,
        "📊 <b>УПРАВЛЕНИЕ УРОВНЯМИ</b>\n\n"
        "<i>Команды:</i>\n"
        "<code>/setlevel @user уровень</code>\n"
        "<code>/addexp @user опыт</code>\n\n"
        "<i>Уровень: 1-1000</i>",
        buttons
    )

def handle_admin_rappers_panel(chat_id):
    """Управление рэперами"""
    buttons = [
        [{"text": "➕ ДОБАВИТЬ РЭПЕРА", "callback_data": "admin_addrap"}],
        [{"text": "➖ ЗАБРАТЬ РЭПЕРА", "callback_data": "admin_remrap"}],
        [{"text": "🎯 ВЫДАТЬ ВСЕХ", "callback_data": "admin_allrap"}],
        [{"text": "🗑️ ОЧИСТИТЬ ВСЕХ", "callback_data": "admin_clrrap"}],
        [{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id,
        "🎤 <b>УПРАВЛЕНИЕ РЭПЕРАМИ</b>\n\n"
        "<i>Команды:</i>\n"
        "<code>/addrapper @user id</code>\n"
        "<code>/remrapper @user id</code>\n"
        "<code>/allrappers @user</code>\n"
        "<code>/clearrappers @user</code>\n\n"
        "<i>ID рэперов:</i> cowboy, smoke, liltrap, cloudy, sadboy, ghost, money, ice, fire, diamond",
        buttons
    )

def handle_admin_stats_panel(chat_id):
    """Статистика бота"""
    total_users = len(users_db)
    total_balance = sum(u.get("balance", 0) for u in users_db.values())
    total_rappers = sum(len(u.get("rappers", [])) for u in users_db.values())
    online_users = sum(1 for uid in users_db if time.time() - last_message_time.get(uid, 0) < 3600)
    
    buttons = [[{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]]
    
    send_message(chat_id,
        f"📊 <b>СТАТИСТИКА БОТА</b>\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🟢 Онлайн: {online_users}\n"
        f"💰 Общий баланс: {total_balance:,}\n"
        f"🎤 Всего рэперов: {total_rappers}\n"
        f"🎰 Джекпот лотереи: {lottery_jackpot:,}\n"
        f"🚫 Забанено: {len(banned_users)}\n"
        f"📅 Дата: {time.strftime('%d.%m.%Y %H:%M')}",
        buttons
    )

def handle_admin_mod_panel(chat_id):
    """Модерация"""
    buttons = [
        [{"text": "🚫 МУТ В КАНАЛЕ", "callback_data": "admin_mute"}],
        [{"text": "✅ РАЗМУТ В КАНАЛЕ", "callback_data": "admin_unmute"}],
        [{"text": "⚠️ ПРЕДУПРЕЖДЕНИЕ", "callback_data": "admin_warn"}],
        [{"text": "⛔ БАН", "callback_data": "admin_ban"}],
        [{"text": "✅ РАЗБАН", "callback_data": "admin_unban"}],
        [{"text": "🔄 ОБНУЛИТЬ ИГРОКА", "callback_data": "admin_reset"}],
        [{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id,
        "🔧 <b>МОДЕРАЦИЯ КАНАЛА</b>\n\n"
        "<i>Команды:</i>\n"
        "<code>/mute @user 5</code> - мут на 5 мин\n"
        "<code>/unmute @user</code> - размут\n"
        "<code>/warn @user</code> - предупреждение\n"
        "<code>/ban @user причина</code> - бан\n"
        "<code>/unban @user</code> - разбан\n"
        "<code>/reset @user</code> - обнулить\n\n"
        "<i>Бот должен быть админом в канале!</i>",
        buttons
    )

def handle_admin_manage_panel(chat_id, user_data):
    """Управление админами (только для владельцев)"""
    if user_data.get("admin_index", -1) not in [0, 1]:
        send_message(chat_id, "❌ Только для владельцев!")
        return
    
    text = "👑 <b>УПРАВЛЕНИЕ АДМИНАМИ</b>\n\n"
    
    # Основные админы
    text += "<b>Владельцы:</b>\n"
    for i, admin in enumerate(ADMINS, 1):
        text += f"{i}. @{admin}\n"
    
    # Дополнительные админы
    if ADDITIONAL_ADMINS:
        text += f"\n<b>Дополнительные админы ({len(ADDITIONAL_ADMINS)}):</b>\n"
        for i, admin in enumerate(ADDITIONAL_ADMINS, 1):
            text += f"{i}. @{admin}\n"
    else:
        text += "\n<b>Дополнительные админы:</b> Нет\n"
    
    text += f"\n<b>Всего админов:</b> {len(ADMINS) + len(ADDITIONAL_ADMINS)}"
    
    buttons = [
        [{"text": "➕ НАЗНАЧИТЬ АДМИНА", "callback_data": "admin_add"}],
        [{"text": "➖ СНЯТЬ АДМИНА", "callback_data": "admin_remove"}],
        [{"text": "🔙 В АДМИНКУ", "callback_data": "admin_panel"}]
    ]
    
    send_message(chat_id, text, buttons)

def handle_admin_add_panel(chat_id):
    """Назначение админа - форма"""
    send_message(chat_id,
        "➕ <b>НАЗНАЧЕНИЕ АДМИНА</b>\n\n"
        "<i>Используй команду:</i>\n"
        "<code>/setadmin @username</code>\n\n"
        "<b>Пример:</b>\n"
        "<code>/setadmin @prostokiril</code>\n\n"
        "<i>Новый админ получит:</i>\n"
        "• 999,999 монет\n"
        "• Всех рэперов\n"
        "• Уровень 100\n"
        "• Все предметы\n"
        "• Доступ к админ-панели"
    )

def handle_admin_remove_panel(chat_id):
    """Снятие админа - форма"""
    send_message(chat_id,
        "➖ <b>СНЯТИЕ АДМИНА</b>\n\n"
        "<i>Используй команду:</i>\n"
        "<code>/removeadmin @username</code>\n\n"
        "<b>Пример:</b>\n"
        "<code>/removeadmin @username</code>\n\n"
        "<i>⚠️ Внимание:</i>\n"
        "• Аккаунт будет сброшен\n"
        "• Нельзя снять владельцев"
    )

# ========== МОДЕРАЦИЯ ==========
def handle_chat_message(msg):
    """Обработка сообщений в чате для модерации"""
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = msg.get("text", "").lower()
    username = msg["from"].get("username", "")
    
    # Проверка на бан
    if user_id in banned_users:
        # Удаляем сообщение забаненного
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                json={"chat_id": chat_id, "message_id": msg["message_id"]},
                timeout=5
            )
        except:
            pass
        return False
    
    # Проверка плохих слов
    for bad_word in BAD_WORDS:
        if bad_word in text:
            # Добавляем предупреждение
            chat_warnings[user_id] += 1
            
            if chat_warnings[user_id] >= 3:
                # Мут на 5 минут
                mute_duration = 300  # 5 минут в секундах
                muted_users[user_id] = time.time() + mute_duration
                
                # Уведомление админам
                notification = f"🚫 @{username} получил мут на 5 мин за плохие слова"
                add_admin_notification(notification)
                
                send_message(chat_id,
                    f"🚫 @{username} получил мут на 5 минут!\n"
                    f"Причина: Использование запрещенных слов"
                )
            else:
                send_message(chat_id,
                    f"⚠️ @{username}, не используйте запрещенные слова!\n"
                    f"Предупреждение {chat_warnings[user_id]}/3"
                )
            break
    
    # Проверка на спам (более 5 сообщений за 10 секунд)
    current_time = time.time()
    last_time = last_message_time.get(user_id, 0)
    
    if current_time - last_time < 2:  # Меньше 2 секунд между сообщениями
        spam_count = messages_db.get(user_id, 0) + 1
        messages_db[user_id] = spam_count
        
        if spam_count > 5:
            # Мут на 2 минуты за спам
            mute_duration = 120
            muted_users[user_id] = current_time + mute_duration
            
            # Уведомление админам
            notification = f"🚫 @{username} получил мут на 2 мин за спам"
            add_admin_notification(notification)
            
            send_message(chat_id,
                f"🚫 @{username} получил мут на 2 минуты!\n"
                f"Причина: Спам"
            )
    else:
        messages_db[user_id] = 1
    
    last_message_time[user_id] = current_time
    
    # Проверка мута
    if user_id in muted_users:
        if current_time < muted_users[user_id]:
            # Пользователь все еще в муте
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/deleteMessage",
                    json={"chat_id": chat_id, "message_id": msg["message_id"]},
                    timeout=5
                )
            except:
                pass
            return False
        else:
            # Мут истек
            del muted_users[user_id]
            if user_id in chat_warnings:
                chat_warnings[user_id] = max(0, chat_warnings[user_id] - 1)
    
    return True

# ========== АДМИН КОМАНДЫ ==========
def handle_admin_command(user_data, chat_id, command, params):
    """Обработка админ-команд"""
    if not user_data.get("admin", False):
        send_message(chat_id, "❌ Нет прав!")
        return
    
    parts = params.strip().split()
    
    if command == "/getid":
        send_message(chat_id, f"🆔 <b>ID этого чата:</b> <code>{chat_id}</code>\n\n"
                           f"📢 <b>Канал для подписки:</b> @{CHANNEL_USERNAME}")
        return
    
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
        
        target = find_user_by_username(username)
        if target:
            target["balance"] += amount
            notification = f"💰 @{user_data['username']} выдал {amount:,} монет @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Выдано {amount:,} монет @{target['username']}")
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
        
        target = find_user_by_username(username)
        if target:
            if amount > target["balance"]:
                amount = target["balance"]
            target["balance"] -= amount
            notification = f"📉 @{user_data['username']} забрал {amount:,} монет у @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Забрано {amount:,} монет у @{target['username']}")
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
        
        target = find_user_by_username(username)
        if target:
            target["balance"] = amount
            notification = f"🎯 @{user_data['username']} установил баланс {amount:,} монет @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Баланс установлен {amount:,} монет @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/setlevel" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        try:
            level = int(parts[1])
            if level < 1 or level > 1000:
                send_message(chat_id, "❌ Уровень должен быть от 1 до 1000!")
                return
        except:
            send_message(chat_id, "❌ Неверный уровень!")
            return
        
        target = find_user_by_username(username)
        if target:
            target["level"] = level
            target["xp"] = (level - 1) * 1000
            notification = f"⭐ @{user_data['username']} установил уровень {level} @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Уровень {level} установлен для @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/addrapper" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        rapper_id = parts[1]
        
        target = find_user_by_username(username)
        if target:
            if rapper_id in RAPPERS:
                if rapper_id not in target["rappers"]:
                    target["rappers"].append(rapper_id)
                    notification = f"🎤 @{user_data['username']} добавил рэпера {RAPPERS[rapper_id]['name']} @{target['username']}"
                    add_admin_notification(notification)
                    send_message(chat_id, f"✅ Рэпер {RAPPERS[rapper_id]['name']} добавлен @{target['username']}")
                else:
                    send_message(chat_id, f"✅ У @{target['username']} уже есть этот рэпер")
            else:
                send_message(chat_id, "❌ Неверный ID рэпера!")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/remrapper" and len(parts) >= 2:
        username = parts[0].lstrip('@')
        rapper_id = parts[1]
        
        target = find_user_by_username(username)
        if target:
            if rapper_id in RAPPERS:
                if rapper_id in target["rappers"]:
                    target["rappers"].remove(rapper_id)
                    notification = f"➖ @{user_data['username']} забрал рэпера {RAPPERS[rapper_id]['name']} у @{target['username']}"
                    add_admin_notification(notification)
                    send_message(chat_id, f"✅ Рэпер {RAPPERS[rapper_id]['name']} забран у @{target['username']}")
                else:
                    send_message(chat_id, f"✅ У @{target['username']} нет этого рэпера")
            else:
                send_message(chat_id, "❌ Неверный ID рэпера!")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/allrappers" and len(parts) >= 1:
        username = parts[0].lstrip('@')
        target = find_user_by_username(username)
        
        if target:
            target["rappers"] = list(RAPPERS.keys())
            notification = f"🎯 @{user_data['username']} выдал всех рэперов @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Все рэперы выданы @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/clearrappers" and len(parts) >= 1:
        username = parts[0].lstrip('@')
        target = find_user_by_username(username)
        
        if target:
            target["rappers"] = []
            notification = f"🗑️ @{user_data['username']} очистил рэперов @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Все рэперы удалены у @{target['username']}")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/reset" and len(parts) >= 1:
        username = parts[0].lstrip('@')
        target = find_user_by_username(username)
        
        if target:
            target.update({
                "balance": 5000,
                "rappers": [],
                "level": 1,
                "xp": 0,
                "rank": "👤 НОВИЧОК",
                "items": [],
                "wins": 0,
                "losses": 0,
                "gang": None,
                "stocks": {},
                "daily_streak": 0
            })
            notification = f"🔄 @{user_data['username']} обнулил аккаунт @{target['username']}"
            add_admin_notification(notification)
            send_message(chat_id, f"✅ Аккаунт @{target['username']} сброшен!")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    elif command == "/stats":
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
            f"🎰 Джекпот лотереи: {lottery_jackpot:,}\n"
            f"🚫 Забанено: {len(banned_users)}\n"
            f"📅 Дата: {time.strftime('%d.%m.%Y %H:%M')}"
        )
    
    # ФИКС: Команда /mute с исправленным поиском пользователя
    elif command == "/mute":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /mute @username [минуты]\nПример: /mute @user 5")
            return
        
        username = parts[0].lstrip('@')
        
        # Проверяем, есть ли время мута
        if len(parts) >= 2:
            try:
                minutes = int(parts[1])
                if minutes < 1 or minutes > 1440:
                    send_message(chat_id, "❌ Время мута должно быть от 1 до 1440 минут!")
                    return
            except:
                send_message(chat_id, "❌ Неверное время!")
                return
        else:
            minutes = 5  # Значение по умолчанию
        
        # Используем улучшенную функцию поиска
        target = find_user_by_username_or_get_from_telegram(username)
        if target:
            mute_duration = minutes * 60
            muted_users[target["id"]] = time.time() + mute_duration
            notification = f"🚫 @{user_data['username']} замутил @{target['username']} на {minutes} мин"
            add_admin_notification(notification)
            
            # Отправляем сообщение в чат
            send_message(chat_id, f"✅ @{target['username']} замьючен на {minutes} минут")
            
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    # ФИКС: Команда /unmute с исправленным поиском пользователя
    elif command == "/unmute":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /unmute @username")
            return
        
        username = parts[0].lstrip('@')
        
        # Ищем пользователя
        target = find_user_by_username_or_get_from_telegram(username)
        
        if target:
            if target["id"] in muted_users:
                del muted_users[target["id"]]
                notification = f"✅ @{user_data['username']} размутил @{target['username']}"
                add_admin_notification(notification)
                send_message(chat_id, f"✅ @{target['username']} размьючен")
            else:
                send_message(chat_id, f"✅ @{target['username']} не в муте")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    # ФИКС: Команда /warn с исправленным поиском пользователя
    elif command == "/warn":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /warn @username")
            return
        
        username = parts[0].lstrip('@')
        
        # Используем улучшенную функцию поиска
        target = find_user_by_username_or_get_from_telegram(username)
        
        if target:
            chat_warnings[target["id"]] = chat_warnings.get(target["id"], 0) + 1
            warnings = chat_warnings[target["id"]]
            
            notification = f"⚠️ @{user_data['username']} предупредил @{target['username']} ({warnings}/3)"
            add_admin_notification(notification)
            
            if warnings >= 3:
                # Автоматический мут
                mute_duration = 300
                muted_users[target["id"]] = time.time() + mute_duration
                send_message(chat_id, 
                    f"⚠️ @{target['username']} получил предупреждение {warnings}/3\n"
                    f"🚫 Автоматический мут на 5 минут!"
                )
            else:
                send_message(chat_id, f"⚠️ @{target['username']} получил предупреждение {warnings}/3")
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    # ФИКС: Команда /ban с исправленным поиском пользователя
    elif command == "/ban":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /ban @username [причина]")
            return
        
        username = parts[0].lstrip('@')
        reason = " ".join(parts[1:]) if len(parts) > 1 else "Нарушение правил"
        
        # Используем улучшенную функцию поиска
        target = find_user_by_username_or_get_from_telegram(username)
        
        if target:
            # Нельзя забанить админа или владельца
            if target.get("admin", False):
                send_message(chat_id, "❌ Нельзя забанить админа!")
                return
            
            # Проверяем, не владелец ли
            if target["username"].lower() in [a.lower() for a in ADMINS]:
                send_message(chat_id, "❌ Нельзя забанить владельца!")
                return
            
            banned_users[target["id"]] = {
                "username": target["username"],
                "admin": user_data["username"],
                "reason": reason,
                "time": time.strftime("%d.%m.%Y %H:%M:%S")
            }
            
            notification = f"⛔ @{user_data['username']} забанил @{target['username']}\nПричина: {reason}"
            add_admin_notification(notification)
            
            # Удаляем из мутов если был там
            if target["id"] in muted_users:
                del muted_users[target["id"]]
            
            send_message(chat_id,
                f"⛔ <b>ПОЛЬЗОВАТЕЛЬ ЗАБАНЕН!</b>\n\n"
                f"👤 @{target['username']}\n"
                f"👮‍♂️ Админ: @{user_data['username']}\n"
                f"📝 Причина: {reason}\n"
                f"🕒 Время: {time.strftime('%d.%m.%Y %H:%M:%S')}"
            )
            
            # Пытаемся кикнуть из канала
            if CHANNEL_ID:
                try:
                    url = f"https://api.telegram.org/bot{TOKEN}/banChatMember"
                    data = {
                        "chat_id": CHANNEL_ID,
                        "user_id": target["id"],
                        "revoke_messages": True
                    }
                    requests.post(url, json=data, timeout=5)
                except:
                    pass
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден!")
    
    # ФИКС: Команда /unban с исправленным поиском пользователя
    elif command == "/unban":
        if len(parts) < 1:
            send_message(chat_id, "❌ Использование: /unban @username")
            return
        
        username = parts[0].lstrip('@')
        
        # Ищем в забаненных
        target_id = None
        target_username = ""
        for uid, ban_info in banned_users.items():
            if ban_info.get("username", "").lower() == username.lower():
                target_id = uid
                target_username = ban_info.get("username", username)
                break
        
        if target_id:
            # Получаем данные пользователя
            target = users_db.get(target_id)
            if not target:
                # Создаем минимальную запись
                target = {
                    "id": target_id,
                    "username": target_username,
                    "name": f"Пользователь {target_id}"
                }
                users_db[target_id] = target
            
            del banned_users[target_id]
            notification = f"✅ @{user_data['username']} разбанил @{target['username']}"
            add_admin_notification(notification)
            
            send_message(chat_id, f"✅ @{target['username']} разбанен!")
            
            # Пытаемся разбанить в канале
            if CHANNEL_ID:
                try:
                    url = f"https://api.telegram.org/bot{TOKEN}/unbanChatMember"
                    data = {
                        "chat_id": CHANNEL_ID,
                        "user_id": target_id,
                        "only_if_banned": True
                    }
                    requests.post(url, json=data, timeout=5)
                except:
                    pass
        else:
            send_message(chat_id, f"❌ Пользователь @{username} не найден в списке забаненных!")
    
    # ФИКС: Команда /setadmin
    elif command == "/setadmin":
        handle_set_admin(chat_id, user_data, params)
    
    # ФИКС: Команда /removeadmin
    elif command == "/removeadmin":
        handle_remove_admin(chat_id, user_data, params)

# ========== START МЕНЮ ==========
def handle_start(user_data, chat_id):
    """Главное меню"""
    # Проверка на бан
    if user_data["id"] in banned_users:
        ban_info = banned_users[user_data["id"]]
        send_message(chat_id,
            f"⛔ <b>ВЫ ЗАБАНЕНЫ!</b>\n\n"
            f"👮‍♂️ Админ: @{ban_info.get('admin', 'Неизвестно')}\n"
            f"📝 Причина: {ban_info.get('reason', 'Не указана')}\n"
            f"🕒 Время: {ban_info.get('time', 'Неизвестно')}\n\n"
            f"<i>Обратитесь к админу для разбана</i>"
        )
        return
    
    if not user_data.get("admin", False) and not check_subscription(user_data["id"]):
        buttons = [
            [{"text": "📢 ПОДПИСАТЬСЯ", "url": f"https://t.me/{CHANNEL_USERNAME}"}],
            [{"text": "✅ Я ПОДПИСАЛСЯ", "callback_data": "check_sub"}]
        ]
        
        send_message(chat_id,
            f"🔒 <b>ДОСТУП ЗАКРЫТ</b>\n\n"
            f"Подпишись на канал:\n<b>@{CHANNEL_USERNAME}</b>\n\n"
            f"👑 <b>Владельцы:</b>\n"
            f"• @{ADMINS[0]}\n"
            f"• @{ADMINS[1]}",
            buttons
        )
        return
    
    if user_data.get("admin", False):
        admin_index = user_data.get("admin_index", -1)
        admin_badge = "👑" if admin_index == 0 else "💩" if admin_index == 1 else "⚡"
        
        buttons = [
            [{"text": "🛒 МАГАЗИН", "callback_data": "shop"}, {"text": "🎒 ИНВЕНТАРЬ", "callback_data": "inventory"}],
            [{"text": "💰 БАЛАНС", "callback_data": "balance"}, {"text": "👤 ПРОФИЛЬ", "callback_data": "profile"}],
            [{"text": "🎮 ИГРЫ", "callback_data": "games"}, {"text": "📊 ТОП", "callback_data": "top"}],
            [{"text": "⚡ АДМИН-ПАНЕЛЬ", "callback_data": "admin_panel"}],
            [{"text": "📈 СТАТИСТИКА", "callback_data": "stats"}]
        ]
        
        send_message(chat_id,
            f"{admin_badge} <b>АДМИН-ПАНЕЛЬ</b>\n\n"
            f"👋 Привет, {user_data['name']}!\n\n"
            f"💰 <b>Баланс:</b> {user_data['balance']:,} монет\n"
            f"⭐ <b>Уровень:</b> {user_data['level']}\n"
            f"🎤 <b>Рэперов:</b> {len(user_data['rappers'])}\n"
            f"⚫ <b>Банда:</b> {GANGS.get(user_data.get('gang', ''), {}).get('name', 'Нет')}\n"
            f"🏆 <b>Побед:</b> {user_data.get('wins', 0)}\n\n"
            f"<i>Доступны все функции!</i>",
            buttons
        )
    else:
        buttons = [
            [{"text": "🛒 МАГАЗИН", "callback_data": "shop"}, {"text": "🎒 ИНВЕНТАРЬ", "callback_data": "inventory"}],
            [{"text": "💰 БАЛАНС", "callback_data": "balance"}, {"text": "👤 ПРОФИЛЬ", "callback_data": "profile"}],
            [{"text": "🎮 ИГРЫ", "callback_data": "games"}, {"text": "📊 ТОП", "callback_data": "top"}],
            [{"text": "🎁 БОНУС", "callback_data": "daily"}, {"text": "📈 СТАТИСТИКА", "callback_data": "stats"}]
        ]
        
        send_message(chat_id,
            f"🎵 <b>ULTIMATE RAP BOSS</b>\n\n"
            f"👋 Привет, {user_data['name']}!\n\n"
            f"💰 <b>Баланс:</b> {user_data['balance']:,} монет\n"
            f"⭐ <b>Уровень:</b> {user_data['level']}\n"
            f"🎤 <b>Рэперов:</b> {len(user_data['rappers'])}\n"
            f"⚫ <b>Банда:</b> {GANGS.get(user_data.get('gang', ''), {}).get('name', 'Нет')}\n"
            f"🏆 <b>Побед:</b> {user_data.get('wins', 0)}\n\n"
            f"<i>Выбери раздел:</i>",
            buttons
        )

# ========== MAIN LOOP ==========
def main():
    print("🚀 Загрузка данных...")
    load_data()
    print("✅ Данные загружены!")
    print("🤖 Бот запущен! Ожидаю сообщения...")
    
    last_save_time = time.time()
    last_crypto_update = time.time()
    
    offset = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Автосохранение каждые 5 минут
            if current_time - last_save_time > 300:
                save_data()
                last_save_time = current_time
            
            # Обновление цен крипты
            if current_time - last_crypto_update > 300:
                update_crypto_prices()
                last_crypto_update = current_time
            
            # Очистка истекших мутов
            expired_mutes = [uid for uid, end_time in list(muted_users.items()) if current_time >= end_time]
            for uid in expired_mutes:
                if uid in muted_users:
                    del muted_users[uid]
            
            # Получение обновлений
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"offset": offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                
                if data.get("ok"):
                    for update in data["result"]:
                        offset = update["update_id"] + 1
                        
                        # Сообщения
                        if "message" in update and "chat" in update["message"]:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            
                            # Модерация чатов
                            if chat_id < 0:
                                if not handle_chat_message(msg):
                                    continue
                            
                            if "text" in msg:
                                user_id = msg["from"]["id"]
                                text = msg["text"]
                                username = msg["from"].get("username", "")
                                first_name = msg["from"].get("first_name", "Игрок")
                                
                                user_data = get_user_data(user_id, username, first_name)
                                
                                # Обработка команд
                                if text == "/start":
                                    handle_start(user_data, chat_id)
                                
                                elif text == "/shop":
                                    handle_shop(chat_id, user_data)
                                
                                elif text == "/inventory":
                                    handle_inventory(chat_id, user_data)
                                
                                elif text == "/games":
                                    handle_games_menu(chat_id)
                                
                                elif text == "/top":
                                    handle_top_command(chat_id, user_data)
                                
                                elif text == "/ask":
                                    handle_ask_command(chat_id, user_data)
                                
                                elif text == "/admin":
                                    handle_admin_panel(chat_id, user_data)
                                
                                elif text == "/save":
                                    save_data()
                                    send_message(chat_id, "💾 <b>Данные сохранены!</b>")
                                
                                # ФИКС: Проверка админ-команд
                                elif user_data.get("admin", False):
                                    # Все админ команды
                                    if (text.startswith("/give ") or text.startswith("/take ") or 
                                        text.startswith("/setbalance ") or text.startswith("/setlevel ") or 
                                        text.startswith("/addrapper ") or text.startswith("/remrapper ") or 
                                        text.startswith("/allrappers ") or text.startswith("/clearrappers ") or 
                                        text.startswith("/reset ") or text.startswith("/mute ") or 
                                        text.startswith("/unmute ") or text.startswith("/warn ") or 
                                        text.startswith("/ban ") or text.startswith("/unban ") or
                                        text.startswith("/setadmin ") or text.startswith("/removeadmin ")):
                                        
                                        parts = text.split(" ", 1)
                                        command = parts[0]
                                        params = parts[1] if len(parts) > 1 else ""
                                        handle_admin_command(user_data, chat_id, command, params)
                                    
                                    # Команды без параметров
                                    elif text in ["/stats", "/getid"]:
                                        handle_admin_command(user_data, chat_id, text, "")
                                    
                                    # Команды setadmin и removeadmin (могут быть без параметров)
                                    elif text.startswith("/setadmin") or text.startswith("/removeadmin"):
                                        parts = text.split(" ", 1)
                                        command = parts[0]
                                        params = parts[1] if len(parts) > 1 else ""
                                        handle_admin_command(user_data, chat_id, command, params)
                        
                        # Callback кнопки
                        elif "callback_query" in update:
                            call = update["callback_query"]
                            call_id = call["id"]
                            user_id = call["from"]["id"]
                            chat_id = call["message"]["chat"]["id"]
                            data = call["data"]
                            username = call["from"].get("username", "")
                            first_name = call["from"].get("first_name", "Игрок")
                            
                            user_data = get_user_data(user_id, username, first_name)
                            
                            # Ответ на callback
                            try:
                                requests.post(
                                    f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                    json={"callback_query_id": call_id},
                                    timeout=5
                                )
                            except:
                                pass
                            
                            # Обработка callback
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
                            
                            elif data == "top":
                                handle_top_command(chat_id, user_data)
                            
                            elif data == "top_balance":
                                handle_top_balance(chat_id)
                            
                            elif data == "top_level":
                                handle_top_level(chat_id)
                            
                            elif data == "top_wins":
                                handle_top_wins(chat_id)
                            
                            elif data.startswith("join_"):
                                gang_id = data[5:]
                                if gang_id in GANGS:
                                    user_data["gang"] = gang_id
                                    if user_id not in GANGS[gang_id]["members"]:
                                        GANGS[gang_id]["members"].append(user_id)
                                    send_message(chat_id, f"✅ Ты вступил в {GANGS[gang_id]['name']}!")
                                else:
                                    send_message(chat_id, "❌ Ошибка!")
                            
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
                                bet_amount = int(data[4:])
                                handle_find_opponent(chat_id, user_data, bet_amount)
                            
                            elif data.startswith("accept_"):
                                parts = data.split("_")
                                if len(parts) == 3:
                                    opponent_id = int(parts[1])
                                    bet_amount = int(parts[2])
                                    opponent = users_db.get(opponent_id)
                                    if opponent:
                                        handle_start_battle(chat_id, user_data, opponent, bet_amount)
                            
                            elif data.startswith("find_"):
                                bet_amount = int(data[5:]) if data[5:] else 0
                                handle_find_opponent(chat_id, user_data, bet_amount)
                            
                            elif data == "check_sub":
                                if check_subscription(user_id):
                                    send_message(chat_id, "✅ Подписка подтверждена! Напиши /start")
                                else:
                                    send_message(chat_id, "❌ Ты еще не подписался на канал!")
                            
                            elif data.startswith("buy_"):
                                rapper_id = data[4:]
                                handle_buy_rapper(chat_id, user_data, rapper_id)
                            
                            elif data == "balance":
                                send_message(chat_id, f"💰 <b>Твой баланс:</b> {user_data['balance']:,} монет")
                            
                            elif data == "profile":
                                gang_name = GANGS.get(user_data.get('gang', ''), {}).get('name', 'Нет')
                                send_message(chat_id,
                                    f"👤 <b>ПРОФИЛЬ</b>\n\n"
                                    f"📛 Имя: {user_data['name']}\n"
                                    f"🔗 @{user_data['username']}\n"
                                    f"💰 Баланс: {user_data['balance']:,}\n"
                                    f"⭐ Уровень: {user_data['level']}\n"
                                    f"🎤 Рэперов: {len(user_data['rappers'])}\n"
                                    f"⚫ Банда: {gang_name}\n"
                                    f"🏆 Побед: {user_data.get('wins', 0)}\n"
                                    f"📅 В боте с: {user_data['join_date']}"
                                )
                            
                            elif data == "game_dice":
                                handle_game_dice(chat_id, user_data)
                            
                            elif data.startswith("dice_bet_"):
                                bet_amount = int(data[9:])
                                handle_dice_game(chat_id, user_data, bet_amount)
                            
                            elif data == "game_slots":
                                handle_game_slots(chat_id, user_data)
                            
                            elif data.startswith("slots_bet_"):
                                bet_amount = int(data[10:])
                                handle_slots_game(chat_id, user_data, bet_amount)
                            
                            elif data == "game_coin":
                                handle_game_coin(chat_id, user_data)
                            
                            elif data.startswith("coin_bet_"):
                                bet_amount = int(data[9:])
                                handle_coin_game(chat_id, user_data, bet_amount)
                            
                            elif data.startswith("coin_side_"):
                                parts = data.split("_")
                                if len(parts) == 4:
                                    side = parts[2]
                                    bet_amount = int(parts[3])
                                    handle_coin_flip(chat_id, user_data, side, bet_amount)
                            
                            elif data == "lottery":
                                handle_lottery(chat_id, user_data)
                            
                            elif data == "buy_lottery_ticket":
                                handle_buy_lottery_ticket(chat_id, user_data)
                            
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
                                send_message(chat_id, "💾 <b>Данные сохранены!</b>")
                            
                            elif data == "clear_notifications":
                                admin_notifications.clear()
                                send_message(chat_id, "🗑️ <b>Уведомления очищены!</b>")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()