import datetime

from telegram import Update
from telegram.ext import CallbackContext, ChatMemberHandler

from sqlalchemy import select
from db.models import Group, Calendar, Event, Session, engine

local_session = Session(bind=engine)

def initiate_group(update: Update, context: CallbackContext):
    """
    handle that bot has been invited to the telegram group
    """
    chat_id = update.effective_chat.id # update.my_chat_member.chat.id
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