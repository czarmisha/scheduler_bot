import logging
import datetime

from telegram import (
    CallbackQuery,
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
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
from db.models import Group, Calendar, Event, Session, engine

from handlers.keyboards import get_data_keyboard, get_time_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATA, START, END, DESCRIPTION = range(4)

def reserve(update: Update, context: CallbackContext):
    logger.info(update.message.text)

    global day, month, year, chat_id
    chat_id = update.effective_chat.id
    day = datetime.datetime.today().day
    month = datetime.datetime.today().month
    year = datetime.datetime.today().year

    update.message.reply_text('Введите дату брони',
        reply_markup=InlineKeyboardMarkup(get_data_keyboard(day, month, year))
        # reply_markup=ReplyKeyboardRemove()
    )
    return DATA

def increase_data(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global day, month, year
    if query.data == 'inc_day':
        day += 1
    elif query.data == 'inc_month':
        month += 1
    elif query.data == 'inc_year':
        year += 1

    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(get_data_keyboard(day, month, year))
    )

def decrease_data(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global day, month, year
    if query.data == 'dec_day':
        day -= 1
    elif query.data == 'dec_month':
        month -= 1
    elif query.data == 'dec_year':
        year -= 1

    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(get_data_keyboard(day, month, year))
    )

def data(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minute
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    
    query.edit_message_text(
        text='Введите время начала брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(hour, minute, 'start'))
    )

    return START

def increase_time(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minute
    if query.data.startswith('inc_hour'):
        hour += 1
    elif query.data.startswith('inc_minute'):
        minute += 1


    state = 'начала' if query.data.endswith('start') else 'окончания'
    query.edit_message_text(
        text=f'Введите время {state} брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
                hour, minute, 'start' if query.data.endswith('start') else 'end'
            )
        )
    )


def decrease_time(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minute
    if query.data.startswith('dec_hour'):
        hour -= 1
    elif query.data.startswith('dec_minute'):
        minute -= 1
    
    state = 'начала' if query.data.endswith('start') else 'окончания'
    query.edit_message_text(
        text=f'Введите время {state} брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
                hour, minute, 'start' if query.data.endswith('start') else 'end'
            )
        )
    )

def start(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minutes

    hour = datetime.datetime.now().hour + 1
    minutes = datetime.datetime.now().minute
    
    query.edit_message_text(
        text='Введите время окончания брони',
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(hour, minute, 'end'))
    )

    return END

def end(update: Update, context: CallbackContext):
    global chat_id
    context.bot.send_message(chat_id=chat_id, text='Введите описание')

    return DESCRIPTION

def description(update: Update, context: CallbackContext):
    logger.info(update)
    #TODO validate date
    update.message.reply_text('Результат')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.callback_query.answer()
    global chat_id
    context.bot.send_message(chat_id=chat_id, text='Мое дело предложить - Ваше отказаться')
    # update.message.reply_text(
    #     'Мое дело предложить - Ваше отказаться', 
    #     reply_markup=ReplyKeyboardRemove()
    # )
    return ConversationHandler.END

reserve_handler = ConversationHandler(
        entry_points=[CommandHandler('reserve', reserve)],
        states={
            DATA: [
                CallbackQueryHandler(increase_data, pattern='^inc_'),
                CallbackQueryHandler(decrease_data, pattern='^dec_'),
                CallbackQueryHandler(data, pattern='^done$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
                # MessageHandler(Filters.text & ~Filters.command, data)
                # CallbackQueryHandler(increase, pattern='\b([1-9]|[12][0-9]|3[01])\b'),
                # CallbackQueryHandler(decrease, pattern='\b([1-9]|1[0-2])\b'),
                # CallbackQueryHandler(data, pattern='\b202[23]\b'),
            ],
            START: [
                CallbackQueryHandler(increase_time, pattern='^inc_'),
                CallbackQueryHandler(decrease_time, pattern='^dec_'),
                CallbackQueryHandler(start, pattern='^done$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            END: [
                CallbackQueryHandler(increase_time, pattern='^inc_'),
                CallbackQueryHandler(decrease_time, pattern='^dec_'),
                CallbackQueryHandler(end, pattern='^done$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )