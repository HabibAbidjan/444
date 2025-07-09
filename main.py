# === TO'LIQ ISHLAYDIGAN TELEGRAM GAME BOT KODI ===
# O'yinlar: Mines, Aviator, Dice
# Tugmalar: balans, hisob toldirish, pul chiqarish, bonus, referal

from keep_alive import keep_alive
from telebot import TeleBot, types
import random
import threading
import time
import os
import datetime

TOKEN = "8161107014:AAGBWEYVxie7-pB4-2FoGCPjCv_sl0yHogc"
bot = TeleBot(TOKEN)

ADMIN_ID = 5815294733  # Admin ID

user_balances = {}
lucky_users = set()
global_azart_level = 0  # Azart boshlanishda o‘chiq

user_mines_game = {}
user_aviator = {}
user_chicken_states = {}
tic_tac_toe_states = {}

# Qo‘shimcha sozlamalar va foydalanuvchi ma'lumotlar
addbal_state = {}
user_settings = {}
user_games = {}
user_data = {}
user_bonus_state = {}
user_positions = {}
withdraw_sessions = {}
user_states = {}
user_referred_by = {}

# Karta ma’lumotlari (faqat ko‘rsatish uchun)
uzcard = "5394 2822 2304 2232"
humo = "9860 1766 2141 5916"

# Multiplikatorlar (ko‘p o‘yinlarda ishlatiladi)
multipliers = [1.08, 1.17, 1.27, 1.56, 1.89, 2.31, 2.8, 3.6, 5.5, 6.5]

azart_enabled = True

@bot.message_handler(commands=['myid'])
def get_my_id(message):
    bot.send_message(message.chat.id, f"Sizning ID'ingiz: <code>{message.from_user.id}</code>", parse_mode="HTML")

cancel_commands = [
    "/start", "/help", "/addbal", "/cancel",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice", "💣 Play Mines",
    "🛩 Play Aviator", "🎮 Play TicTacToe", "🐔 Play Chicken",
    "🐸 Play Frog Jump",  # 🆕 Qo‘shildi
    "💸 Pul chiqarish", "🎁 Kunlik bonus", "👥 Referal link",
    "🔙 Orqaga"
]


user_referred_by = {}  # Foydalanuvchi qaysi referal orqali kelganini saqlash uchun

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if user_id not in user_balances:
        user_balances[user_id] = 3000  # boshlang‘ich balans

        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    # Agar foydalanuvchi hali referal orqali bonus olmagan bo‘lsa
                    if user_id not in user_referred_by:
                        user_referred_by[user_id] = ref_id
                        user_balances[ref_id] = user_balances.get(ref_id, 0) + 1000
                        bot.send_message(ref_id, f"🎉 Siz yangi foydalanuvchini taklif qilib, 1000 so‘m bonus oldingiz!")
            except ValueError:
                pass
    else:
        # Foydalanuvchi mavjud bo‘lsa, referal kodi bilan bonus bermaymiz
        pass

    back_to_main_menu(message)



# === Asosiy menyuga qaytish funksiyasi ===
def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '🎮 Play TicTacToe')
    markup.add('🐔 Play Chicken', '🐸 Play Frog Jump')
    markup.add('💰 Balance', '💳 Hisob toldirish')
    markup.add('💸 Pul chiqarish', '🎁 Kunlik bonus')
    markup.add('👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def show_balance(message):
    user_id = message.from_user.id
    bal = user_balances.get(user_id, 0)
    bot.send_message(message.chat.id, f"💰 Sizning balansingiz: {bal} so‘m")

cancel_commands = [
    "/start", "/help", "/addbal", "/cancel",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice", "💣 Play Mines",
    "🛩 Play Aviator", "🎮 Play TicTacToe", "🐔 Play Chicken",
    "🐸 Play Frog Jump",  # 🆕 Qo‘shildi
    "💸 Pul chiqarish", "🎁 Kunlik bonus", "👥 Referal link",
    "🔙 Orqaga"
]

@bot.message_handler(commands=['addbal'])
def addbal_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "🆔 Foydalanuvchi ID raqamini kiriting:")
    bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_id(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        target_id = int(message.text)
        addbal_state[message.from_user.id] = {'target_id': target_id}
        msg = bot.send_message(message.chat.id, "💵 Qo‘shiladigan miqdorni kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri ID. Iltimos, raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_amount(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError()
        admin_id = message.from_user.id
        target_id = addbal_state[admin_id]['target_id']

        user_balances[target_id] = user_balances.get(target_id, 0) + amount

        bot.send_message(admin_id, f"✅ {amount:,} so‘m foydalanuvchi {target_id} ga qo‘shildi.")

        try:
            bot.send_message(target_id, f"✅ Hisobingizga {amount:,} so‘m tushirildi!", parse_mode="HTML")
        except Exception:
            # Foydalanuvchiga xabar yuborishda xato bo‘lsa, e'tiborsiz qoldiramiz
            pass

        del addbal_state[admin_id]

    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor. Qaytadan raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)

@bot.message_handler(func=lambda message: message.text in cancel_commands)
def handle_cancel_command(message):
    user_id = message.from_user.id
    user_states.pop(user_id, None)
    user_chicken_states.pop(user_id, None)
    user_aviator.pop(user_id, None)
    user_mines_game.pop(user_id, None)
    tic_tac_toe_states.pop(user_id, None)
    back_to_main_menu(message)
        

# === Admin buyruq orqali Azartni yoqish/o‘chirish ===
@bot.message_handler(commands=['azart'])
def toggle_azart(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "⛔ Bu buyruq faqat admin uchun.")
    global global_azart_level
    if global_azart_level == 0:
        global_azart_level = 25
        bot.reply_to(message, "🔥 Azart yoqildi (25%).")
    else:
        global_azart_level = 0
        bot.reply_to(message, "❄️ Azart o‘chirildi.")

# === Keep Alive va polling bilan uzluksiz ish ===
keep_alive()

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"⚠️ Xatolik yuz berdi: {e}")
        time.sleep(5)


@bot.message_handler(func=lambda m: m.text == "👥 Referal link")
def referal_link(message):
    uid = message.from_user.id
    username = bot.get_me().username
    link = f"https://t.me/{username}?start={uid}"
    bot.send_message(message.chat.id, f"👥 Referal linkingiz:\n{link}")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💳 Hisob toldirish")
    bot.send_message(message.chat.id, "Xush kelibsiz! Tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💳 Hisob toldirish")
def ask_amount(message):
    bot.send_message(message.chat.id, "💰 Qancha so‘m to‘ldirmoqchisiz?")
    bot.register_next_step_handler(message, ask_card_type)

def ask_card_type(message):
    try:
        amount = int(message.text)
        user_data[message.chat.id] = {'amount': amount}
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Uzcard", callback_data="card_uzcard"),
            types.InlineKeyboardButton("Humo", callback_data="card_humo")
        )
        bot.send_message(message.chat.id, "💳 Karta turini tanlang:", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❗ Iltimos, raqam kiriting.")
        return ask_amount(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("card_"))
def send_card(call):
    user_id = call.from_user.id
    card_type = call.data.split("_")[1]
    user_data[user_id]['card_type'] = card_type

    card_number = uzcard if card_type == "uzcard" else humo
    amount = user_data[user_id]['amount']

    msg = (
        f"💳 To‘lov uchun karta:\n<b>{card_number}</b>\n\n"
        f"💰 Summa: {amount} so‘m\n\n"
        f"✅ To‘lovni amalga oshirgach, tugmani bosing."
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ To‘lov qildim", callback_data="paid"))
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                          text=msg, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "paid")
def user_paid(call):
    user_id = call.from_user.id
    data = user_data.get(user_id)
    if not data:
        bot.send_message(user_id, "Xatolik yuz berdi.")
        return

    amount = data['amount']
    card_type = data['card_type']
    username = call.from_user.username or "Yo‘q"

    msg = (
        f"📅 <b>Yangi to‘lov so‘rovi</b>\n"
        f"👤 Foydalanuvchi: @{username}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"💰 Summa: {amount} so‘m\n"
        f"💳 Karta: {card_type.upper()}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
    )
    bot.send_message(ADMIN_ID, msg, parse_mode="HTML", reply_markup=markup)
    bot.send_message(user_id, "🕐 So‘rovingiz yuborildi. Tekshiruv kutilmoqda...")


@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_action(call):
    user_id = int(call.data.split("_")[1])
    action = call.data.split("_")[0]
    data = user_data.get(user_id)

    if not data:
        bot.send_message(ADMIN_ID, "❗ Foydalanuvchi ma'lumoti topilmadi.")
        return

    amount = data['amount']

    if action == "approve":
        if user_id not in user_balances:
            user_balances[user_id] = 0
        user_balances[user_id] += amount

        bot.send_message(user_id, f"✅ To‘lov tasdiqlandi. Balansingiz {amount} so‘mga oshirildi.")
        bot.send_message(ADMIN_ID, f"💰 Hisob to‘ldirildi.\nFoydalanuvchi ID: <code>{user_id}</code>\nSumma: {amount} so‘m", parse_mode="HTML")
    else:
        bot.send_message(user_id, "❌ To‘lov rad etildi. Pul tushmagan bo‘lishi mumkin.")
        bot.send_message(ADMIN_ID, f"❌ To‘lov rad etildi. Foydalanuvchi ID: <code>{user_id}</code>", parse_mode="HTML")

    bot.answer_callback_query(call.id, "Yuborildi.")

@bot.message_handler(commands=['addbal'])
def add_balance(message):
    if message.from_user.id != admin_id:
        return

    try:
        _, user_id, amount = message.text.split()
        user_id = int(user_id)
        amount = int(amount)

        if user_id not in balances:
            balances[user_id] = 0
        balances[user_id] += amount

        bot.send_message(user_id, f"💰 Admin tomonidan balansingiz {amount} so‘mga to‘ldirildi.")
        bot.send_message(message.chat.id, f"✅ {user_id} ga {amount} so‘m qo‘shildi.")
    except:
        bot.send_message(message.chat.id, "❌ Xato format. To‘g‘ri foydalaning: /addbal user_id summa")


    bot.send_message(message.chat.id, text, parse_mode="HTML")
    # Botni sozlash, importlar, token va boshqalar

def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '🎮 Play TicTacToe')
    markup.add('🐔 Play Chicken', '🐸 Play Frog Jump')  # 🆕 Frog Jump tugmasi qo‘shildi
    markup.add('💰 Balance', '💳 Hisob toldirish')
    markup.add('💸 Pul chiqarish', '🎁 Kunlik bonus')
    markup.add('👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)


# Yoki boshqa joyda
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def go_back(message):
    back_to_main_menu(message)


@bot.message_handler(func=lambda m: m.text == "💸 Pul chiqarish")
def withdraw_step1(message):
    msg = bot.send_message(message.chat.id, "💵 Miqdorni kiriting (min 20000 so‘m):")
    bot.register_next_step_handler(msg, withdraw_step2)

def withdraw_step2(message):
    try:
        amount = int(message.text)
        user_id = message.from_user.id
        if amount < 20000:
            bot.send_message(message.chat.id, "❌ Minimal chiqarish miqdori 20000 so‘m.")
            return
        if user_balances.get(user_id, 0) < amount:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
        withdraw_sessions[user_id] = amount
        msg = bot.send_message(message.chat.id, "💳 Karta yoki to‘lov usulini yozing:")
        bot.register_next_step_handler(msg, withdraw_step3)
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor.")

# === SHU YERGA QO‘Y — withdraw_step3 ===
def withdraw_step3(message):
    user_id = message.from_user.id
    amount = withdraw_sessions.get(user_id)
    info = message.text.strip()

    # === Karta yoki to‘lov tizimi tekshiruvlari ===
    valid = False
    digits = ''.join(filter(str.isdigit, info))
    if len(digits) in [16, 19] and (digits.startswith('8600') or digits.startswith('9860') or digits.startswith('9989')):
        valid = True
    elif any(x in info.lower() for x in ['click', 'payme', 'uzcard', 'humo', 'apelsin']):
        valid = True

    if not valid:
        bot.send_message(message.chat.id, "❌ To‘lov usuli noto‘g‘ri kiritildi. Karta raqami (8600...) yoki servis nomini kiriting.")
        return

    user_balances[user_id] -= amount
    text = f"🔔 Yangi pul chiqarish so‘rovi!\n👤 @{message.from_user.username or 'no_username'}\n🆔 ID: {user_id}\n💵 Miqdor: {amount} so‘m\n💳 To‘lov: {info}"
    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "✅ So‘rov yuborildi, kuting.")
    del withdraw_sessions[user_id]

@bot.message_handler(commands=['lucky_list'])
def show_lucky_list(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not lucky_users:
        bot.send_message(message.chat.id, "📭 Lucky foydalanuvchilar yo‘q.")
    else:
        users = "\n".join([f"🆔 {uid}" for uid in lucky_users])
        bot.send_message(message.chat.id, f"🎯 Lucky foydalanuvchilar ro‘yxati:\n{users}")


# ========== TicTacToe boshlash ==========
@bot.message_handler(func=lambda m: m.text == "🎮 Play TicTacToe")
def start_tictactoe(message):
    user_id = message.from_user.id
    if user_id in user_games:
        return bot.send_message(message.chat.id, "⏳ Avvalgi o‘yinni tugating.")
    msg = bot.send_message(message.chat.id, "💸 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, lambda m: ask_tictactoe_symbol(m, user_id))

def ask_tictactoe_symbol(message, user_id):
    try:
        stake = int(message.text)
        if stake < 1000:
            return bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
        if user_balances.get(user_id, 0) < stake:
            return bot.send_message(message.chat.id, "❌ Balans yetarli emas.")
    except:
        return bot.send_message(message.chat.id, "❌ Raqam kiriting.")

    user_balances[user_id] -= stake
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("❌ Men boshlayman", "⭕ Bot boshlasın")
    bot.send_message(message.chat.id, "Kim boshlaydi?", reply_markup=markup)
    user_states[user_id] = {"stake": stake}

@bot.message_handler(func=lambda m: m.text in ["❌ Men boshlayman", "⭕ Bot boshlasın"])
def start_board(message):
    user_id = message.from_user.id
    stake = user_states[user_id]["stake"]
    board = ['⬜️'] * 9
    user_symbol, bot_symbol = ('❌', '⭕') if message.text == "❌ Men boshlayman" else ('⭕', '❌')

    user_games[user_id] = {
        'board': board,
        'user': user_symbol,
        'bot': bot_symbol,
        'stake': stake,
        'turn': 'user' if user_symbol == '❌' else 'bot',
        'msg_id': None
    }

    if user_symbol == '⭕':
        move = best_move(board, bot_symbol, user_symbol)
        board[move] = bot_symbol

    send_tictactoe_board(message.chat.id, user_id)

def send_tictactoe_board(chat_id, user_id):
    state = user_games[user_id]
    board = state['board']
    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            k = i + j
            if board[k] == '⬜️':
                row.append(types.InlineKeyboardButton('⬜️', callback_data=f"ttt_{k}"))
            else:
                row.append(types.InlineKeyboardButton(board[k], callback_data="none"))
        markup.add(*row)

    text = f"❌⭕ TicTacToe\n\n{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}"
    if state['msg_id']:
        bot.edit_message_text(text, chat_id, state['msg_id'], reply_markup=markup)
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        state['msg_id'] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("ttt_"))
def handle_ttt(call):
    user_id = call.from_user.id
    if user_id not in user_games:
        return
    state = user_games[user_id]
    board = state['board']
    pos = int(call.data.split("_")[1])
    if board[pos] != '⬜️':
        return bot.answer_callback_query(call.id, "❗ Bu katak band.")
    board[pos] = state['user']

    if check_winner(board, state['user']):
        win = int(state['stake'] * 1.5)
        user_balances[user_id] += win
        end_game(call, user_id, f"🎉 Siz yutdingiz!\n✅ Yutuq: {win} so‘m")
        return

    if '⬜️' not in board:
        win = int(state['stake'] * 0.5)
        user_balances[user_id] += win
        end_game(call, user_id, f"🤝 Durang.\n🔁 Qaytgan: {win} so‘m")
        return

    # Botning yurishi
    if state['stake'] >= 10000 or global_azart_level > 0:
        move = best_move(board, state['bot'], state['user'])  # Eng kuchli yurish
    else:
        move = random.choice([i for i, v in enumerate(board) if v == '⬜️'])
    board[move] = state['bot']

    if check_winner(board, state['bot']):
        end_game(call, user_id, f"😈 Bot yutdi! Pul yo‘qotildi.")
        return

    if '⬜️' not in board:
        win = int(state['stake'] * 0.5)
        user_balances[user_id] += win
        end_game(call, user_id, f"🤝 Durang.\n🔁 Qaytgan: {win} so‘m")
        return

    send_tictactoe_board(call.message.chat.id, user_id)

def end_game(call, user_id, result_text):
    board = user_games[user_id]['board']
    msg = f"{result_text}\n\n{board[0]}{board[1]}{board[2]}\n{board[3]}{board[4]}{board[5]}\n{board[6]}{board[7]}{board[8]}"
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
    del user_games[user_id]
    user_states.pop(user_id, None)

# ========== AI strategiya ==========
def best_move(board, bot_symbol, user_symbol):
    for i in range(9):
        if board[i] == '⬜️':
            board[i] = bot_symbol
            if check_winner(board, bot_symbol):
                board[i] = '⬜️'
                return i
            board[i] = '⬜️'
    for i in range(9):
        if board[i] == '⬜️':
            board[i] = user_symbol
            if check_winner(board, user_symbol):
                board[i] = '⬜️'
                return i
            board[i] = '⬜️'
    if board[4] == '⬜️':
        return 4
    for i in [0, 2, 6, 8]:
        if board[i] == '⬜️':
            return i
    for i in [1, 3, 5, 7]:
        if board[i] == '⬜️':
            return i
    return -1

def check_winner(board, symbol):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for line in wins:
        if all(board[i] == symbol for i in line):
            return True
    return False


    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=board_to_markup(board))
    bot.answer_callback_query(call.id, "Yurishingiz qabul qilindi!")


# 🐸 FROG JUMP o'yini
@bot.message_handler(func=lambda m: m.text == "🐸 Play Frog Jump")
def frog_start(message):
    user_id = message.from_user.id
    msg = bot.send_message(message.chat.id, "💸 Stavka miqdorini kiriting (min 1000):")
    bot.register_next_step_handler(msg, lambda m: frog_process_stake(m, user_id))


def frog_process_stake(message, user_id):
    chat_id = message.chat.id
    try:
        stake = int(message.text)
        if stake < 1000:
            return bot.send_message(chat_id, "❌ Minimal stavka 1000 so‘m.")
        if user_balances.get(user_id, 0) < stake:
            return bot.send_message(chat_id, "❌ Mablag‘ yetarli emas.")
    except:
        return bot.send_message(chat_id, "❌ Raqam kiriting.")

    user_balances[user_id] -= stake
    user_chicken_states[user_id] = {
        'pos': 0,
        'stake': stake,
        'multiplier': 1.0,
        'alive': True
    }

    send_frog_grid(chat_id, user_id)


def send_frog_grid(chat_id, user_id):
    state = user_chicken_states[user_id]
    pos = state['pos']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➡️ Oldinga sakrash", callback_data="frog_jump"))
    markup.add(types.InlineKeyboardButton("💸 Pulni yechib olish", callback_data="frog_cashout"))

    line = render_frog_line(pos)
    pot_win = int(state['stake'] * state['multiplier'])

    bot.send_message(chat_id,
        f"🐸 Frog Jump o‘yini\n\n{line}\n\n"
        f"📈 Koef: x{round(state['multiplier'], 2)}\n"
        f"💰 Potensial yutuq: {pot_win:,} so‘m",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in ["frog_jump", "frog_cashout"])
def frog_handle(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    state = user_chicken_states.get(user_id)
    if not state:
        return bot.answer_callback_query(call.id, "⛔ O‘yin topilmadi.")

    pos = state['pos']

    # 💸 Pulni chiqarish (cashout)
    if call.data == "frog_cashout":
        win = int(state['stake'] * state['multiplier'])
        user_balances[user_id] += win
        user_chicken_states.pop(user_id)
        try:
            bot.send_audio(chat_id, open('sounds/cashout.mp3', 'rb'))  # 💵 Pul chiqarish ovozi
        except:
            pass
        return bot.edit_message_text(
            f"✅ Pul chiqarildi! Yutuq: {win:,} so‘m",
            chat_id, call.message.message_id
        )

    # 💥 Baqa portlashi
    risk = 0.3 + (pos * 0.1)
    if global_azart_level > 0:
        risk += global_azart_level / 100
    if user_id in lucky_users:
        risk *= 0.3
    risk = min(risk, 0.95)

    if random.random() < risk:
        line = render_frog_line(pos, dead=True)
        user_chicken_states.pop(user_id)
        try:
            bot.send_audio(chat_id, open('sounds/bomb.mp3', 'rb'))  # 💥 Portlash ovozi
        except:
            pass
        return bot.edit_message_text(
            f"💥 Baqa portladi! Siz yutqazdingiz.\n\n{line}",
            chat_id, call.message.message_id
        )

    # ✅ Baqa xavfsiz sakradi
    state['pos'] += 1
    state['multiplier'] = multipliers[state['pos']]
    if state['pos'] == 9:
        win = int(state['stake'] * state['multiplier'])
        user_balances[user_id] += win
        line = render_frog_line(state['pos'])
        user_chicken_states.pop(user_id)
        try:
            bot.send_audio(chat_id, open('sounds/win.mp3', 'rb'))  # 🎉 G‘alaba musiqasi
        except:
            pass
        return bot.edit_message_text(
            f"🎉 Baqa manzilga yetdi! Yutuq: {win:,} so‘m\n\n{line}",
            chat_id, call.message.message_id
        )

    # 🔊 Sakrash ovozi (harakat davomida)
    try:
        bot.send_audio(chat_id, open('sounds/jump.mp3', 'rb'))  # 🐸 Sakrash
    except:
        pass
    send_frog_grid(chat_id, user_id)

    
@bot.message_handler(func=lambda m: m.text == "🎁 Kunlik bonus")
def daily_bonus(message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_bonus_state.get(user_id) == today:
        bot.send_message(message.chat.id, "🎁 Siz bugun bonus oldingiz.")
        return
    bonus = random.randint(1000, 5000)
    user_balances[user_id] = user_balances.get(user_id, 0) + bonus
    user_bonus_state[user_id] = today
    bot.send_message(message.chat.id, f"🎉 Sizga {bonus} so‘m bonus berildi!")

# Ovoz fayllarining yo‘llari
WIN_SOUND = '/mnt/data/win.ogg'
LOSE_SOUND = '/mnt/data/lose.ogg'

@bot.message_handler(func=lambda m: m.text == "🎲 Play Dice")
def dice_start(message):
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, dice_process)

def dice_process(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)

    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if stake < 1000:
            bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return

        user_balances[user_id] -= stake
        bot.send_message(message.chat.id, "🎲 O‘yin boshlanmoqda...")

        sent_dice = bot.send_dice(message.chat.id)
        time.sleep(4)

        dice_value = sent_dice.dice.value
        azart_factor = global_azart_level if global_azart_level >= 25 else 0
        dice_chance = dice_value - (azart_factor // 10)
        if dice_chance < 1:
            dice_chance = 1

        if dice_chance <= 2:
            win = 0
        elif dice_chance <= 4:
            win = stake
        else:
            win = stake * 2

        user_balances[user_id] += win

        # Ovoz yuborish
        if win > 0:
            with open(WIN_SOUND, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
        else:
            with open(LOSE_SOUND, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)

        bot.send_message(
            message.chat.id,
            f"🎲 Natija: {dice_value}\n"
            f"{'✅ Yutdingiz!' if win > 0 else '❌ Yutqazdingiz.'}\n"
            f"💵 Yutuq: {win} so‘m"
        )

    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri stavka kiriting.")

@bot.message_handler(commands=['remove_lucky'])
def remove_lucky(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")

    parts = message.text.strip().split()
    if len(parts) < 2:
        return bot.send_message(message.chat.id, "❗ Foydalanuvchi ID raqamini yozing. Masalan: /remove_lucky 12345678")

    try:
        user_id = int(parts[1])
        if user_id in lucky_users:
            lucky_users.remove(user_id)
            bot.send_message(message.chat.id, f"🗑 Foydalanuvchi {user_id} lucky ro‘yxatidan o‘chirildi.")
        else:
            bot.send_message(message.chat.id, f"⚠️ {user_id} lucky ro‘yxatida yo‘q.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ ID raqami noto‘g‘ri.")

@bot.message_handler(commands=['lucky_list'])
def lucky_list(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "⛔ Sizda ruxsat yo‘q.")

    if not lucky_users:
        return bot.send_message(message.chat.id, "📭 Lucky ro‘yxati bo‘sh.")

    text = "📋 Lucky foydalanuvchilar ro‘yxati:\n"
    for uid in lucky_users:
        text += f"🆔 {uid}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "💣 Play Mines")
def ask_stake(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.send_message(chat_id, "💵 Iltimos, stavka miqdorini kiriting (minimum 1000 so‘m):")
    user_states[user_id] = "awaiting_stake"

@bot.message_handler(func=lambda m: m.from_user.id in user_states and user_states[m.from_user.id] == "awaiting_stake")
def handle_stake(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        stake = int(message.text)
        if stake < 1000:
            return bot.send_message(chat_id, "❌ Minimal stavka 1000 so‘m.")
        if user_balances.get(user_id, 0) < stake:
            return bot.send_message(chat_id, "❌ Hisobingizda mablag‘ yetarli emas.")

        user_balances[user_id] -= stake
        cells = list(range(25))
        bombs = random.sample(cells, 4)  # 🔥 4 dona bomba
        user_mines_game[user_id] = {
            'bombs': bombs,
            'opened': [],
            'stake': stake
        }
        user_states.pop(user_id, None)

        # 🔊 O‘yin boshlanish ovozi
        try:
            with open('start.mp3', 'rb') as audio:
                bot.send_audio(chat_id, audio)
        except:
            pass

        bot.send_message(chat_id, f"🎮 O‘yin boshlandi! Stavka: {stake} so‘m\n📦 Maydon: 5x5 | 💣 Bombalar: 4 ta")
        send_mines_grid(user_id)

    except:
        bot.send_message(chat_id, "❗ Iltimos, faqat raqam kiriting.")

def send_mines_grid(user_id):
    game = user_mines_game[user_id]
    chat_id = user_id
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []

    for i in range(25):
        if i in game['opened']:
            btn = types.InlineKeyboardButton("💵", callback_data="ignore")
        else:
            btn = types.InlineKeyboardButton("⬜️", callback_data=f"mine_{i}")
        buttons.append(btn)

    for i in range(0, 25, 5):
        markup.row(*buttons[i:i+5])

    markup.add(types.InlineKeyboardButton("💸 Pulni olish", callback_data="cashout"))
    bot.send_message(chat_id, "⬇️ Katakni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mine_") or call.data == "cashout")
def handle_mines_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id not in user_mines_game:
        return bot.answer_callback_query(call.id, "❌ Sizda faol o‘yin yo‘q.")

    game = user_mines_game[user_id]

    if call.data == "cashout":
        count = len(game['opened'])
        if count == 0:
            return bot.answer_callback_query(call.id, "⛔ Avval kamida bitta katakni oching.")
        multiplier = multipliers[min(count - 1, len(multipliers) - 1)]
        win = round(game['stake'] * multiplier)
        user_balances[user_id] += win

        # 🎵 Yutgan ovoz
        try:
            with open('win.mp3', 'rb') as audio:
                bot.send_audio(chat_id, audio)
        except:
            pass

        del user_mines_game[user_id]
        return bot.edit_message_text(f"✅ Pul chiqarildi!\n📈 Koef: x{multiplier}\n💰 Yutuq: {win} so‘m", chat_id, call.message.message_id)

    index = int(call.data.split("_")[1])
    if index in game['opened']:
        return bot.answer_callback_query(call.id, "❗ Bu katak allaqachon ochilgan.")

    if index in game['bombs']:
        # 💥 Portlash
        try:
            with open('boom.mp3', 'rb') as audio:
                bot.send_audio(chat_id, audio)
        except:
            pass

        del user_mines_game[user_id]
        return bot.edit_message_text("💥 Boom! Bombaga tushdingiz! ❌ Siz yutqazdingiz.", chat_id, call.message.message_id)

    # ✅ Xavfsiz ochilgan katak — "kassa" ovozi
    try:
        with open('kash.mp3', 'rb') as audio:
            bot.send_audio(chat_id, audio)
    except:
        pass

    game['opened'].append(index)
    send_mines_grid(user_id)



# === AVIATOR o'yini funksiyasi ===
@bot.message_handler(func=lambda m: m.text == "🛩 Play Aviator")
def play_aviator(message):
    user_id = message.from_user.id
    if user_id in user_aviator:
        bot.send_message(message.chat.id, "⏳ Avvalgi Aviator o‘yini tugamagani uchun kuting.")
        return
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, process_aviator_stake)

def process_aviator_stake(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)
    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if stake < 1000:
            bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Yetarli balans yo‘q.")
            return
        user_balances[user_id] -= stake
        user_aviator[user_id] = {
            'stake': stake,
            'multiplier': 1.0,
            'chat_id': message.chat.id,
            'message_id': None,
            'stopped': False
        }
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        msg = bot.send_message(message.chat.id, f"🛫 Boshlanmoqda... x1.00", reply_markup=markup)
        user_aviator[user_id]['message_id'] = msg.message_id
        threading.Thread(target=run_aviator_game, args=(user_id,)).start()
    except:
        bot.send_message(message.chat.id, "❌ Xatolik. Raqam kiriting.")

def run_aviator_game(user_id):
    data = user_aviator.get(user_id)
    if not data:
        return
    chat_id = data['chat_id']
    message_id = data['message_id']
    stake = data['stake']
    multiplier = data['multiplier']

    # 🔊 O'yin boshlanganda — Takeoff ovozi
    try:
        with open('takeoff.mp3', 'rb') as audio:
            bot.send_audio(chat_id, audio)
    except:
        pass

    for step in range(40):
        if user_aviator.get(user_id, {}).get('stopped'):
            win = int(stake * multiplier)
            user_balances[user_id] += win
            try:
                with open('cashout.mp3', 'rb') as audio:
                    bot.send_audio(chat_id, audio)
            except:
                pass
            bot.edit_message_text(f"🚫 To‘xtatildi: x{multiplier}\n✅ Yutuq: {win} so‘m", chat_id, message_id)
            del user_aviator[user_id]
            return

        time.sleep(1)
        increment = round(random.uniform(0.1, 0.35), 2)
        multiplier = round(multiplier + increment, 2)

        # 🎯 Crash ehtimollari
        if multiplier <= 1.1:
            crash_chance = 0.12
        elif multiplier <= 1.3:
            crash_chance = 0.18
        elif multiplier <= 1.5:
            crash_chance = 0.3
        elif multiplier <= 2.0:
            crash_chance = 0.45
        elif multiplier <= 3.0:
            crash_chance = 0.65
        elif multiplier <= 5.0:
            crash_chance = 0.8
        elif multiplier <= 7.0:
            crash_chance = 0.9
        else:
            crash_chance = 0.98

        # 🔥 Global azart
        if stake >= 10000:
            crash_chance += 0.20
        if user_id in lucky_users:
            crash_chance *= 0.3
        if global_azart_level > 0:
            crash_chance += global_azart_level / 100
        crash_chance = min(crash_chance, 0.98)

        if random.random() < crash_chance:
            try:
                with open('crash.mp3', 'rb') as audio:
                    bot.send_audio(chat_id, audio)
            except:
                pass
            bot.edit_message_text(f"💥 Portladi: x{multiplier}\n❌ Siz yutqazdingiz.", chat_id, message_id)
            del user_aviator[user_id]
            return

        # ↗ Yangilash
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        try:
            bot.edit_message_text(f"🛫 Ko‘tarilmoqda... x{multiplier}", chat_id, message_id, reply_markup=markup)
        except:
            pass

        user_aviator[user_id]['multiplier'] = multiplier


CHICKEN = "🐔"
PASSED = "✅"
UNLOCKED = "🔓"
LOCKED = "🔒"
BOMB = "💥"

azart_enabled = True  # Global azart sozlamasi

@bot.message_handler(func=lambda m: m.text == "🐔 Play Chicken")
def start_chicken(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    msg = bot.send_message(chat_id, "💸 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, lambda m: process_chicken_stake(m, user_id))

def process_chicken_stake(message, user_id):
    chat_id = message.chat.id
    try:
        stake = int(message.text)
        if stake < 1000:
            return bot.send_message(chat_id, "❌ Minimal stavka 1000 so‘m.")
        if user_balances.get(user_id, 0) < stake:
            return bot.send_message(chat_id, "❌ Mablag‘ yetarli emas.")
    except:
        return bot.send_message(chat_id, "❌ Raqam kiriting.")

    user_balances[user_id] -= stake
    user_chicken_states[user_id] = {
        'pos': 0,
        'stake': stake,
        'multiplier': 1.0,
        'alive': True
    }

    # 🔔 O‘yin boshlanish signali
    try:
        with open('start.mp3', 'rb') as audio:
            bot.send_audio(chat_id, audio)
    except:
        pass

    send_chicken_grid(chat_id, user_id)

def send_chicken_grid(chat_id, user_id):
    state = user_chicken_states[user_id]
    pos = state['pos']
    cells = []
    markup = types.InlineKeyboardMarkup(row_width=5)

    for i in range(10):
        if i < pos:
            cells.append(PASSED)
            markup.add(types.InlineKeyboardButton(PASSED, callback_data="ignore"))
        elif i == pos:
            cells.append(CHICKEN)
            markup.add(types.InlineKeyboardButton(CHICKEN, callback_data="ignore"))
        elif i == pos + 1:
            cells.append(UNLOCKED)
            markup.add(types.InlineKeyboardButton(UNLOCKED, callback_data=f"chicken_jump_{i}"))
        else:
            cells.append(LOCKED)
            markup.add(types.InlineKeyboardButton(LOCKED, callback_data="ignore"))

    pot_win = int(state['stake'] * state['multiplier'])

    markup.add(types.InlineKeyboardButton("💸 Pulni yechib olish", callback_data="chicken_cashout"))

    line = " > ".join(cells)
    bot.send_message(chat_id,
        f"🐔 Chicken Road o‘yini\n\n"
        f"{line}\n\n"
        f"📈 Koef: x{round(state['multiplier'], 2)}\n"
        f"💰 Potensial yutuq: {pot_win:,} so‘m\n\n"
        f"🐔 Keyingi katakka sakrash uchun 🔓 tugmasini bosing yoki pulni yeching.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("chicken_"))
def handle_chicken(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    state = user_chicken_states.get(user_id)

    if not state or not state['alive']:
        return bot.answer_callback_query(call.id, "⛔ O‘yin mavjud emas.")

    if call.data == "chicken_cashout":
        win = int(state['stake'] * state['multiplier'])
        user_balances[user_id] += win
        user_chicken_states.pop(user_id)

        # 🏆 G‘alaba ovozi
        try:
            with open('win.mp3', 'rb') as audio:
                bot.send_audio(chat_id, audio)
        except:
            pass

        return bot.edit_message_text(f"✅ Pul chiqarildi! Yutuq: {win:,} so‘m", chat_id, call.message.message_id)

    if call.data.startswith("chicken_jump_"):
        target = int(call.data.split("_")[-1])
        pos = state['pos']
        if target != pos + 1:
            return bot.answer_callback_query(call.id, "⛔ Faqat yonidagi katakka sakrashingiz mumkin.")

        # 🎲 Azart va xavf
        if azart_enabled:
            risk = 0.6 + (pos * 0.08)
        else:
            risk = 0.9 + (pos * 0.3)
        if global_azart_level > 0:
            risk += global_azart_level / 100
        risk = min(risk, 0.98)

        if random.random() < risk:
            # 💥 Portlashdan oldin ovoz
            try:
                with open('boom.mp3', 'rb') as audio:
                    bot.send_audio(chat_id, audio)
            except:
                pass

            line = []
            for i in range(10):
                if i == target:
                    line.append(BOMB)
                elif i < pos:
                    line.append(PASSED)
                elif i == pos:
                    line.append(CHICKEN)
                else:
                    line.append(LOCKED)
            user_chicken_states.pop(user_id)
            return bot.edit_message_text(
                f"💥 Boom! Bombaga tushdi!\nStavka yo‘qotildi.\n\n{' > '.join(line)}",
                chat_id, call.message.message_id
            )

        # ✅ Xavfsiz sakrash
        state['pos'] += 1
        state['multiplier'] = multipliers[state['pos']]
        if state['pos'] == 9:
            win = int(state['stake'] * state['multiplier'])
            user_balances[user_id] += win
            line = get_final_chicken_line(state['pos'])
            user_chicken_states.pop(user_id)

            # 🏆 Yutuq ovozi
            try:
                with open('win.mp3', 'rb') as audio:
                    bot.send_audio(chat_id, audio)
            except:
                pass

            return bot.edit_message_text(
                f"🎉 Tovuq manzilga yetdi! Yutuq: {win:,} so‘m\n\n{line}",
                chat_id, call.message.message_id
            )
        send_chicken_grid(chat_id, user_id)

def get_final_chicken_line(pos):
    cells = []
    for i in range(10):
        if i < pos:
            cells.append(PASSED)
        elif i == pos:
            cells.append(CHICKEN)
        else:
            cells.append(LOCKED)
    return " > ".join(cells)


print("Bot ishga tushdi...")
keep_alive()
bot.polling(none_stop=True)
