import logging
import os
import inspect
import sys
from sqlalchemy import select

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import Event, Group, Calendar, Session, engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

local_session = Session(bind=engine)

def clean(group_id):
    logger.info('!*!*!*!*!* starting clean db after remove bot from the group !*!*!*!*!**!')

    statement = select(Group).filter_by(tg_id=group_id)
    group = local_session.execute(statement).scalars().one()
    logger.info('!*!*!*!*!* Group is find !*!*!*!*!* ') if group else logger.info('!*!*!*!*!* Group do not find !*!*!*!*!* ')

    statement = select(Calendar).filter_by(group_id=group.id)
    calendar = local_session.execute(statement).scalars().one()
    logger.info('!*!*!*!*!* Calendar is find !*!*!*!*!* ') if calendar else logger.info('!*!*!*!*!* Calendar do not find !*!*!*!*!* ')

    statement = select(Event).filter_by(calendar_id=calendar.id)
    events = local_session.execute(statement).scalars().all()
    logger.info(f'!*!*!*!*!* Deleting events !*!*!*!*!* ')
    for event in events:
        logger.info(f'!*!*!*!*!* Deleting event \"{event}\" from db !*!*!*!*!* ')
        local_session.delete(event)
    
    logger.info(f'!*!*!*!*!* Deleting calendar \"{calendar.name}\" from db !*!*!*!*!* ')
    local_session.delete(calendar)

    logger.info(f'!*!*!*!*!* Deleting group \"{group.name}\" from db !*!*!*!*!* ')
    local_session.delete(group)
    local_session.commit()

    
