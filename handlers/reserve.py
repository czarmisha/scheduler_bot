from calendar import calendar
from email import message
import logging
import datetime

from telegram import (
    Update,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    CallbackQueryHandler,
)

from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound
from db.models import Group, Calendar, Event, Session, engine

from handlers.keyboards import get_date_keyboard, get_time_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

local_session = Session(bind=engine)

DATE, START, END, DESCRIPTION = range(4)


def reserve(update: Update, context: CallbackContext):
    logger.info(update.message.text)

    global day, month, year, chat_id
    chat_id = update.effective_chat.id
    day = datetime.datetime.today().day
    month = datetime.datetime.today().month
    year = datetime.datetime.today().year

    str_day = f'0{day}' if day < 10 else day
    str_month = f'0{month}' if month < 10 else month
    update.message.reply_text('Введите дату брони',
                              reply_markup=InlineKeyboardMarkup(
                                  get_date_keyboard(str_day, str_month, year))
                              )
    return DATE


def increase_date(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global day, month, year
    if query.data == 'inc_day' and not day == 31:
        day += 1
    elif query.data == 'inc_month' and not month == 12:
        month += 1
    elif query.data == 'inc_year':
        year += 1

    str_day = f'0{day}' if day < 10 else day
    str_month = f'0{month}' if month < 10 else month
    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, year))
    )


def decrease_date(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global day, month, year
    if query.data == 'dec_day' and not day == 1:
        day -= 1
    elif query.data == 'dec_month' and not month == 1:
        month -= 1
    elif query.data == 'dec_year' and not year == 2022:
        year -= 1

    str_day = f'0{day}' if day < 10 else day
    str_month = f'0{month}' if month < 10 else month
    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, year))
    )


def date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global day, hour, minute, event_date
    event_date = query.data

    if int(event_date[:2]) < datetime.datetime.today().day or int(event_date[3:5]) < datetime.datetime.today().month:
        global chat_id
        context.bot.send_message(
            chat_id=chat_id, text='Дата не может быть в прошлом. Ну вот, все по новой теперь..\n\n /reserve')
        return ConversationHandler.END

    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute

    str_min = f'0{minute}' if minute < 10 else minute
    str_h = f'0{hour}' if hour < 10 else hour
    query.edit_message_text(
        text='Введите время начала брони',
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, 'start'))
    )

    return START


def increase_time(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minute
    if query.data.startswith('inc_hour'):
        if hour == 20:
            hour = 8
        else:
            hour += 1
    elif query.data.startswith('inc_minute'):
        if not minute % 5 == 0:
            minute = minute + (5 - minute % 5)
            if minute == 60:
                minute = 0
        elif minute == 59:
            minute = 0
        else:
            minute += 5
            if minute >= 59:
                minute = 0

    str_min = f'0{minute}' if minute < 10 else minute
    str_h = f'0{hour}' if hour < 10 else hour
    state = 'начала' if query.data.endswith('start') else 'окончания'
    query.edit_message_text(
        text=f'Введите время {state} брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('start') else 'end'
        )
        )
    )


def decrease_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global hour, minute
    if query.data.startswith('dec_hour'):
        if hour == 8:
            hour = 20
        else:
            hour -= 1
    elif query.data.startswith('dec_minute'):
        if not minute % 5 == 0:
            minute = minute - (minute % 5)
        elif minute == 0:
            minute = 55
        else:
            minute -= 5

    str_min = f'0{minute}' if minute < 10 else minute
    str_h = f'0{hour}' if hour < 10 else hour
    state = 'начала' if query.data.endswith('start') else 'окончания'
    query.edit_message_text(
        text=f'Введите время {state} брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('start') else 'end'
        )
        )
    )


def start(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global hour, minutes, event_start
    event_start = query.data
    hour = datetime.datetime.now().hour + 1
    minutes = datetime.datetime.now().minute

    query.edit_message_text(
        text='Введите время окончания брони',
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(hour, minute, 'end'))
    )

    return END


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global chat_id, event_end
    event_end = query.data
    context.bot.send_message(chat_id=chat_id, text='Введите описание')

    return DESCRIPTION


def description(update: Update, context: CallbackContext):
    # TODO validate date
    # есть ли бронь на это время  end < start1 ok, start1<end<end1 err, start1<start<end1 err, start>end1 ok

    statement = select(Group)
    try:
        group = local_session.execute(statement).scalars().one_or_none()
    except MultipleResultsFound:
        logger.error('больше 1й группы в бд')
        update.message.reply_text(
            'Ошибка! больше 1й группы в бд. обратитесь к админу')
        return ConversationHandler.END
    if not group:
        logger.error('нет бд при создании события')
        update.message.reply_text('Ошибка! Нет группы в базе данных')
        return ConversationHandler.END

    statement = select(Calendar).where(Calendar.group_id == group.id)
    try:
        calendar = local_session.execute(statement).scalars().one_or_none()
    except MultipleResultsFound:
        logger.error('больше 1го календаря в бд')
        update.message.reply_text(
            'Ошибка! больше 1го календаря в бд. обратитесь к админу')
        return ConversationHandler.END
    if not calendar:
        logger.error('Нет календаря при создании события')
        update.message.reply_text('Ошибка! Нет календаря в базе данных')
        return ConversationHandler.END

    global event_date, event_start, event_end
    event_start = event_date + ' ' + event_start
    event_start = datetime.datetime.strptime(event_start, '%d.%m.%Y %H:%M')
    event_end = event_date + ' ' + event_end
    event_end = datetime.datetime.strptime(event_end, '%d.%m.%Y %H:%M')
    diff = event_end - event_start
    if diff.total_seconds() < 300:
        logger.error('Событие не может длиться меньше 5минут')
        update.message.reply_text('Событие не может длиться меньше 5минут')
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute

        str_min = f'0{minute}' if minute < 10 else minute
        str_h = f'0{hour}' if hour < 10 else hour
        update.message.reply_text(
            text='Введите время начала брони',
            reply_markup=InlineKeyboardMarkup(
                get_time_keyboard(str_h, str_min, 'start'))
        )

        return START
    elif diff.total_seconds() > 28800:
        logger.error('Событие не может длиться больше 8 часов')
        update.message.reply_text('Событие не может длиться больше 8 часов')
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute

        str_min = f'0{minute}' if minute < 10 else minute
        str_h = f'0{hour}' if hour < 10 else hour
        update.message.reply_text(
            text='Введите время начала брони',
            reply_markup=InlineKeyboardMarkup(
                get_time_keyboard(str_h, str_min, 'start'))
        )

        return START

    event = Event(
        start=event_start,
        end=event_end,
        description=update.message.text,
        calendar_id=calendar.id,
        is_repeated=False
    )
    local_session.add(event)
    local_session.commit()
    update.message.reply_text('Событие создано')
    context.bot.send_message(chat_id=group.tg_id,
                             text='Только что было создано новое событие \n\n'
                             f'Дата начала: {event_start}\n'
                             f'Дата окончания: {event_end}\n'
                             f'Описание: {update.message.text}'
                             )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.callback_query.answer()
    global chat_id
    context.bot.send_message(
        chat_id=chat_id, text='Мое дело предложить - Ваше отказаться')
    return ConversationHandler.END


reserve_handler = ConversationHandler(
    entry_points=[CommandHandler('reserve', reserve)],
    states={
        DATE: [
            CallbackQueryHandler(increase_date, pattern='^inc_'),
            CallbackQueryHandler(decrease_date, pattern='^dec_'),
            CallbackQueryHandler(
                date, pattern="^[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2}$"),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
        START: [
            CallbackQueryHandler(increase_time, pattern='^inc_'),
            CallbackQueryHandler(decrease_time, pattern='^dec_'),
            CallbackQueryHandler(
                start, pattern='^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
        END: [
            CallbackQueryHandler(increase_time, pattern='^inc_'),
            CallbackQueryHandler(decrease_time, pattern='^dec_'),
            CallbackQueryHandler(
                end, pattern='^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
        ],
        DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
