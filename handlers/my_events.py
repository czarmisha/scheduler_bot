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
    ConversationHandler,
    MessageHandler,
    Filters,
)
from sqlalchemy import select

from db.models import Event, Session, engine
from .keyboards import get_date_keyboard, get_time_keyboard
from validators.eventValidator import EventValidator

local_session = Session(bind=engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATE, START, END, DESCRIPTION = range(4)

# TODO: do refactor

def my_events(update: Update, context: CallbackContext):
    if not update.message.chat.type == 'private':
        update.message.reply_text('Давайте не будем никому мешать и пообщаемся в личных сообщениях 🤫')
        return 
    global chat_id, events
    chat_id = update.effective_chat.id
    statement = select(Event).filter(Event.user_tg_id==update.effective_user.id)
    #try?
    events = local_session.execute(statement).scalars().all()
    if events:
        keyboard = [
            [InlineKeyboardButton(f'{event.description}', callback_data=f"my_event_{ind}")] for ind, event in enumerate(events)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        print(reply_markup)
        update.message.reply_text("🗃 Выберите событие:", reply_markup=reply_markup)
        return 
    else:
        update.message.reply_text("🗃 У вас нет активных событий")
        return 

def sel_event(update: Update, context: CallbackContext):
    global event
    query = update.callback_query
    query.answer()
    event = events[int(query.data[query.data.rfind('_')+1:])]
    query.edit_message_text(
        text=f'✅ Вы выбрали событие:\nНачало {event.start}\nКонец {event.end}\nОписание {event.description}\n\nВыберите действие для этого события',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('🚮 Удалить', callback_data=f'del_event'),
                InlineKeyboardButton('✏️ Редактировать', callback_data=f'edit_event')],
            ],
        )
    )

def del_event(update: Update, context: CallbackContext):
    global event
    query = update.callback_query
    query.answer()
    local_session.delete(event)
    local_session.commit()
    context.bot.send_message(chat_id, '⚰️🚽 Событие удалено! Продолжим?\n\n📝 /reserve \n🖥 /display \n🗃 /my_events')

def edit_event(update: Update, context: CallbackContext):
    global event, day, month, year
    query = update.callback_query
    query.answer()
    day = event.start.day
    month = event.start.month
    year = event.start.year

    str_day = f'0{day}' if day < 10 else day
    str_month = f'0{month}' if month < 10 else month
    query.edit_message_text(text='📅 Введите дату брони\n\nДля отмены - /cancel',
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
        text='📅 Введите дату брони\n\nДля отмены - /cancel',
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
            chat_id=chat_id, text='❗️Дата не может быть в прошлом. Ну вот, все по новой теперь..\n\n 📝 /reserve')
        return ConversationHandler.END

    hour = event.start.hour
    minute = event.start.minute

    str_min = f'0{minute}' if minute < 10 else minute
    str_h = f'0{hour}' if hour < 10 else hour
    query.edit_message_text(
        text='Введите время начала брони\n\nДля отмены - /cancel',
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '🕒start'))
    )

    return START


def increase_time(update: Update, context: CallbackContext):
    # может время по 15мин сделать а не по 5
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minute
    if query.data.startswith('inc_hour'):
        if hour >= 20:
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
        text=f'Введите время {state} брони\n\nДля отмены - /cancel',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('🕒start') else '⏰end'
        )
        )
    )


def decrease_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global hour, minute
    if query.data.startswith('dec_hour'):
        if hour <= 8:
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
        text=f'Введите время {state} брони\n\nДля отмены - /cancel',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('🕒start') else '⏰end'
        )
        )
    )


def start(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    #TODO validate date: can not be in past
    global hour, minute, event_start
    event_start = query.data
    hour += 1

    str_min = f'0{minute}' if minute < 10 else minute
    str_h = f'0{hour}' if hour < 10 else hour
    query.edit_message_text(
        text='Введите время окончания брони\n\nДля отмены - /cancel',
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '⏰end'))
    )

    return END


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    global chat_id, event_end
    event_end = query.data
    context.bot.send_message(chat_id=chat_id, text='🖊Введите описание\n\nДля отмены - /cancel')

    return DESCRIPTION


def description(update: Update, context: CallbackContext):
    global event_date, event_start, event_end
    
    event_start = datetime.datetime.strptime(event_date + ' ' + event_start, '%d.%m.%Y %H:%M')
    event_end = datetime.datetime.strptime(event_date + ' ' + event_end, '%d.%m.%Y %H:%M')

    validator = EventValidator(event_start, event_end, update.message.text)
    success, mess = validator.duration_validation()
    if not success:
        logger.error(mess)
        update.message.reply_text(mess)
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute

        str_min = f'0{minute}' if minute < 10 else minute
        str_h = f'0{hour}' if hour < 10 else hour
        update.message.reply_text(
            text='Введите время начала брони\n\nДля отмены - /cancel',
            reply_markup=InlineKeyboardMarkup(
                get_time_keyboard(str_h, str_min, '🕒start'))
        )
        return START
    
    collision = validator.collision_validation()
    if not collision[0]:
        logger.error(collision[1])
        update.message.reply_text(collision[1])
        return ConversationHandler.END

    #try
    #validate with exlude this event
    event.description = update.effective_message.text
    event.start = event_start
    event.end = event_end
    local_session.commit()
    update.message.reply_text('✏️✅ Событие изменено! Продолжим?\n\n📝 /reserve \n🖥 /display \n🗃 /my_events')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    global chat_id
    context.bot.send_message(
        chat_id=chat_id, text='Мое дело предложить - Ваше отказаться \n\n📝 /reserve \n🖥 /display \n🗃 /my_events')
    return ConversationHandler.END

edit_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_event,  pattern='^edit_event$')],
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


my_events_handler = CommandHandler("my_events", my_events)
event_handler = CallbackQueryHandler(sel_event,  pattern='^my_event_')
del_handler = CallbackQueryHandler(del_event,  pattern='^del_event$')
