import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# الحصول على التوكن من متغيرات البيئة (للأمان)
TOKEN = os.getenv("BOT_TOKEN")

# نموذج بسيط للأذكار (يمكنك توسيعه أو وضعه في ملف JSON منفصل)
AZKAR = {
    "أذكار الصباح": ["أصبحنا وأصبح الملك لله والحمد لله..", "آية الكرسي.."],
    "أذكار المساء": ["أمسين وأمسى الملك لله والحمد لله..", "قل هو الله أحد.."],
    "أذكار النوم": ["باسمك ربي وضعت جنبي.."]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["أذكار الصباح", "أذكار المساء"], ["أذكار النوم"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("مرحباً بك في بوت أذكار المسلم. اختر النوع:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in AZKAR:
        response = "\n\n".join(AZKAR[text])
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("من فضلك اختر من القائمة.")

def main():
    # بناء التطبيق
    application = Application.builder().token(TOKEN).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # معالجة الرسائل النصية (القائمة)
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء تشغيل البوت
    print("البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()