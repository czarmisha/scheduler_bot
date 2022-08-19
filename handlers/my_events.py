import logging
import datetime
from tokenize import group

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
from utils.translation import messages

local_session = Session(bind=engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

DATE, START, END, DESCRIPTION = range(4)
TZ = datetime.timezone(datetime.timedelta(hours=5), 'Uzbekistan/UTC+5')

# TODO: do refactor

def my_events(update: Update, context: CallbackContext):
    if not update.message.chat.type == 'private':
        update.message.reply_text(f"{messages['private_error']['ru']} \n\n {messages['private_error']['uz']}")
        return 
    context.user_data["chat_id"] = update.effective_chat.id
    statement = select(Event).filter(Event.author_id==update.effective_user.id)
    #try?
    context.user_data["events"] = local_session.execute(statement).scalars().all()
    if context.user_data["events"]:
        keyboard = [
            [InlineKeyboardButton(f'{event.description}', callback_data=f"my_event_{ind}")] for ind, event in enumerate(context.user_data["events"])
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        print(reply_markup)
        update.message.reply_text(f"🗃 {messages['select_event']['ru']}\n\t\t{messages['select_event']['uz']}:", reply_markup=reply_markup)
        return 
    else:
        update.message.reply_text(f"🗃 {messages['active_events']['ru']} / {messages['active_events']['uz']}")
        return 

def sel_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["event"] = context.user_data['events'][int(query.data[query.data.rfind('_')+1:])]
    query.edit_message_text(
        text=f"✅ {messages['your_select']['ru']}:\n{messages['start']['ru']} {context.user_data['event'].start}\n{messages['end']['ru']} {context.user_data['event'].end}\n{messages['description']['ru']} {context.user_data['event'].description}\n\n{messages['select_action']['ru']}\n\n"\
            f"✅ {messages['your_select']['uz']}:\n{messages['start']['uz']} {context.user_data['event'].start}\n{messages['end']['uz']} {context.user_data['event'].end}\n{messages['description']['uz']} {context.user_data['event'].description}\n\n{messages['select_action']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"✏️ {messages['edit']['ru']} / {messages['edit']['uz']}", callback_data=f'edit_event')],
                [InlineKeyboardButton(f"🗑 {messages['delete']['ru']} / {messages['delete']['uz']}", callback_data=f'del_event')]
            ],
        )
    )

def del_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    group = EventValidator().get_group()
    author = f"@{update.effective_user.username}" if update.effective_user.username else f"{update.effective_user.first_name}" 
    if group[0]:
        context.bot.send_message(chat_id=group[1].tg_id,
                                text=f"🗑 {messages['del_alert']['ru']}: \n\n"
                                f"{messages['start']['ru']}: {context.user_data['event'].start}\n"
                                f"{messages['end']['ru']}: {context.user_data['event'].end}\n"
                                f"{messages['description']['ru']}: {context.user_data['event'].description}\n"
                                f"{messages['author']['ru']}: {author}"
                                f"\n\n🗑 {messages['del_alert']['uz']}: \n\n"
                                f"{messages['start']['uz']}: {context.user_data['event'].start}\n"
                                f"{messages['end']['uz']}: {context.user_data['event'].end}\n"
                                f"{messages['description']['uz']}: {context.user_data['event'].description}\n"
                                f"{messages['author']['uz']}: {author}"
                                )
    local_session.delete(context.user_data["event"])
    local_session.commit()
    context.bot.send_message(context.user_data['chat_id'], f"🗑 {messages['event_is_deleted']['ru']}\n\t\t{messages['event_is_deleted']['uz']}\n\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")

def edit_event(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["day"] = context.user_data["event"].start.day
    context.user_data["month"] = context.user_data["event"].start.month
    context.user_data["year"] = context.user_data["event"].start.year
    context.user_data["event_id"] = context.user_data["event"].id

    str_day = f'0{context.user_data["day"]}' if context.user_data["day"] < 10 else context.user_data["day"]
    str_month = f'0{context.user_data["month"]}' if context.user_data["month"] < 10 else context.user_data["month"]
    query.edit_message_text(text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
                                reply_markup=InlineKeyboardMarkup(
                                get_date_keyboard(str_day, str_month, context.user_data["year"]))
                            )
    return DATE

def increase_date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'inc_day' and not context.user_data["day"] == 31:
        context.user_data["day"] += 1
    elif query.data == 'inc_month' and not context.user_data["month"] == 12:
        context.user_data["month"] += 1
    elif query.data == 'inc_year':
        context.user_data["year"] += 1

    str_day = f'0{context.user_data["day"]}' if context.user_data["day"] < 10 else context.user_data["day"]
    str_month = f'0{context.user_data["month"]}' if context.user_data["month"] < 10 else context.user_data["month"]
    query.edit_message_text(
        text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, context.user_data["year"]))
    )


def decrease_date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'dec_day' and not context.user_data["day"] == 1:
        context.user_data["day"] -= 1
    elif query.data == 'dec_month' and not context.user_data["month"] == 1:
        context.user_data["month"] -= 1
    elif query.data == 'dec_year' and not context.user_data["year"] == 2022:
        context.user_data["year"] -= 1

    str_day = f'0{context.user_data["day"]}' if context.user_data["day"] < 10 else context.user_data["day"]
    str_month = f'0{context.user_data["month"]}' if context.user_data["month"] < 10 else context.user_data["month"]
    query.edit_message_text(
        text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_date_keyboard(str_day, str_month, context.user_data["year"]))
    )


def date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data["event_date"] = query.data
    if datetime.datetime.strptime(context.user_data["event_date"], '%d.%m.%Y').replace(tzinfo=TZ) < datetime.datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0):
        context.bot.send_message(
            chat_id=context.user_data["chat_id"], text=f"❗️ {messages['date_in_past']['ru']}\n{messages['date_in_past']['uz']}\n\n")
        str_day = f'0{context.user_data["day"]}' if context.user_data["day"] < 10 else context.user_data["day"]
        str_month = f'0{context.user_data["month"]}' if context.user_data["month"] < 10 else context.user_data["month"]
        context.bot.send_message(chat_id=context.user_data["chat_id"], text=f"📅 {messages['select_date']['ru']} / {messages['select_date']['uz']}",
                                reply_markup=InlineKeyboardMarkup(
                                get_date_keyboard(str_day, str_month, context.user_data["year"]))
                            )
        return DATE

    context.user_data["hour"] = datetime.datetime.now(TZ).hour if datetime.datetime.now(TZ).hour < 20 or datetime.datetime.now(TZ).hour > 8 else 8
    context.user_data["minute"] = context.user_data["event"].start.minute

    str_min = f'0{context.user_data["minute"]}' if context.user_data["minute"] < 10 else context.user_data["minute"]
    str_h = f'0{context.user_data["hour"]}' if context.user_data["hour"] < 10 else context.user_data["hour"]
    query.edit_message_text(
        text=f"{messages['select_start_time']['ru']} / {messages['select_start_time']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '🕒start'))
    )

    return START


def increase_time(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith('inc_hour'):
        if context.user_data["hour"] >= 20:
            context.user_data["hour"] = 8
        else:
            context.user_data["hour"] += 1
    elif query.data.startswith('inc_minute'):
        if not context.user_data["minute"] % 5 == 0:
            context.user_data["minute"] = context.user_data["minute"] + (5 - context.user_data["minute"] % 5)
            if context.user_data["minute"] == 60:
                context.user_data["minute"] = 0
        elif context.user_data["minute"] == 59:
            context.user_data["minute"] = 0
        else:
            context.user_data["minute"] += 5
            if context.user_data["minute"] >= 59:
                context.user_data["minute"] = 0

    str_min = f'0{context.user_data["minute"]}' if context.user_data["minute"] < 10 else context.user_data["minute"]
    str_h = f'0{context.user_data["hour"]}' if context.user_data["hour"] < 10 else context.user_data["hour"]
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
        if context.user_data["hour"] <= 8:
            context.user_data["hour"] = 20
        else:
            context.user_data["hour"] -= 1
    elif query.data.startswith('dec_minute'):
        if not context.user_data["minute"] % 5 == 0:
            context.user_data["minute"] = context.user_data["minute"] - (context.user_data["minute"] % 5)
        elif context.user_data["minute"] == 0:
            context.user_data["minute"] = 55
        else:
            context.user_data["minute"] -= 5

    str_min = f'0{context.user_data["minute"]}' if context.user_data["minute"] < 10 else context.user_data["minute"]
    str_h = f'0{context.user_data["hour"]}' if context.user_data["hour"] < 10 else context.user_data["hour"]
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

    context.user_data["event_start"] = query.data
    context.user_data["hour"] += 1

    str_min = f'0{context.user_data["minute"]}' if context.user_data["minute"] < 10 else context.user_data["minute"]
    str_h = f'0{context.user_data["hour"]}' if context.user_data["hour"] < 10 else context.user_data["hour"]
    query.edit_message_text(
        text=f"🕔 {messages['select_end_time']['ru']} / {messages['select_end_time']['uz']}",
        reply_markup=InlineKeyboardMarkup(
            get_time_keyboard(str_h, str_min, '⏰end'))
    )

    return END


def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.user_data["event_end"] = query.data
    context.bot.send_message(chat_id=context.user_data["chat_id"], text=f"🖊 {messages['input_description']['ru']} / {messages['input_description']['uz']}")

    return DESCRIPTION


def description(update: Update, context: CallbackContext):
    
    context.user_data["event_start"] = datetime.datetime.strptime(context.user_data["event_date"] + ' ' + context.user_data["event_start"], '%d.%m.%Y %H:%M')
    context.user_data["event_end"] = datetime.datetime.strptime(context.user_data["event_date"] + ' ' + context.user_data["event_end"], '%d.%m.%Y %H:%M')
    # context.user_data["event_before_editing"] = context.user_data["event"].copy()

    validator = EventValidator(context.user_data["event_start"], context.user_data["event_end"], update.message.text)
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
    
    collision = validator.collision_validation(edit=True, event_id=context.user_data["event_id"])
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
    desc_before = context.user_data["event"].description
    start_before = context.user_data["event"].start
    end_before = context.user_data["event"].end
    if update.effective_message.text:
        context.user_data["event"].description = update.effective_message.text
    context.user_data["event"].start = context.user_data["event_start"]
    context.user_data["event"].end = context.user_data["event_end"]
    local_session.commit()
    update.message.reply_text(f"✏️✅ {messages['event_is_edited']['ru']}\n\t\t{messages['event_is_edited']['uz']}\n\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")
    author = f"@{update.effective_user.username}" if update.effective_user.username else f"{update.effective_user.first_name}" 
    group = validator.get_group()
    context.bot.send_message(chat_id=group[1].tg_id,
                            text=f"✏️ {messages['edit_alert']['ru']}: \n\n"
                            f"{messages['start']['ru']}: {start_before} => {context.user_data['event'].start}\n"
                            f"{messages['end']['ru']}: {end_before} => {context.user_data['event'].end}\n"
                            f"{messages['description']['ru']}: {desc_before} => {context.user_data['event'].description}\n"
                            f"{messages['author']['ru']}: {author}"
                            f"\n\n✏️ {messages['edit_alert']['uz']}: \n\n"
                            f"{messages['start']['uz']}: {start_before} => {context.user_data['event'].start}\n"
                            f"{messages['end']['uz']}: {end_before} => {context.user_data['event'].end}\n"
                            f"{messages['description']['uz']}: {desc_before} => {context.user_data['event'].description}\n"
                            f"{messages['author']['uz']}: {author}"
                            )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=context.user_data["chat_id"], text=f"{messages['canceled']['ru']}\n\t\t{messages['canceled']['uz']}\n\n📝 /reserve \n🖥 /display \n🗃 /my_events\n🗣 /feedback")
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
    conversation_timeout=datetime.timedelta(seconds=60)
)


my_events_handler = CommandHandler("my_events", my_events)
event_handler = CallbackQueryHandler(sel_event,  pattern='^my_event_')
del_handler = CallbackQueryHandler(del_event,  pattern='^del_event$')
