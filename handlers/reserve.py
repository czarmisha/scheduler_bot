import logging
import datetime

from telegram import (
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
)

from sqlalchemy import select
from db.models import Group, Calendar, Event, Session, engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATA, START, END, DESCRIPTION = range(4)

def reserve(update: Update, context: CallbackContext):
    #TODO inline keyboar
    logger.info(update.message.text)
    update.message.reply_text(
        'Если хотите забронировать конф. зал - введите дату брони в следующем формате:\n'
        'dd.mm.yy\n\n'
        'Пример брони на 25 июня 2022 года:\n'
        '25.06.22',
        reply_markup=ReplyKeyboardRemove()
    )
    return DATA

def data(update: Update, context: CallbackContext):
    logger.info(update.message.text)
    #TODO inline keyboar
    update.message.reply_text(
        'Введите время начала брони в следующем формате:\n'
        'hh:mm\n\n'
        'Пример брони на 15:30\n'
        '15:30'
    )
    return START

def start(update: Update, context: CallbackContext):
    #TODO inline keyboar
    update.message.reply_text(
        'Введите время окончания брони в следующем формате:\n'
        'hh:mm\n\n'
        'Пример\n'
        '16:30'
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
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

reserve_handler = ConversationHandler(
        entry_points=[CommandHandler('reserve', reserve)],
        states={
            DATA: [MessageHandler(Filters.text & ~Filters.command, data)],
            START: [MessageHandler(Filters.text & ~Filters.command, start)],
            END: [MessageHandler(Filters.text & ~Filters.command, end)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )