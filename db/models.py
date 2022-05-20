import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, SmallInteger, String, DateTime, Boolean, ForeignKey

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

engine = create_engine(f'postgresql://{db_username}:{db_password}@localhost:5432/{db_name}', echo=True)

Base = declarative_base()
Session = sessionmaker()


class Group(Base):
    __tablename__ = 'group'

    id = Column(SmallInteger, primary_key=True)
    tg_id = Column(Integer, nullable=False) # tg group id
    name = Column(String(50), nullable=False)
    # member_count = Column(Integer) # need positive small integer
    calendar = relationship("Calendar", back_populates="group", uselist=False)
    # user = relationship("User", back_populates="group")
    #admins

    def __repr__(self):
        return f'<Telegram group - {self.name}, id: {self.id}>'


class Calendar(Base):
    __tablename__ = 'calendar'
    
    id = Column(SmallInteger, primary_key=True)# need positive small integer
    name = Column(String(50), nullable=False)
    group_id = Column(Integer, ForeignKey("group.id"))
    group = relationship("Group", back_populates="calendar")
    event = relationship("Event", back_populates="calendar")

    def __repr__(self):
        return f'<Calendar - name: {self.name}, group id: {self.group_id}>'


# class User(Base):
#     __tablename__ = 'user'
    
#     id = Column(SmallInteger, primary_key=True)
#     tg_id = Column(Integer, nullable=False) # tg user id
#     is_admin = Column(Boolean, nullable=False)
#     is_blocked = Column(Boolean, nullable=False)
#     group_id = Column(Integer, ForeignKey("group.id"))
#     group = relationship("Group", back_populates="user")
#     event = relationship("Event", back_populates="user")


#     def __repr__(self):
#         return f'<Telegram user - tg id: {self.id}, group id{self.group_id}>'
    

class Event(Base):
    __tablename__ = 'events'

    id = Column(SmallInteger, primary_key=True)# need positive small integer
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    description = Column(String(255), nullable=False)
    # is_repeated = Column(Boolean, nullable=False)
    calendar_id = Column(Integer, ForeignKey("calendar.id"))
    # user_id = Column(Integer, ForeignKey("user.id"))
    user_tg_id = Column(Integer, nullable=False)
    calendar = relationship("Calendar", back_populates="event")
    # user = relationship("User", back_populates="event")

    def __repr__(self):
        return f'<Event - start: {self.start}, end: {self.end}>'

    