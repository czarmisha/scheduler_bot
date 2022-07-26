from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from sqlalchemy import select
from db.models import Group, Session, engine

local_session = Session(bind=engine)

RESERVE, DISPLAY = range(2)

def start(update: Update, context: CallbackContext):
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    # проверка группы еще по названию нужна
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id, text="У Вас нет прав общаться со мной")
    else:
        reply_keyboard = [['/reserve', '/display', '/my_events']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text(
            'Меня зовут планировщик концференц. зала Uzinfocom. '
            'Вот, что я умею:\n\n'
            'Команда /reserve, чтобы забронировать зал.\n'
            'Команда /my_events, чтобы отобразить ваш список мероприятий\n'
            'Команда /display, чтобы отобразить список брони.\n\n'
            'по вопросам сотрудничества и рекламы - @m_dergachyov',
            reply_markup=markup_key)

start_handler = CommandHandler('start', start)
