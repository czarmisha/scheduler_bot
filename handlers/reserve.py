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

    buttons = [
        [
            InlineKeyboardButton('День', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_day'),
            InlineKeyboardButton(f'{day}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_day'),
        ],
        [
            InlineKeyboardButton('Месяц', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_month'),
            InlineKeyboardButton(f'{month}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_month'),
        ],
        [
            InlineKeyboardButton('Год', callback_data=-3),
            InlineKeyboardButton('➖', callback_data='dec_year'),
            InlineKeyboardButton(f'{year}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_year'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    update.message.reply_text('Введите дату брони',
        reply_markup=InlineKeyboardMarkup(buttons)
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

    buttons = [
        [
            InlineKeyboardButton('День', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_day'),
            InlineKeyboardButton(f'{day}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_day'),
        ],
        [
            InlineKeyboardButton('Месяц', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_month'),
            InlineKeyboardButton(f'{month}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_month'),
        ],
        [
            InlineKeyboardButton('Год', callback_data=-3),
            InlineKeyboardButton('➖', callback_data='dec_year'),
            InlineKeyboardButton(f'{year}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_year'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(buttons)
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

    buttons = [
        [
            InlineKeyboardButton('День', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_day'),
            InlineKeyboardButton(f'{day}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_day'),
        ],
        [
            InlineKeyboardButton('Месяц', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_month'),
            InlineKeyboardButton(f'{month}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_month'),
        ],
        [
            InlineKeyboardButton('Год', callback_data=-3),
            InlineKeyboardButton('➖', callback_data='dec_year'),
            InlineKeyboardButton(f'{year}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_year'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите дату брони',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def data(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minutes
    hour = datetime.datetime.now().hour
    minutes = datetime.datetime.now().minute
    
    buttons = [
        [
            InlineKeyboardButton('Часы', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{hour}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [
            InlineKeyboardButton('Минуты', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_minutes'),
            InlineKeyboardButton(f'{minutes}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_minutes'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите время начала брони',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    return START

def increase_time(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minutes
    if query.data == 'inc_hour':
        hour += 1
    elif query.data == 'inc_minutes':
        minutes += 1

    buttons = [
        [
            InlineKeyboardButton('Часы', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{hour}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [
            InlineKeyboardButton('Минуты', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_minutes'),
            InlineKeyboardButton(f'{minutes}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_minutes'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите время начала брони',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def decrease_time(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minutes
    if query.data == 'dec_hour':
        hour -= 1
    elif query.data == 'dec_minutes':
        minutes -= 1

    buttons = [
        [
            InlineKeyboardButton('Часы', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{hour}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [
            InlineKeyboardButton('Минуты', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{minutes}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите время начала брони',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def start(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    global hour, minutes

    hour = datetime.datetime.now().hour + 1
    minutes = datetime.datetime.now().minute
    
    buttons = [
        [
            InlineKeyboardButton('Часы', callback_data=-1),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{hour}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [
            InlineKeyboardButton('Минуты', callback_data=-2),
            InlineKeyboardButton('➖', callback_data='dec_hour'),
            InlineKeyboardButton(f'{minutes}', callback_data=2),
            InlineKeyboardButton('➕', callback_data='inc_hour'),
        ],
        [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
        [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
    ]
    query.edit_message_text(
        text='Введите время окончания брони',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    return END

def end(update: Update, context: CallbackContext):
    logger.info(update.message.text)
    update.message.reply_text(
        'Введите описание'
    )
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
                CallbackQueryHandler(data, pattern='^done$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            END: [
                CallbackQueryHandler(increase_time, pattern='^inc_'),
                CallbackQueryHandler(decrease_time, pattern='^dec_'),
                CallbackQueryHandler(data, pattern='^done$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )