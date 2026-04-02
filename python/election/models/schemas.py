from pydantic import BaseModel
#Validates request data
#Controls API input/output
class VoterCreate(BaseModel):
    name:str
    age:int

class VoteCreate(BaseModel):
    candidate: str
    voter_id:int

class VoteResponse(BaseModel):
    id:int
    candidate:str
    voter_id :int