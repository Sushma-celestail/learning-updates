"""
### Q18. Filter and Transform with Comprehension 

Topics: Dictionary Comprehension 

Problem Statement: 

Given a list of user dictionaries, use a single dictionary comprehension to create a mapping of username → email for users who are active and aged 18+. 

Input: 

users = [ 

  {"username": "alice", "email": "a@b.com", "age": 25, "active": True}, 

  {"username": "bob", "email": "b@b.com", "age": 17, "active": True}, 

  {"username": "carol", "email": "c@b.com", "age": 30, "active": False}, 

  {"username": "dave", "email": "d@b.com", "age": 22, "active": True}, 

] 

Output: 

{'alice': 'a@b.com', 'dave': 'd@b.com'} 

Constraints: 

Use a single dictionary comprehension (one line) 

Both conditions (active AND age >= 18) must be met 

 
"""
users = [
    {"username": "alice", "email": "a@b.com", "age": 25, "active": True},
    {"username": "bob", "email": "b@b.com", "age": 17, "active": True},
    {"username": "carol", "email": "c@b.com", "age": 30, "active": False},
    {"username": "dave", "email": "d@b.com", "age": 22, "active": True},
]

result = {u["username"]: u["email"] for u in users if u["active"] and u["age"] >= 18}

print(result)