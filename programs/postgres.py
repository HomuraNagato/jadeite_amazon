from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db = create_engine('postgresql://postgres:Nagato13!#@localhost:5432/pensieve', echo=False)
base = declarative_base()

class Film(base):  
    __tablename__ = 'films2'

    title = Column(String, primary_key=True)
    director = Column(String)
    year = Column(String)

Session = sessionmaker(db)  
session = Session()

base.metadata.create_all(db)
