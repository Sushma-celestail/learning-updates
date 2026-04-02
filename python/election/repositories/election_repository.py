#especially used for data access
#Handles file/database operations
#here dont add business logic
"""
import json
import os

FILE = "data/election.json"

class ElectionRepository:

    def load_data(self):
        if not os.path.exists(FILE):
            return {"voters": [], "votes": []}
        
        with open(FILE, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(FILE, "w") as f:
            json.dump(data, f, indent=4)

    def add_voter(self, voter):
        data = self.load_data()
        data["voters"].append(voter)
        self.save_data(data)
        return voter

    def add_vote(self, vote):
        data = self.load_data()
        data["votes"].append(vote)
        self.save_data(data)
        return vote

    def get_all_votes(self):
        return self.load_data()["votes"]

"""

from database import SessionLocal
from models.db_models import Voter, Vote

class ElectionRepository:

    def create_voter(self, voter_data):
        db = SessionLocal()

        voter = Voter(
            name=voter_data.name,
            age=voter_data.age
        )

        db.add(voter)
        db.commit()
        db.refresh(voter)
        db.close()

        return voter

    def create_vote(self, vote_data):
        db = SessionLocal()

        vote = Vote(
            candidate=vote_data.candidate,
            voter_id=vote_data.voter_id
        )

        db.add(vote)
        db.commit()
        db.refresh(vote)
        db.close()

        return vote

    def get_all_votes(self):
        db = SessionLocal()
        votes = db.query(Vote).all()
        db.close()
        return votes