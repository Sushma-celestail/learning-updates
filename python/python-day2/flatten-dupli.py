"""
### Q19. Flatten and Deduplicate Tags 

Topics: List Comprehension, Sets 

Problem Statement: 

Given a list of articles (each with a list of tags), extract all unique tags sorted alphabetically using comprehensions and sets. 

Input: 

articles = [ 

  {"title": "AI Intro", "tags": ["python", "ml", "ai"]}, 

  {"title": "Web Dev", "tags": ["python", "fastapi", "api"]}, 

  {"title": "Data 101", "tags": ["ml", "pandas", "python"]}, 

] 

Output: 

['ai', 'api', 'fastapi', 'ml', 'pandas', 'python'] 

Constraints: 

Use set comprehension or list comprehension with set conversion 

Output must be sorted alphabetically 

Solve in no more than 2 lines of code 

 
"""


articles = [
    {"title": "AI Intro",  "tags": ["python", "ml", "ai"]},
    {"title": "Web Dev",   "tags": ["python", "fastapi", "api"]},
    {"title": "Data 101",  "tags": ["ml", "pandas", "python"]},
]

unique_tags = sorted({tag for article in articles for tag in article["tags"]})
print(unique_tags)
# ['ai', 'api', 'fastapi', 'ml', 'pandas', 'python']