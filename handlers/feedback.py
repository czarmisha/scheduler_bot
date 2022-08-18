import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler

from sqlalchemy import select
from db.models import Group, Session, engine
from utils.translation import messages

local_session = Session(bind=engine)

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BODY = range(1)
# _ADMIN_ID = os.environ['ADMIN_ID']
_ADMIN_ID=4644278

def feedback(update: Update, context: CallbackContext):
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
        return ConversationHandler.END
    else:
        context.user_data['chat_id'] = update.effective_chat.id
        context.user_data['user'] = update.effective_user
        update.message.reply_text(f"🗣 {messages['feedback_title']['ru']}✖️ {messages['for_cancel']['ru']} /cancel\n\n🗣 {messages['feedback_title']['uz']}✖️ {messages['for_cancel']['uz']} /cancel")
        return BODY

def enter_text(update: Update, context: CallbackContext):
    admin_text = "New feedback from user:\n\n"\
                f"ID: {context.user_data['user'].id}\n"\
                f"Firstname: {context.user_data['user'].first_name}\n"
    if context.user_data['user'].username:
        admin_text += f"Username: @{context.user_data['user'].username}"
    admin_text += f"\nText: {update.message.text} \n\n #feedback"
    context.bot.send_message(chat_id=_ADMIN_ID, text=admin_text)
    update.message.reply_text(f"✔️ {messages['feedback_complete']['ru']}\n✔️ {messages['feedback_complete']['uz']}\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=context.user_data['chat_id'], text="Canceled feedback")
    return ConversationHandler.END

feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback)],
    states={
        BODY: [MessageHandler(Filters.text & ~Filters.command, enter_text)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    conversation_timeout=datetime.timedelta(seconds=60),
    allow_reentry=True,
    run_async=True,
    per_user=True,
)