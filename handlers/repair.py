from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from db.models import Session, engine


local_session = Session(bind=engine)

def repair(update: Update, context: CallbackContext):
    print(update)

repair_handler = CommandHandler('repair', repair)
