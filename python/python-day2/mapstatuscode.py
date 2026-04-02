"""
### Q20. Map HTTP Status Codes to Categories 

Topics: List Comprehension, HTTP Status Codes 

Problem Statement: 

Given a list of HTTP response codes, use a list comprehension to classify each as success, client_error, or server_error. 

Input: 

codes = [200, 201, 404, 500, 301, 403, 502, 204] 

Output: 

[(200, 'success'), (201, 'success'), (404, 'client_error'), 

 (500, 'server_error'), (301, 'redirect'), (403, 'client_error'), 

 (502, 'server_error'), (204, 'success')] 

Constraints: 

2xx → success, 3xx → redirect, 4xx → client_error, 5xx → server_error 

Use a single list comprehension with a helper function or inline conditional 

"""
 

codes = [200, 201, 404, 500, 301, 403, 502, 204]

def classify(code):
    if 200 <= code < 300: return "success"
    if 300 <= code < 400: return "redirect"
    if 400 <= code < 500: return "client_error"
    return "server_error"

result = [(code, classify(code)) for code in codes]
print(result)
# [(200, 'success'), (201, 'success'), (404, 'client_error'),
#  (500, 'server_error'), (301, 'redirect'), (403, 'client_error'),
#  (502, 'server_error'), (204, 'success')]