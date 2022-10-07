from sqlalchemy import select, and_, or_
from sqlalchemy.exc import MultipleResultsFound
from db.models import Group, Calendar, Event, Session, engine
from utils.translation import messages


class EventValidator:
    def __init__(self, start=None, end=None, description=None):
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
            err_message = f"{messages['duration_err_1']['ru']}\n{messages['duration_err_1']['uz']}"
            return False, err_message
        elif diff.total_seconds() > 28800:
            err_message = f"{messages['duration_err_2']['ru']}\n{messages['duration_err_2']['uz']}"
            return False, err_message
        return True, ''

    def collision_validation(self, edit=False, event_id=None):
        if edit and event_id:
            statement = select(Event).filter(or_(and_(Event.start < self.start, Event.end > self.start), and_(
            Event.start < self.end, Event.end > self.end))).filter(Event.id!=event_id)
        else:
            statement = select(Event).filter(or_(and_(Event.start < self.start, Event.end > self.start), and_(
            Event.start < self.end, Event.end > self.end)))

        events = self.session.execute(statement).scalars().all()
        if events:
            err_message = f"{messages['collision_err']['ru']} / {messages['collision_err']['uz']}: \n\n"
            for event in events:
                author = f"@{event.author_username}" if event.author_username else f"{event.author_firstname}"
                start_hour = event.start.hour if event.start.hour > 9 else f'0{event.start.hour}'
                start_minute = event.start.minute if event.start.minute > 9 else f'0{event.start.minute}'
                end_hour = event.end.hour if event.end.hour > 9 else f'0{event.end.hour}'
                end_minute = event.end.minute if event.end.minute > 9 else f'0{event.end.minute}'
                text = f'\t\t{event.start.day}.{event.start.month}.{event.start.year} {start_hour}:{start_minute} - {end_hour}:{end_minute} {event.description} [{author}] \n'
                err_message += text
            return False, err_message
        return True, ''

    def get_group(self):
        statement = select(Group)
        try:
            self.group = self.session.execute(
                statement).scalars().one_or_none()
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
            self.calendar = self.session.execute(
                statement).scalars().one_or_none()
        except MultipleResultsFound:
            err_message = 'Ошибка! больше 1го календаря в бд. обратитесь к админу'
            return False, err_message
        return True, self.calendar

    def create_event(self, user):
        calendar = self.get_calendar()
        if not calendar[0]:
            return calendar
        # try except
        self.event = Event(
            start=self.start,
            end=self.end,
            description=self.description,
            calendar_id=self.calendar.id,
            author_id=user.id,
            author_firstname=user.first_name,
            author_username=user.username if user.username else '',
        )
        self.session.add(self.event)
        self.session.commit()
        return True, ''

    def update_event(self, event):
        print(event)
        self.session.query(Event).filter(Event.id == event.id).update(
            {'description': self.description, 'start': self.start, 'end': self.end}, synchronize_session = False)
        self.session.commit()
        self.session.close()
        return True, ''
        #сохраняется только после перезапуска бота
