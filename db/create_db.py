from models import engine, Base

Base.metadata.create_all(engine) # create a database
