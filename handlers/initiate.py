import logging
from os import stat

from telegram import Update
from telegram.ext import CallbackContext, ChatMemberHandler

from sqlalchemy import select
from db.models import Group, Calendar, Event, Session, engine
from utils.clean_db import clean

local_session = Session(bind=engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def initiate_group(update: Update, context: CallbackContext):
    """
    handle that bot has been invited to the telegram group
    """
    logger.info(f'Initiate bot for this group:{update.effective_chat.title}')

    if update.my_chat_member.new_chat_member.status == 'left' and update.my_chat_member.new_chat_member.user.id == context.bot.id:
        logger.info('Bot was removed from the group')
        # clean(update.my_chat_member.chat.id)
        return 

    chat_id = update.effective_chat.id
    # statement = select(Group).filter_by(tg_id=chat_id)
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    if not group:
        group = Group(tg_id=chat_id, name=context.bot.get_chat(chat_id).title)
        local_session.add(group)
        local_session.commit()
        calendar = Calendar(name=context.bot.get_chat(chat_id).title, group_id=group.id)
        local_session.add(calendar)
        local_session.commit()
        logger.info('Bot is ready')
        context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bot is ready to work')
    else:
        # context.bot.send_message(chat_id=update.effective_chat.id, text="Calendar is already exist")
        if group.tg_id == chat_id:
            logger.info("Calendar is already exist")
        else:
            new_group = Group(tg_id=chat_id, name=context.bot.get_chat(chat_id).title)
            local_session.add(new_group)
            local_session.commit()
            statement = select(Calendar).filter_by(group_id=group.id)
            calendar = local_session.execute(statement).scalars().first()
            if calendar:
                calendar.group_id = new_group.id
                local_session.add(calendar)
                local_session.commit()
                logger.info('Bot is ready')
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Возникла ошибка. Обратитесь к админу')
            local_session.delete(group)
            local_session.commit()

initiate_handler = ChatMemberHandler(initiate_group)