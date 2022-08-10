import logging
import datetime

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
)
from sqlalchemy import select, and_

from db.models import Event, Session, engine

local_session = Session(bind=engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TZ = datetime.timezone(datetime.timedelta(hours=5), 'Uzbekistan/UTC+5')

# TODO: do refactor
# TODO use pandas to create table and import to jpg with pillow and send to user
# https://datatofish.com/create-pandas-dataframe/
# https://pypi.org/project/dataframe-image/
# День            Начало    Конец    Описание
# Понедельник     9:00      11:00     Собрание
# Вторник
# Среда
# Четверг
# Пятница

def display(update: Update, context: CallbackContext):
    if not update.message.chat.type == 'private':
        update.message.reply_text('Давайте не будем никому мешать и пообщаемся в личных сообщениях 🤫')
        return 
    global chat_id
    chat_id = update.effective_chat.id
    keyboard = [
        [
            InlineKeyboardButton("На сегодня", callback_data="display_1"),
            InlineKeyboardButton("На завтра", callback_data="display_2"),
        ],
        [
            InlineKeyboardButton("На эту неделю", callback_data="display_3"),
            InlineKeyboardButton("На следующую неделю",
                                 callback_data="display_4"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("📅Выберите дату:", reply_markup=reply_markup)


def option(update: Update, context: CallbackContext):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    today = datetime.datetime.now(TZ)

    if query.data[-1] == '1':
        """today"""
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = today.replace(hour=23, minute=59, second=59)
        text = create_text(get_events(start,end), query.data[-1])
        
    elif query.data[-1] == '2':
        """tomorrow"""
        start = today.replace(
            hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        end = today.replace(
            hour=23, minute=59, second=59) + datetime.timedelta(days=1)
        text = create_text(get_events(start,end), query.data[-1])
        
    elif query.data[-1] == '3':
        """current week"""
        start = today.replace(hour=0, minute=0, second=0, microsecond=0) - \
            datetime.timedelta(days=today.isoweekday() - 1)
        end = today.replace(hour=23, minute=59, second=59) + \
            datetime.timedelta(days=5 - today.isoweekday())
        text = create_text(get_events(start,end), query.data[-1])
        
    elif query.data[-1] == '4':
        """next week"""
        start = today.replace(hour=0, minute=0, second=0, microsecond=0) + \
            datetime.timedelta(days=8 - today.isoweekday())
        end = today.replace(hour=23, minute=59, second=59) + \
            datetime.timedelta(days=12 - today.isoweekday())
        text = create_text(get_events(start,end), query.data[-1])
        
    context.bot.send_message(chat_id, text)

def get_events(start, end):
    statement = select(Event).filter(and_(
                                        Event.start > start,
                                        Event.end < end,
                                    )).order_by(Event.start)
    return local_session.execute(statement).scalars().all()

def create_text(events, period):
    text = '📖Список броней как вы и просили: \n\n'
    week = {
        1: '\n📅Понедельник: \n',
        2: '\n📅Вторник: \n',
        3: '\n📅Среда: \n',
        4: '\n📅Четверг: \n',
        5: '\n📅Пятница: \n',
    }
    if period == '1' or period == '2':
        for event in events:
            start_hour = event.start.hour if event.start.hour > 9 else f'0{event.start.hour}'
            start_minute = event.start.minute if event.start.minute > 9 else f'0{event.start.minute}'
            end_hour = event.end.hour if event.end.hour > 9 else f'0{event.end.hour}'
            end_minute = event.end.minute if event.end.minute > 9 else f'0{event.end.minute}'
            text += f'\t\t {start_hour}:{start_minute} - {end_hour}:{end_minute} {event.description} \n'

    else:
        for event in events:
            start_hour = event.start.hour if event.start.hour > 9 else f'0{event.start.hour}'
            start_minute = event.start.minute if event.start.minute > 9 else f'0{event.start.minute}'
            end_hour = event.end.hour if event.end.hour > 9 else f'0{event.end.hour}'
            end_minute = event.end.minute if event.end.minute > 9 else f'0{event.end.minute}'
            week[event.start.isoweekday()] += f'\t {start_hour}:{start_minute} - {end_hour}:{end_minute} {event.description} \n'

        for str in week.values():
            text += str

    text += '\n📝 /reserve \n🖥 /display \n🗃 /my_events'
    return text

display_handler = CommandHandler("display", display)
option_handler = CallbackQueryHandler(option,  pattern='^display_')
