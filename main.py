# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import time

# إعداد التوكن من بيئة العمل
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= DATA ENGINE (الأذكار) =================
# تم تقسيمها كقوالب لضمان التنوع وعدم الملل
AZKAR_DATA = {
    "sabah": {
        "title": "☀️ أذكار الصباح",
        "items": [
            {"text": "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له.", "fadl": "من قالها حين يصبح أُعطي خير هذا اليوم."},
            {"text": "اللهم بك أصبحنا، وبك أمسينا، وبك نحيا، وبك نموت، وإليك النشور.", "fadl": "تجديد التوكل على الله في بداية اليوم."},
            {"text": "يا حي يا قيوم برحمتك أستغيث أصلح لي شأني كله ولا تكلني إلى نفسي طرفة عين.", "fadl": "صلاح الشأن كله بإذن الله."}
        ]
    },
    "masaa": {
        "title": "🌙 أذكار المساء",
        "items": [
            {"text": "أمسينـا وأمسى الملك لله والحمد لله، لا إله إلا الله وحده لا شريك له.", "fadl": "حفظ وطمأنينة حتى تصبح."},
            {"text": "اللهم بك أمسينا، وبك أصبحنا، وبك نحيا، وبك نموت، وإليك المصير.", "fadl": "تسليم الأمر لله في ليلك."},
            {"text": "أعوذ بكلمات الله التامات من شر ما خلق.", "fadl": "حماية من الهوام والشرور في الليل."}
        ]
    },
    "salah": {
        "title": "📿 أذكار بعد الصلاة",
        "items": [
            {"text": "أستغفر الله (ثلاثاً) .. اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام.", "fadl": "سنة ثابتة بعد الصلاة المكتوبة."},
            {"text": "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.", "fadl": "من قالها دبر كل صلاة غفرت خطاياه."}
        ]
    },
    "random": {
        "title": "✨ ذكر مطلق وفضائل",
        "items": [
            {"text": "سبحان الله وبحمده، عدد خلقه، ورضا نفسه، وزنة عرشه، ومداد كلماته.", "fadl": "تعدل ساعات من الذكر المتواصل."},
            {"text": "لا حول ولا قوة إلا بالله.", "fadl": "كنز من كنوز الجنة."},
            {"text": "سبحان الله وبحمده، سبحان الله العظيم.", "fadl": "كلمتان خفيفتان على اللسان ثقيلتان في الميزان."}
        ]
    }
}

# ================= EMOJIS & SYMBOLS =================
DECOR = ["✨", "🌿", "💎", "🕌", "📖", "🤍"]

# ================= HISTORY LOCK (منع التكرار) =================
USER_HISTORY = {}

def is_seen(uid, text_hash):
    if uid not in USER_HISTORY:
        USER_HISTORY[uid] = []
    return text_hash in USER_HISTORY[uid]

def add_to_history(uid, text_hash):
    USER_HISTORY.setdefault(uid, []).append(text_hash)
    if len(USER_HISTORY[uid]) > 50: # الاحتفاظ بآخر 50 ذكر فقط لتوفير الذاكرة
        USER_HISTORY[uid].pop(0)

# ================= CORE FUNCTIONS =================
def apply_typography(text, fadl):
    # تنسيق الرسالة بشكل احترافي
    emoji = random.choice(DECOR)
    template = (
        f"{emoji} <b>الذكر:</b>\n"
        f"<code>{text}</code>\n\n"
        f"💡 <b>الفضل:</b>\n"
        f"<i>{fadl}</i>\n\n"
        f"#أذكار_المسلم #Hatshepsut"
    )
    return template

def generate_dhikr_content(uid, cat_key):
    category = AZKAR_DATA.get(cat_key)
    # محاولة جلب ذكر لم يظهر مؤخراً
    items = category["items"]
    random.shuffle(items)
    
    selected = items[0]
    for item in items:
        if not is_seen(uid, hash(item["text"])):
            selected = item
            break
            
    add_to_history(uid, hash(selected["text"]))
    return apply_typography(selected["text"], selected["fadl"])

# ================= KEYBOARDS =================
def main_menu_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(v["title"], callback_data=f"cat|{k}") for k, v in AZKAR_DATA.items()]
    kb.add(*buttons)
    return kb

def action_kb(cat_key):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔄 ذكر آخر", callback_data=f"again|{cat_key}"),
        InlineKeyboardButton("📋 نسخ", callback_data="copy_alert"),
        InlineKeyboardButton("🔙 العودة", callback_data="back_home")
    )
    return kb

# ================= HANDLERS =================
@bot.message_handler(commands=["start"])
def send_welcome(m):
    welcome_text = "<b>مرحباً بك في بوت أذكار المسلم المتطور 🕌</b>\n\nاختر أحد الأقسام التالية:"
    bot.send_message(m.chat.id, welcome_text, reply_markup=main_menu_kb())

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(c):
    uid = c.from_user.id
    data = c.data.split("|")

    if data[0] == "cat":
        cat_key = data[1]
        text = generate_dhikr_content(uid, cat_key)
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=action_kb(cat_key))

    elif data[0] == "again":
        cat_key = data[1]
        text = generate_dhikr_content(uid, cat_key)
        # تعديل الرسالة بذكر جديد
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=action_kb(cat_key))

    elif data[0] == "copy_alert":
        bot.answer_callback_query(c.id, "اضغط مطولاً على النص المنسق للنسخ 📋", show_alert=False)

    elif data[0] == "back_home":
        bot.edit_message_text("<b>اختر أحد الأقسام التالية:</b>", c.message.chat.id, c.message.message_id, reply_markup=main_menu_kb())

# ================= RUN =================
if __name__ == "__main__":
    print("🕌 Azkar Muslim Bot is running via Railway...")
    bot.infinity_polling(skip_pending=True)
