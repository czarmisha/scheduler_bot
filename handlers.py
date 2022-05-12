import datetime
from tokenize import group
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ChatMemberHandler
from sqlalchemy import select
from db.models import Group, Calendar, Event, Session, engine

local_session = Session(bind=engine)

def start(update: Update, context: CallbackContext):
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked':
        context.bot.send_message(chat_id=update.effective_chat.id, text="У Вас нет права общаться со мной")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Инфо о боте")

start_handler = CommandHandler('start', start)

def create_event(update: Update, context: CallbackContext):
    """
    create events (/create_event 28.05.2022 15:00 16:00)
    receive date, start_time and end_time from context.args list
    """
    if not context.args or len(context.args) < 3:
        context.bot.send_message(chat_id=update.effective_chat.id, text="неверный формат создания события")
    else:    
        chat_id = update.message.chat.id
        datetime_start_str = f'{context.args[0]} {context.args[1]}'
        datetime_end_str = f'{context.args[0]} {context.args[2]}'
        # description = context.args[3] if context.args[3] else ''
        #TODO: need validate date and time
        #TODO: need validate permissions
        datetime_start = datetime.datetime.strptime(datetime_start_str, '%d.%m.%y %H:%M')
        datetime_end = datetime.datetime.strptime(datetime_end_str, '%d.%m.%y %H:%M')
        statement = select(Group).filter_by(tg_id=chat_id)
        group = local_session.execute(statement).scalars().first()
        statement = select(Calendar).filter_by(group_id=group.id)
        calendar = local_session.execute(statement).scalars().first()
        if calendar:
            Event(start=datetime_start, end=datetime_end, description='description', is_repeated=False, calendar_id=calendar.id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Событие создано')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Событие не создано')

create_event_handler = CommandHandler('create_event', create_event)

def initiate_group(update: Update, context: CallbackContext):
    """
    handle that bot has been invited to the telegram group
    """

    print(update)
    chat_id = update.my_chat_member.chat.id
    statement = select(Group)
    result = local_session.execute(statement).all()
    if not result:
        group = Group(tg_id=chat_id, name=context.bot.get_chat(chat_id).title)
        local_session.add(group)
        local_session.commit()
        calendar = Calendar(name=context.bot.get_chat(chat_id).title, group_id=group.id)
        local_session.add(calendar)
        local_session.commit()
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'create Group and Calendar in db for this chat \n\n some params: tg_id {chat_id},name {context.bot.get_chat(chat_id).title}, member count {context.bot.get_chat_member_count(chat_id)}')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="table in db already exist") # remove
    #TODO need exeption when bot is kicked from group

initiate_handler = ChatMemberHandler(initiate_group)