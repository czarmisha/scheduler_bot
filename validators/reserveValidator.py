from sqlalchemy import select, and_, or_
from sqlalchemy.exc import MultipleResultsFound
from db.models import Group, Calendar, Event, Session, engine


class ReserveValidator:
    def __init__(self, start, end, description):
        self.start = start
        self.end = end
        self.description = description
        self.session = Session(bind=engine)

    def duration_validation(self):
        """
        duration of the event must be above then 5 minutes and below then 8 hours
        """
        diff = self.end - self.start
        if diff.total_seconds() < 300:
            err_message = 'Событие не может длиться меньше 5минут'
            return False, err_message
        elif diff.total_seconds() > 28800:
            err_message = 'Событие не может длиться больше 8 часов'
            return False, err_message
        return True, ''

    def collision_validation(self):
        statement = select(Event).filter(or_(and_(Event.start < self.start, Event.end > self.start), and_(
        Event.start < self.end, Event.end > self.end)))
        events = self.session.execute(statement).all()
        if events:
            err_message = 'Событие на это время уже запланировано. \n\n /reserve \n /display'
            return False, err_message
        return True, ''

    def get_group(self):
        statement = select(Group)
        try:
            self.group = self.session.execute(statement).scalars().one_or_none()
        except MultipleResultsFound:
            err_message = 'Ошибка! больше 1й группы в бд. обратитесь к админу'
            return False, err_message
        return True, self.group

    def get_calendar(self):
        group = self.get_group()
        if not group[0]:
            return group

        statement = select(Calendar).where(Calendar.group_id == self.group.id)
        try:
            self.calendar = self.session.execute(statement).scalars().one_or_none()
        except MultipleResultsFound:
            err_message = 'Ошибка! больше 1го календаря в бд. обратитесь к админу'
            return False, err_message
        return True, self.calendar

    def create_event(self):
        calendar = self.get_calendar()
        if not calendar[0]:
            return calendar
        self.event = Event(
            start=self.start,
            end=self.end,
            description=self.description,
            calendar_id=self.calendar.id,
            is_repeated=False
        )
        self.session.add(self.event)
        self.session.commit()
        return True, ''
        