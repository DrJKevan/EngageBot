# minimal_flask_app.py

from flask import Flask

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
