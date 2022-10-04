import csv, os, inspect, sys, logging

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import Car, Session, engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

local_session = Session(bind=engine)

with open('cars.csv', newline='') as file:
    filereader = csv.reader(file, delimiter=',', quotechar='|')
    for row in filereader:
        car = Car(model=row[2].strip(), plate=row[3].strip(), owner_phone=row[4].strip())
        local_session.add(car)
        local_session.commit()
    local_session.close()

