from db_models import Voter
from sqlalchemy import Column, Integer, String, ForeignKey


class refer(Voter):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
