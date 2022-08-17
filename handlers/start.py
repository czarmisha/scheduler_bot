from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from sqlalchemy import select
from db.models import Group, Session, engine
from utils.translation import messages

local_session = Session(bind=engine)

def start(update: Update, context: CallbackContext):
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
    else:
        reply_keyboard = [['/reserve', '/display'], ['/my_events', '/feedback']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        update.message.reply_text(f"{messages['start_text']['ru']} \n\n {messages['start_text']['uz']}",
                                  reply_markup=markup_key)
        update.message.reply_text(f"{messages['attention']['ru']} \n\n {messages['attention']['uz']}")


start_handler = CommandHandler('start', start)
