from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from functools import wraps

app = Flask('')
jwt = JWTManager(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_site(path):
    if path == 'tutorial':
        path = 'tutorial/index.html'
    elif path == '':
        path = 'index.html'
    return send_from_directory('site', path)

app.run(host="0.0.0.0", port=80)