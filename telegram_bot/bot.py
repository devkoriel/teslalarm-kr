from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_URL
from telegram_bot.command_handler import change_language, handle_text
from utils.logger import setup_logger

logger = setup_logger()


def create_application():
    """
    Create and configure the Telegram bot application.

    Sets up command and message handlers for the bot.

    Returns:
        Configured Telegram bot application
    """
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app


def run_webhook(app):
    """
    Run the Telegram bot in webhook mode.

    Configures the webhook URL on Telegram servers and starts
    the webhook server to receive updates.

    Args:
        app: Telegram bot application instance
    """
    # Set webhook URL on Telegram servers
    app.bot.set_webhook(WEBHOOK_URL)
    # Run server in webhook mode
    app.run_webhook(
        listen=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        url_path=TELEGRAM_BOT_TOKEN,  # Use bot token in URL path
        webhook_url=WEBHOOK_URL,
    )
