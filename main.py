import os
from sqlalchemy import select
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater
from db.models import Session, engine
from handlers import start_handler, create_event_handler


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ['BOT_TOKEN']

if __name__ == '__main__':
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(create_event_handler)

    updater.start_polling()
