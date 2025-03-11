import logging

from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID
from telegram_bot import subscription_manager

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)


def send_message(text: str, chat_id: str = TELEGRAM_GROUP_ID):
    try:
        bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")


def subscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("Usage: /subscribe <keyword>")
        return
    keyword = " ".join(context.args)
    subscription_manager.add_subscription(chat_id, keyword)
    update.message.reply_text(f"✅ Subscribed to keyword '{keyword}'.")


def unsubscribe(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not context.args:
        update.message.reply_text("Usage: /unsubscribe <keyword>")
        return
    keyword = " ".join(context.args)
    subscription_manager.remove_subscription(chat_id, keyword)
    update.message.reply_text(f"✅ Unsubscribed from keyword '{keyword}'.")


def list_subscriptions(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    subs = subscription_manager.list_subscriptions(chat_id)
    if subs:
        update.message.reply_text("🔖 Your subscriptions:\n" + "\n".join(f"- {s}" for s in subs))
    else:
        update.message.reply_text("You have no subscriptions.")


def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("Unknown command.")


def start_telegram_bot():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("subscribe", subscribe))
    dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe))
    dispatcher.add_handler(CommandHandler("subscriptions", list_subscriptions))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

    updater.start_polling()
    updater.idle()
