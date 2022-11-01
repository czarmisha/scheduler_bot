import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler

from db.models import Session, engine


local_session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def repair(update: Update, context: CallbackContext):
    logger.info('!!!!!!!', update)
    logger.info('!!!!!!!', update.effective_chat.id)

repair_handler = CommandHandler('repair', repair)
