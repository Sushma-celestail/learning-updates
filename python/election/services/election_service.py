"""
from repositories.election_repository import ElectionRepository
#this file contains the logic 
#its checking voter exists or not 
#and if voter not exists its generating new IDs
repo = ElectionRepository()

class ElectionService:

    def create_voter(self, voter_data):
        data = repo.load_data()
        voter_id = len(data["voters"]) + 1

        voter = {
            "id": voter_id,
            "name": voter_data.name,
            "age": voter_data.age
        }

        return repo.add_voter(voter)

    def cast_vote(self, vote_data):
        data = repo.load_data()

        # check voter exists
        voter = next((v for v in data["voters"] if v["id"] == vote_data.voter_id), None)
        if not voter:
            raise Exception("Voter not found")

        vote_id = len(data["votes"]) + 1

        vote = {
            "id": vote_id,
            "candidate": vote_data.candidate,
            "voter_id": vote_data.voter_id
        }

        return repo.add_vote(vote)

    def get_votes(self):
        return repo.get_all_votes()

        """

from repositories.election_repository import ElectionRepository

repo = ElectionRepository()

class ElectionService:

    def create_voter(self, voter_data):
        return repo.create_voter(voter_data)

    def cast_vote(self, vote_data):
        return repo.create_vote(vote_data)

    def get_votes(self):
        return repo.get_all_votes()