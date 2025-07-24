from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import os

# Simulate a user database (can be replaced by MongoDB or SQLite later)
users = {}

# Replace with your Telegram user ID
OWNER_ID = 123456789  # ← Replace with your real Telegram ID

# START Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.setdefault(user_id, {
        'start_time': datetime.now(),
        'balance': 100,
        'usdt_address': None
    })
    keyboard = [
        [InlineKeyboardButton("📈 Progress", callback_data='progress')],
        [InlineKeyboardButton("💰 Balance", callback_data='balance')],
        [InlineKeyboardButton("📤 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("ℹ️ Info", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to Motrox Bot!", reply_markup=reply_markup)

# BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'progress':
        await query.edit_message_text("📊 Your investment progress is updating every 2 hours (0.8%).")
    elif query.data == 'balance':
        if users[user_id].get('start_time'):
            hours = (datetime.now() - users[user_id]['start_time']).total_seconds() / 7200
            profit = users[user_id]['balance'] * (1 + 0.008) ** hours
            await query.edit_message_text(f"💰 Your current balance is *{profit:.2f}* USDT.", parse_mode='Markdown')
        else:
            await query.edit_message_text("⚠️ Your balance is *0 USDT*.", parse_mode='Markdown')
    elif query.data == 'withdraw':
        await query.edit_message_text("📥 Please send me your *USDT TRC20 wallet address* to withdraw your profits.", parse_mode='Markdown')
        context.user_data['awaiting_withdraw_address'] = True
    elif query.data == 'info':
        await query.edit_message_text(
            "🔍 *What We Do?*\n\n"
            "Motrox is a smart investment platform.\n"
            "We generate 10–15% profit daily.\n"
            "Deposit USDT (TRC20), and we update profit every 2 hours (0.8%).",
            parse_mode='Markdown'
        )

# TEXT HANDLER (for USDT address)
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get('awaiting_withdraw_address'):
        context.user_data['awaiting_withdraw_address'] = False
        users[user_id]['usdt_address'] = text
        await update.message.reply_text("✅ Withdrawal request sent to admin.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"📬 Withdraw request:\n\nUser: {user_id}\nWallet: {text}")
    else:
        await update.message.reply_text("❓ Use the menu buttons to interact.")

# MAIN FUNCTION
if __name__ == '__main__':
    import asyncio

    async def main():
        app = ApplicationBuilder().token(os.environ['7509938357:AAEXVLbk0cdud8qgX8R-O50dYFepNrVz6oU']).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

        print("✅ Bot running...")
        await app.run_polling()

    asyncio.run(main())
