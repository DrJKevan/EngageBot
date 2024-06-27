# mock_lti_launch.py

import jwt
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock LTI credentials
LTI_CONSUMER_KEY = "your_mock_consumer_key"
LTI_CONSUMER_SECRET = "your_mock_consumer_secret"

@app.route('/lti_launch', methods=['POST'])
def lti_launch():
    # Verify the JWT token (mock implementation)
    token = request.form.get('id_token')
    try:
        decoded_token = jwt.decode(token, LTI_CONSUMER_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 400
    
    # Handle the LTI launch request
    return jsonify({"message": "LTI Launch Successful", "token": decoded_token})

if __name__ == '__main__':
    app.run(debug=True)
