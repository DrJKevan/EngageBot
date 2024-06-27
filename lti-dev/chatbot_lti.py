# chatbot_lti.py

import os
from flask import Flask, request, jsonify, redirect
import jwt
import logging
import streamlit as st
from datetime import datetime

# Mock LTI credentials
LTI_CONSUMER_KEY = "your_mock_consumer_key"  # Ensure this matches the LTI_CONSUMER_KEY in generate_jwt.py
LTI_CONSUMER_SECRET = "your_mock_consumer_secret"

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home</title>
    </head>
    <body>
        <h1>Flask Application is Running</h1>
    </body>
    </html>
    '''

@app.route('/lti_launch', methods=['POST'])
def lti_launch():
    # Verify the JWT token (mock implementation)
    token = request.form.get('id_token')
    logging.debug(f"Received token: {token}")
    try:
        decoded_token = jwt.decode(token, LTI_CONSUMER_SECRET, algorithms=["HS256"], audience=LTI_CONSUMER_KEY)
        logging.debug(f"Decoded token: {decoded_token}")
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        return jsonify({"error": "Token has expired"}), 400
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")
        return jsonify({"error": f"Invalid token: {e}"}), 400
 
    # Handle the LTI launch request
    st.session_state["lti_params"] = decoded_token
    return redirect("/chatbot")

@app.route('/chatbot')
def chatbot():
    # Existing Streamlit code to render the chatbot
    return "Chatbot UI"

if __name__ == '__main__':
    app.run(debug=True, port=8000)
