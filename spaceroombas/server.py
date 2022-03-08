from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import jwt
import datetime
import os
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userInfo.db'
db = SQLAlchemy(app)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message':'Token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({
                'message' : 'Token is invalid'
            })
        return func(*args, **kwargs)
    return decorated

# Various models
class UserDbInfo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(15), nullable = False, unique = True)
    password = db.Column(db.String(64), nullable = False)
    email = db.Column(db.String(255), nullable = False, unique = True)
    
    def __repr__(self):
        return '<User %r>' % self.username

class UserModel():
    def __init__(self, user = None, pw = None, email = None) -> None:
        self.username = user
        self.password = pw
        self.email = email
        self.hashed_password = self.hash(self.password)
    def hash(self, plaintext):
        if plaintext is None:
            return
        m = sha256()
        m.update(plaintext.encode('utf-8'))
        return m.digest()


def _safe_fetch_json_credentials(json_req):
    username = None
    password = None
    email = None
    req_content = request.get_json()
    try:
        username = req_content['username']
        password = req_content['password']
        email = req_content['email']
    except TypeError:
        return
    if not ((username is None) and (password is None) and (email is None)):
        return UserModel(username, password, email)

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
   
    if len(credentials.username) > 15:
        return("Username exceeds 15 characters")
    if len(credentials.password) > 20:
        return("Password exceeds 20 characters")
    
    newUser =  UserDbInfo(username=credentials.username, password=credentials.hashed_password, email=credentials.email)
    
    if not(credentials is None):
        newUser = UserDbInfo.query.filter_by(email=credentials.email).first()
        if newUser is None:
            newUser =  UserDbInfo(username=credentials.username, password=credentials.hashed_password, email=credentials.email)
            db.session.add(newUser)
            db.session.commit()
        else:
            return("User already exists")
    return("Please insert a username and password")
    

@app.route("/login", methods= ["POST"])
def authenticate_route():
    credentials = _safe_fetch_json_credentials(request.get_json())
    
    if credentials.username is None:
        return("Please insert your username")
    if credentials.password is None:
        return("Please insert your password")
    
    userLogin = UserDbInfo.query.filter_by(username=credentials.username).first()

    if userLogin:
        if userLogin.password == credentials.hashed_password:
            token = jwt.encode({
                'user':userLogin.username,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
            },
                app.config['SECRET_KEY'])
            return jsonify({'token': token})
        else:
            return("Login Information is Not Valid")
    
    return("Login Information is Not Valid")

@app.route("/auth", methods= ["GET"])
@token_required
def authorized():
    return jsonify({
        "message":"User is authorized."
    })

app.run("localhost", 9000)