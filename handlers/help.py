from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from sqlalchemy import select
from db.models import Group, Session, engine
from utils.translation import messages

local_session = Session(bind=engine)

def help(update: Update, context: CallbackContext):
    if not update.message.chat.type == 'private':
        # update.message.reply_text(f"{messages['private_error']['ru']} \n\n {messages['private_error']['uz']}")
        return 
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
    else:
        update.message.reply_text(f"Документация: \nhttps://telegra.ph/Dokumentaciya-k-botu-Event-Scheduler-Uzinfocom-08-18", parse_mode='HTML')


help_handler = CommandHandler('help', help)