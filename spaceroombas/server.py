from flask import Flask
from flask import jsonify
from flask import request
from hashlib import sha256

app = Flask(__name__)


# Various models
class UserModel():
    def __init__(self, user = None, pw = None) -> None:
        self.username = user
        self.password = pw
        self.hashed_password = self.hash(self.password)
    def hash(plaintext):
        if plaintext is None:
            return
        m = sha256()
        m.update(plaintext.encode('utf-8'))
        return m.digest()

def _safe_fetch_json_credentials(json_req):
    username = None
    password = None
    req_content = request.get_json()
    try:
        username = req_content['username']
        password = req_content['password']
    except TypeError:
        return
    if not ((username is None) and (password is None)):
        return UserModel(username, password)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/api/v1', methods=["GET"])
def info_view():
    """List of routes for this API."""
    output = {
            "Server": "placeholder.class",
            "IP": "IP.class"

    }
    return output
    

@app.route("/post", methods = ['POST'])
def postJson():
    try:
        print (request.is_json)
        content = request.get_json()
        print(content)
        print(content['device'])
        print(content['value'])
        print(content['timestamp'])
        return content['timestamp']
    except TypeError:
        return ""

@app.route("/register", methods= ["POST"])
def register_user():
    credentials = _safe_fetch_json_credentials(request.get_json())

    if credentials is None:
        return "Bad"

    print("Test: user: %s password: %s" % (credentials.username, credentials.password))

@app.route("/login", methods= ["POST"])
def authenticate_route():
    credentials = _safe_fetch_json_credentials(request.get_json())

    if credentials is None:
        return "Bad"
    
    print("Test: user: %s password: %s" % (credentials.username, credentials.password))

app.run("localhost", 9000)