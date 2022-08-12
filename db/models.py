import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, SmallInteger, String, DateTime, Boolean, ForeignKey

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db_host = os.environ['POSTGRES_HOST']
db_username = os.environ['POSTGRES_USERNAME']
db_password = os.environ['POSTGRES_PASSWORD']
db_name = os.environ['POSTGRES_DB']
engine = create_engine(
    f'postgresql://{db_username}:{db_password}@{db_host}:5432/{db_name}', echo=True)

# Heroku
# DATABASE_URL = os.environ['DATABASE_URL']
# engine = create_engine('postgresql'+DATABASE_URL[8:], echo=True)

Base = declarative_base()
Session = sessionmaker()


class Group(Base):
    __tablename__ = 'group'

    id = Column(SmallInteger, primary_key=True)
    tg_id = Column(Integer, nullable=False)  # tg group id
    name = Column(String(50), nullable=False)
    calendar = relationship("Calendar", back_populates="group", uselist=False)

    def __repr__(self):
        return f'<Telegram group - {self.name}, id: {self.id}>'


class Calendar(Base):
    __tablename__ = 'calendar'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    group_id = Column(Integer, ForeignKey("group.id"))
    group = relationship("Group", back_populates="calendar")
    event = relationship("Event", back_populates="calendar")

    def __repr__(self):
        return f'<Calendar - name: {self.name}, group id: {self.group_id}>'


class Event(Base):
    __tablename__ = 'events'

    id = Column(SmallInteger, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)
    calendar_id = Column(Integer, ForeignKey("calendar.id"))
    calendar = relationship("Calendar", back_populates="event")
    author_id = Column(Integer, nullable=False)
    author_firstname = Column(String(255), nullable=False)
    author_username = Column(String(255), nullable=True)

    def __repr__(self):
        return f'<Event - start: {self.start}, end: {self.end}>'
