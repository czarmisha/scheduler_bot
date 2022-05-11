from calendar import calendar
from email import charset
import os
from sqlalchemy import select
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from db.models import Session, engine, Group, Calendar


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ['BOT_TOKEN']
updater = Updater(token=token)
dispatcher = updater.dispatcher

local_session = Session(bind=engine)


def start(update: Update, context: CallbackContext):
    """
    create and populate table GROUP
    """
    chat_id = update.message.chat.id

    author = context.bot.get_chat_member(chat_id, update.effective_user.id) # message's author
    if not update.message.chat.type == 'group':
        context.bot.send_message(chat_id=update.effective_chat.id, text="У Вас нет права общаться со мной")
        return
    
    # if author.status == 'administrator' or author.status == 'creator': # https://core.telegram.org/bots/api#chatmember

    print('----------------', context.args)
    print('----------------', )
    print('----------------', update)
    statement = select(Group).filter_by(tg_id=chat_id)
    result = local_session.execute(statement).all()
    if not result:
        group = Group(tg_id=chat_id, name=context.bot.get_chat(
            chat_id).title, member_count=context.bot.get_chat_member_count(chat_id))
        local_session.add(group)
        local_session.commit()
        calendar = Calendar(name=context.bot.get_chat(chat_id).title, group_id=group.id)
        local_session.add(calendar)
        local_session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'create Group and Calendar in db for this chat \n\n some params: tg_id {chat_id},name {context.bot.get_chat(chat_id).title}, member count {context.bot.get_chat_member_count(chat_id)}')
    else:
        #we can also update rows in table
        context.bot.send_message(chat_id=update.effective_chat.id, text="table in db already exist")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def create_event(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="создаем событие")

create_event_handler = CommandHandler('create_event', create_event)
dispatcher.add_handler(create_event_handler)

updater.start_polling()
