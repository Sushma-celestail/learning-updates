import hashlib

def generate_id(text):
    return hashlib.sha256(text.encode()).hexdigest()
