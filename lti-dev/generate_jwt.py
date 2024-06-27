# generate_jwt.py

import jwt
import time

LTI_CONSUMER_SECRET = "your_mock_consumer_secret"
LTI_CONSUMER_KEY = "your_mock_consumer_key"  # Ensure this matches the LTI_CONSUMER_KEY in chatbot_lti.py

# Set issued at time to now and expiration time to 1 hour in the future
iat = int(time.time())
exp = iat + 3600  # Token valid for 1 hour

payload = {
    "iss": "https://d2l.arizona.edu",
    "aud": LTI_CONSUMER_KEY,
    "sub": "user_id",
    "iat": iat,
    "exp": exp,
    "nonce": "nonce",
    "name": "John Doe",
    "given_name": "John",
    "family_name": "Doe",
    "email": "john.doe@example.com"
}

token = jwt.encode(payload, LTI_CONSUMER_SECRET, algorithm="HS256")
print(token)
