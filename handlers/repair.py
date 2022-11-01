from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from db.models import Session, engine


local_session = Session(bind=engine)

def repair(update: Update, context: CallbackContext):
    print(update)
    print(update.message.migrate_from_chat_id)

repair_handler = CommandHandler('repair', repair)
