import csv, os, inspect, sys, logging
from sqlalchemy import select

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import Car, Session, engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

local_session = Session(bind=engine)

with open('cars2.csv', newline='') as file:
    filereader = csv.reader(file, delimiter=';', quotechar='|')
    for row in filereader:
        statement = select(Car).filter(Car.plate == row[8])
        car = local_session.execute(statement).scalars().first()
        if car:
            car.owner_email=row[1],
            car.owner_name=row[2],
            car.owner_department=row[3],
            car.owner_cabinet=row[4],
            car.owner_phone=row[5],
            car.owner_username=row[6],
        else:
            car = Car(
                    owner_email=row[1],
                    owner_name=row[2],
                    owner_department=row[3],
                    owner_cabinet=row[4],
                    owner_phone=row[5],
                    owner_username=row[6],
                    model=row[7],
                    plate=row[8]
                )
        local_session.add(car)
        local_session.commit()
    local_session.close()

