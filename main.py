import os
from dotenv import load_dotenv

from telegram.ext import Updater

from handlers import start, reserve, initiate, display, my_events, feedback, help, car_detect

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
    dispatcher.add_handler(display.display_handler)
    dispatcher.add_handler(display.option_handler)
    dispatcher.add_handler(my_events.my_events_handler)
    dispatcher.add_handler(my_events.event_handler)
    dispatcher.add_handler(my_events.del_handler)
    dispatcher.add_handler(my_events.edit_handler)
    dispatcher.add_handler(feedback.feedback_handler)
    dispatcher.add_handler(help.help_handler)
    dispatcher.add_handler(car_detect.detect_handler)

    # dispatcher.add_error_handler(error.UnauthorizedError)

    updater.start_polling()

    # set webhook for heroku
    # PORT = int(os.environ.get('PORT', '8443'))
    # print(PORT)
    # updater.start_webhook(listen="localhost",
    #                       port=int(PORT),
    #                     #   port=80,
    #                       url_path=token,
    #                       webhook_url = 'https://glacial-depths-89217.herokuapp.com/' + token)
    # updater.bot.setWebhook('https://glacial-depths-89217.herokuapp.com/' + token)
# TODO maybe create admin panel????
