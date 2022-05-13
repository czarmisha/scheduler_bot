import os
from dotenv import load_dotenv

from telegram.ext import Updater

from handlers import start, reserve, initiate


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ['BOT_TOKEN']

if __name__ == '__main__':
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(start.start_handler)
    dispatcher.add_handler(reserve.reserve_handler)
    dispatcher.add_handler(initiate.initiate_handler)

    updater.start_polling()
