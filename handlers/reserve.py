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
from db.models import Group, Session, engine
from handlers.keyboards import get_date_keyboard, get_time_keyboard
from validators.eventValidator import EventValidator
from utils.translation import messages

local_session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATE, START, END, DESCRIPTION = range(4)
TZ = datetime.timezone(datetime.timedelta(hours=5), 'Uzbekistan/UTC+5')

def reserve(update: Update, context: CallbackContext):
    if not update.message.chat.type == 'private':
        update.message.reply_text(f"{messages['private_error']['ru']} \n\n {messages['private_error']['uz']}")
        return ConversationHandler.END
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
        return ConversationHandler.END
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['day'] = datetime.datetime.now(TZ).day
    context.user_data['month'] = datetime.datetime.now(TZ).month
    context.user_data['year'] = datetime.datetime.now(TZ).year

    str_day = f"0{context.user_data['day']}" if context.user_data['day'] < 10 else context.user_data['day']
    str_month = f"0{context.user_data['month']}" if context.user_data['month'] < 10 else context.user_data['month']
    update.message.reply_text(f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
                              reply_markup=InlineKeyboardMarkup(
                                  get_date_keyboard(str_day, str_month, context.user_data['year']))
                              )
    return DATE


def increase_date(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    if query.data == 'inc_day' and not context.user_data['day'] == 31:
        context.user_data['day'] += 1
    elif query.data == 'inc_month' and not context.user_data['month'] == 12:
        context.user_data['month'] += 1
    elif query.data == 'inc_year':
        context.user_data['year'] += 1

    str_day = f"0{context.user_data['day']}" if context.user_data['day'] < 10 else context.user_data['day']
    str_month = f"0{context.user_data['month']}" if context.user_data['month'] < 10 else context.user_data['month']
    query.edit_message_text(
        text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, context.user_data['year']))
    )


def decrease_date(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    if query.data == 'dec_day' and not context.user_data['day'] == 1:
        context.user_data['day'] -= 1
    elif query.data == 'dec_month' and not context.user_data['month'] == 1:
        context.user_data['month'] -= 1
    elif query.data == 'dec_year' and not context.user_data['year'] == 2022:
        context.user_data['year'] -= 1

    str_day = f"0{context.user_data['day']}" if context.user_data['day'] < 10 else context.user_data['day']
    str_month = f"0{context.user_data['month']}" if context.user_data['month'] < 10 else context.user_data['month']
    query.edit_message_text(
        text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, context.user_data['year']))
    )


def date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data['event_date'] = query.data

    if int(context.user_data['event_date'][:2]) < datetime.datetime.now(TZ).day or int(context.user_data['event_date'][3:5]) < datetime.datetime.now(TZ).month:
        context.bot.send_message(
            chat_id=context.user_data['chat_id'], text='❗️Дата не может быть в прошлом. Ну вот, все по новой теперь..\n\n 📝 /reserve')
        return ConversationHandler.END

    context.user_data['hour'] = datetime.datetime.now(TZ).hour if datetime.datetime.now(TZ).hour < 20 or datetime.datetime.now(TZ).hour > 8 else 8
    context.user_data['minute'] = datetime.datetime.now(TZ).minute

    str_min = f"0{context.user_data['minute']}" if context.user_data['minute'] < 10 else context.user_data['minute']
    str_h = f"0{context.user_data['hour']}" if context.user_data['hour'] < 10 else context.user_data['hour']
    query.edit_message_text(
        text=f"{messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '🕒start'))
    )

    return START


def increase_time(update: Update, context: CallbackContext):
    # может время по 15мин сделать а не по 5
    query = update.callback_query
    logger.info(query.data)
    query.answer()

    if query.data.startswith('inc_hour'):
        if context.user_data['hour'] >= 20:
            context.user_data['hour'] = 8
        else:
            context.user_data['hour'] += 1
    elif query.data.startswith('inc_minute'):
        if not context.user_data['minute'] % 5 == 0:
            context.user_data['minute'] = context.user_data['minute'] + (5 - context.user_data['minute'] % 5)
            if context.user_data['minute'] == 60:
                context.user_data['minute'] = 0
        elif context.user_data['minute'] == 59:
            context.user_data['minute'] = 0
        else:
            context.user_data['minute'] += 5
            if context.user_data['minute'] >= 59:
                context.user_data['minute'] = 0

    str_min = f"0{context.user_data['minute']}" if context.user_data['minute'] < 10 else context.user_data['minute']
    str_h = f"0{context.user_data['hour']}" if context.user_data['hour'] < 10 else context.user_data['hour']
    txt = f"🕔 {messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}" if query.data.endswith('start') else f"{messages['select_end_time']['ru']} / {messages['select_end_time']['uz']}"
    query.edit_message_text(
        text=txt,
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('🕒start') else '⏰end'
        )
        )
    )


def decrease_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith('dec_hour'):
        if context.user_data['hour'] <= 8:
            context.user_data['hour'] = 20
        else:
            context.user_data['hour'] -= 1
    elif query.data.startswith('dec_minute'):
        if not context.user_data['minute'] % 5 == 0:
            context.user_data['minute'] = context.user_data['minute'] - (context.user_data['minute'] % 5)
        elif context.user_data['minute'] == 0:
            context.user_data['minute'] = 55
        else:
            context.user_data['minute'] -= 5

    str_min = f"0{context.user_data['minute']}" if context.user_data['minute'] < 10 else context.user_data['minute']
    str_h = f"0{context.user_data['hour']}" if context.user_data['hour'] < 10 else context.user_data['hour']
    txt = f"🕔 {messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}" if query.data.endswith('start') else f"{messages['select_end_time']['ru']} / {messages['select_end_time']['uz']}"
    query.edit_message_text(
        text=txt,
        reply_markup=InlineKeyboardMarkup(get_time_keyboard(
            str_h, str_min, 'start' if query.data.endswith('🕒start') else '⏰end'
        )
        )
    )


def start(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    #TODO validate date: can not be in past
    context.user_data['event_start'] = query.data
    context.user_data['hour'] += 1

    str_min = f"0{context.user_data['minute']}" if context.user_data['minute'] < 10 else context.user_data['minute']
    str_h = f"0{context.user_data['hour']}" if context.user_data['hour'] < 10 else context.user_data['hour']
    query.edit_message_text(
        text=f"{messages['select_end_time']['ru']} / {messages['select_end_time']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '⏰end'))
    )

    return END


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data['event_end'] = query.data
    context.bot.send_message(chat_id=context.user_data['chat_id'], text=f"🖊 {messages['input_description']['ru']} / {messages['input_description']['uz']}")

    return DESCRIPTION


def description(update: Update, context: CallbackContext):

    context.user_data['event_start'] = datetime.datetime.strptime(context.user_data['event_date'] + ' ' + context.user_data['event_start'], '%d.%m.%Y %H:%M')
    context.user_data['event_end'] = datetime.datetime.strptime(context.user_data['event_date'] + ' ' + context.user_data['event_end'], '%d.%m.%Y %H:%M')

    validator = EventValidator(context.user_data['event_start'], context.user_data['event_end'], update.message.text)
    success, mess = validator.duration_validation()
    if not success:
        logger.error(mess)
        update.message.reply_text(mess)
        hour = datetime.datetime.now(TZ).hour
        minute = datetime.datetime.now(TZ).minute

        str_min = f'0{minute}' if minute < 10 else minute
        str_h = f'0{hour}' if hour < 10 else hour
        update.message.reply_text(
            text=f"{messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}",
            reply_markup=InlineKeyboardMarkup(
                get_time_keyboard(str_h, str_min, '🕒start'))
        )
        return START
    
    collision = validator.collision_validation()
    if not collision[0]:
        logger.error(collision[1])
        update.message.reply_text(collision[1])
        hour = datetime.datetime.now(TZ).hour
        minute = datetime.datetime.now(TZ).minute

        str_min = f'0{minute}' if minute < 10 else minute
        str_h = f'0{hour}' if hour < 10 else hour
        update.message.reply_text(
            text=f"{messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}",
            reply_markup=InlineKeyboardMarkup(
                get_time_keyboard(str_h, str_min, '🕒start'))
        )
        return START
    event = validator.create_event(update.effective_user)
    if not event[0]:
        logger.error(event[1])
        update.message.reply_text(event[1])
        return ConversationHandler.END

    update.message.reply_text(f"{messages['event_is_created']['ru']} / {messages['event_is_created']['uz']} \n\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")
    author = f"@{update.effective_user.username}" if update.effective_user.username else f"{update.effective_user.first_name}"
    context.bot.send_message(chat_id=validator.group.tg_id,
                             text=f"{messages['new_event']['ru']}: \n\n"
                             f"{messages['start']['ru']}: {validator.start}\n"
                             f"{messages['end']['ru']}: {validator.end}\n"
                             f"{messages['description']['ru']}: {validator.description}\n"
                             f"{messages['author']['ru']}: {author}"
                             f"\n\n{messages['new_event']['uz']}: \n\n"
                             f"{messages['start']['uz']}: {validator.start}\n"
                             f"{messages['end']['uz']}: {validator.end}\n"
                             f"{messages['description']['uz']}: {validator.description}\n"
                             f"{messages['author']['uz']}: {author}"
                             )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=context.user_data['chat_id'], text=f"{messages['canceled']['ru']}\n\t\t{messages['canceled']['uz']}\n\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")
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
    conversation_timeout=datetime.timedelta(seconds=60),
    allow_reentry=True,
    run_async=True,
    per_user=True,
)
