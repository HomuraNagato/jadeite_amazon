"""
Intro to SQLAlchemy
https://www.compose.com/articles/using-postgresql-through-sqlalchemy/

Advanced SQLAlchemy
https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
https://hackersandslackers.com/pythonic-database-management-with-sqlalchemy/
"""

'''
Low level interaction with postgresql database
'''
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:Nagato13!#@localhost:5432/pensieve', echo=False)


# Create

engine.execute("DROP TABLE IF EXISTS films")
engine.execute("CREATE TABLE IF NOT EXISTS films (title text, director text, year text)")
engine.execute("INSERT INTO films (title, director, year) VALUES ('Doctor Strange', 'Scott Derrickson', '2016')")

# Read
result_set = engine.execute("SELECT * FROM films")
for r in result_set:
    print(r)
        


'''
High level interaction with postgresql database
'''
    
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

# Create 
doctor_strange = Film(title="Doctor Strange", director="Scott Derrickson", year="2016")  
session.add(doctor_strange)  
session.commit()

# Read
films = session.query(Film)  
for film in films:  
    print(film.title)

# Update
doctor_strange.title = "Some2016Film"  
session.commit()

# Delete
session.delete(doctor_strange)  
session.commit()
