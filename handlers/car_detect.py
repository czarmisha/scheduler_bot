import os, requests, base64, logging
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters

from sqlalchemy import select, func
from dotenv import load_dotenv

from db.models import Group, Car, Session, engine
from utils.translation import messages

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

_TOKEN = os.environ['PLATE_RECOGNITION_TOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

local_session = Session(bind=engine)

def get_plate_numbers(file_path):
    logger.info('API is working')
    with open(file_path, "rb") as image:
            img_b64 = base64.b64encode(image.read())
            url = 'https://api.platerecognizer.com/v1/plate-reader/'
            data={
                'regions': 'uz',
                'upload': img_b64,
                "detection_rule": "strict",
            }
            headers = {
                "Authorization": f"Token {_TOKEN}"
            }
            response = requests.post(url=url, headers=headers, data=data)
            if response.ok:
                return (True, response.json()['results'])
            else:
                return (False, response.text)


def car_detect(update: Update, context: CallbackContext):
    logger.info('Start detection')
    statement = select(Group)
    group = local_session.execute(statement).scalars().first()
    author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    if author.status == 'left' or author.status == 'kicked' or not author.status:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
    else:
        logger.info('Downloading file')
        file = context.bot.getFile(update.message.photo[1].file_id)
        file_path = f'media/images/{update.effective_user.id}-{datetime.now().strftime("%Y%m%d%H%M")}.jpg'
        file.download(file_path)

        plate_nums = get_plate_numbers(file_path)
        if not plate_nums[0]:
            logger.info('I can\'t recognize the plate number')
            return #ignore if does not recognize plate on image
        # local_session.execute('CREATE EXTENSION pg_trgm;')
        # SET pg_trgm.similarity_threshold = 0.7;
        for num in plate_nums[1]:
            logger.info(f"FINDING CAR from db. Plate num: {num['plate']}")
            statement = select(Car).filter(func.similarity(Car.plate, num['plate'].upper()) > 0.4)
            car = local_session.execute(statement).scalars().first()
            if car:
                logger.info('DONE')
                message_text = f"Это возможно наша машина:\nНомер машины: {car.plate}\nНомер владельца: {car.owner_phone}"
                if hasattr(car, "owner_name"):
                    message_text += f"\nИмя владельца: {car.owner_name}"
                update.message.reply_text(message_text)
                break

    os.remove(file_path)

detect_handler = MessageHandler(Filters.photo, car_detect)
