import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from config import REFERRAL_REWARD, DAILY_BONUS, WITHDRAW_LIMIT
from utils import users

# लॉगिंग सेटअप
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    referred_by = context.args[0] if context.args else None

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "daily_claimed": False}
        if referred_by and int(referred_by) in users:
            users[int(referred_by)]["balance"] += REFERRAL_REWARD
            users[int(referred_by)]["referrals"] += 1
            await context.bot.send_message(
                chat_id=int(referred_by),
                text=f"🎉 You earned ₹{REFERRAL_REWARD} for referring a new user!"
            )

    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("📢 How to Earn?", callback_data="how_to_earn")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Welcome to the Referral Bot! 🎉\n\nRefer friends and earn ₹{REFERRAL_REWARD} per referral.\n\n"
        f"Your referral link: `https://t.me/{context.bot.username}?start={user_id}`\n\n"
        "Use the buttons below to navigate.", reply_markup=reply_markup, parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "daily_claimed": False}

    if query.data == "balance":
        await query.edit_message_text(f"💰 Your Balance: ₹{users[user_id]['balance']}\n👥 Referrals: {users[user_id]['referrals']}")

    elif query.data == "withdraw":
        if users[user_id]["balance"] >= WITHDRAW_LIMIT:
            await query.edit_message_text("✅ Withdrawal request sent! You will receive payment soon.")
            users[user_id]["balance"] -= WITHDRAW_LIMIT
        else:
            await query.edit_message_text("❌ You need at least ₹50 to withdraw.")

    elif query.data == "daily_bonus":
        if not users[user_id]["daily_claimed"]:
            users[user_id]["balance"] += DAILY_BONUS
            users[user_id]["daily_claimed"] = True
            await query.edit_message_text(f"🎁 Daily Bonus Claimed! ₹{DAILY_BONUS} added to your balance.")
        else:
            await query.edit_message_text("❌ You have already claimed your daily bonus today.")

    elif query.data == "how_to_earn":
        await query.edit_message_text(
            "📢 How to Earn:\n\n"
            f"1️⃣ Refer friends using your unique link.\n"
            f"2️⃣ You get ₹{REFERRAL_REWARD} per successful referral.\n"
            "3️⃣ Claim your daily bonus every 24 hours.\n"
            "4️⃣ Withdraw when your balance reaches ₹50."
			  
