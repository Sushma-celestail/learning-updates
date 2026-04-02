##this file represents how the data is stored
#exactly like table structure
"""
class Voter:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age


class Vote:
    def __init__(self, id, candidate, voter_id):
        self.id = id
        self.candidate = candidate
        self.voter_id = voter_id
"""
## Convert db_models.py to SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    candidate = Column(String)
    voter_id = Column(Integer, ForeignKey("voters.id"))