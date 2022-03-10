import json
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import jwt
import datetime
import os
from functools import wraps
from sqlalchemy.exc import IntegrityError


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
        m = sha256(plaintext.encode('utf-8'))
        return m.hexdigest()


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
    return ""

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
        return("Username exceeds 15 characters"), 400
    if len(credentials.password) > 20:
        return("Password exceeds 20 characters"), 400
    
    newUser =  UserDbInfo(username=credentials.username, password=credentials.hashed_password, email=credentials.email)
    
    if not(credentials is None):
        newUser = UserDbInfo.query.filter_by(email=credentials.email).first()
        if newUser is None:
            newUser =  UserDbInfo(username=credentials.username, password=credentials.hashed_password, email=credentials.email)
            db.session.add(newUser)
            try:
                db.session.commit()
            except IntegrityError:
                return "Username already exists", 400
            return jsonify({"status":"registered"})
        else:
            return("User already exists"), 400
    return("Please insert a username and password"), 400
    

@app.route("/login", methods= ["POST"])
def authenticate_route():
    credentials = _safe_fetch_json_credentials(request.get_json())
    
    # TODO probably should return some sort of JSON error object here
    if credentials.username is None:
        return("Please insert your username"), 400
    if credentials.password is None:
        return("Please insert your password"), 400
    
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
            return("Login Information is Not Valid"), 403
    
    return("Login Information is Not Valid"), 403

@app.route("/auth", methods= ["GET"])
@token_required
def authorized():
    return jsonify({
        "message":"User is authorized."
    })

# Migrate database on server start
db.create_all()
db.session.commit()

app.run("localhost", 9000)