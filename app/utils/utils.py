import random
import string
import uuid

def generate_username():
    return "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_verification_code():
    return str(uuid.uuid4())