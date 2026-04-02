#comes under API LAYER

#it only handles HTTP requests
#calss the service layer 

from fastapi import APIRouter
from models.schemas import VoterCreate,VoteCreate
from services.election_service import ElectionService



#now creating the objects used to define API endpoints like /voters,/vote
#same creates service object to call create_voter(),vote(),get_votes()

router=APIRouter()
service=ElectionService()

#creating voter API and This is post API endpoint    
#here its connected to the voters creation end points 
#create new voter
@router.post("/voters") 
def create_voter(voter: VoterCreate):
    #api requesting body must match VoterCreate schema
    #then api auto parses JSON
    #validates data
    return service.create_voter(voter)
@router.post("/vote")
def cast_vote(vote: VoteCreate):
    return service.cast_vote(vote)

@router.get("/votes")
def get_votes():
    return service.get_votes()
"""
POST /voters
   ↓
create_voter()
   ↓
VoterCreate (validation)
   ↓
ElectionService.create_voter()
   ↓
Database
   ↓
Response
"""