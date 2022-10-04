import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, SmallInteger, String, DateTime, Boolean, ForeignKey, BigInteger

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

_db_host = os.environ['POSTGRES_HOST']
_db_username = os.environ['POSTGRES_USERNAME']
_db_password = os.environ['POSTGRES_PASSWORD']
_db_name = os.environ['POSTGRES_DB']
engine = create_engine(
    f'postgresql://{_db_username}:{_db_password}@{_db_host}:5432/{_db_name}', echo=True)

# Heroku
# DATABASE_URL = os.environ['DATABASE_URL']
# engine = create_engine('postgresql'+DATABASE_URL[8:], echo=True)

Base = declarative_base()
Session = sessionmaker()


class Group(Base):
    __tablename__ = 'group'

    id = Column(SmallInteger, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)  # tg group id
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
    is_archive = Column(Boolean, default=False, nullable=True)

    def __repr__(self):
        return f'<Event - start: {self.start}, end: {self.end}>'


class Car(Base):
    __tablename__ = 'car'

    id = Column(SmallInteger, primary_key=True)
    model = Column(String(55), nullable=False)
    plate = Column(String(8), nullable=False)
    owner_phone = Column(String(13), nullable=False)
    owner_name = Column(String(60), nullable=True)

    def __repr__(self):
        return f'<Car: plate - {self.plate}>'