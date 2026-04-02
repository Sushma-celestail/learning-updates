##json validation 
import json
def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False
print(is_valid_json('{"name":"sushma",:20}'))

import json 
def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False
print(is_valid_json('{"name":"sushma","age":30}'))