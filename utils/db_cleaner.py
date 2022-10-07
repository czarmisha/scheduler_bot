import logging
import os
import datetime
import inspect
import sys
# from crontab import CronTab

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import Event, Session, engine

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'db_cleaner.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

local_session = Session(bind=engine)
TZ = datetime.timezone(datetime.timedelta(hours=5), 'Uzbekistan/UTC+5')

# cron = CronTab(user='uzinfocom')
# job = cron.new(command='echo hello_world')
# job.minute.every(1)
# cron.write()

def clear_db():
    logger.info('!*!*!*!*!* cron job !*!*!*!*!**!')
    today = datetime.datetime.now(TZ)
    overdue_events = local_session.query(Event).filter(Event.end < today)
    if overdue_events:
        for event in overdue_events:    
            logger.info(f'arhiving {event}')
            event.is_archive = True
            local_session.commit()
    else:
        logger.info('no events to archive')

if __name__ == '__main__':
    clear_db()
