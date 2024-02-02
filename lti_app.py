from flask import Flask, request, jsonify, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
import os
import jwt

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Setup OAuth 2.0 Client
oauth = OAuth(app)
lti_tool = oauth.register(
    name='lti',
    client_id='your_client_id',
    client_secret='your_client_secret',
    authorize_url='https://example.com/authorize',
    access_token_url='https://example.com/token',
    client_kwargs={
        'scope': 'openid',
        'response_type': 'id_token',
        'response_mode': 'form_post',
        'token_endpoint_auth_method': 'client_secret_post'
    },
)

@app.route('/lti_launch', methods=['POST'])
def lti_launch():
    # Extract ID Token from request
    id_token = request.form.get('id_token')
    # Decode ID Token here and verify
    # For demonstration, let's pretend we have decoded it and extracted info
    user_info = {
        "name": "John Doe",
        "role": "Instructor",  # This would be extracted from the decoded ID token
    }
    # Store user info in session or handle as needed
    session['user_info'] = user_info
    return redirect(url_for('display_role'))

@app.route('/display_role')
def display_role():
    user_info = session.get('user_info', {})
    return jsonify(user_info)

if __name__ == '__main__':
    app.run(debug=True)
    decoded_token = jwt.decode(id_token, algorithms=['RS256'], options={"verify_signature": False})
    print(decoded_token)