from flask import Flask, flash
from flask import jsonify
from flask import request
from flask import url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import jwt
import datetime
import os
from functools import wraps
from sqlalchemy import true
from sqlalchemy.exc import IntegrityError
from flask_mailing import Mail, Message
from forms import PasswordResetForm
from subprocess import Popen
from sys import executable, stdout
from pathlib import Path
import logging

LOGLEVEL = os.environ.get('LOGGING', 'WARNING').upper()
logging.basicConfig(
    level=LOGLEVEL, 
    handlers=[logging.StreamHandler(stdout)],
    format='%(levelname)s: -- %(message)s'
)

class MatchSession():
    
    def __init__(self, port:int, userids):
        self.players: list[str] = []
        self.port: int = port
        self.players += self.__ensure_string_list(userids)
        self.session_process: Popen = None

    def __ensure_string_list(self, it):
        objType = type(it)
        if objType != list and objType == str:
            return [it]
        return it

    def create_process(self):
        spaceroombas_path = Path(__file__).parent.resolve()
        server_path = Path(str(spaceroombas_path), 'session_server.py')
        envvars = dict(os.environ.items())
        envvars['PORT'] = str(self.port)

        args = [str(executable), str(server_path)]
        self.session_process = Popen(args, env=envvars)
    
    def is_alive(self):
        return self.session_process.poll() is None

    def stop(self):
        if self.session_process.is_alive():
            self.session_process.terminate()

class MatchManager():

    def __init__(self, baseport):
        self.matches:dict[MatchSession] = {}
        self.baseport = baseport
    
    def create_match(self, userid):
        avail_port = self.find_avail_port()
        match = MatchSession(avail_port, userid)

        self.matches[avail_port] = match

        match.create_process()

    def find_avail_port(self):
        ports = self.matches.keys()
        currPort = self.baseport

        # Terrible, but search for available ports
        while currPort in ports:
            currPort = currPort + 1
        
        return currPort


    def destroy_match(self, match_port):
        match: MatchSession = None
        try:
            match = self.matches[match_port]
        except KeyError:
            logging.error("Match doesnt exist")
            return

        match.stop()
        self.matches.pop(match_port, None)

match_manager = MatchManager(9001) # This will start all game sessions at port 9001, and going up

mail = Mail()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userInfo.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_ADDRESS')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail.init_app(app)

db = SQLAlchemy(app)

def token_required(func): #May not be needed, depending on what else we use tokens for
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
    
    def verifyToken(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            userId = data.get('user')
        except:
            return None
        return UserDbInfo.query.get(userId) #Get ID of user who submitted token, and return the user
    
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

def _safe_fetch_json_email(json_req):
    email = None
    req_content = request.get_json()
    try:
        email = req_content['email']
    except KeyError:
        return
    if not email is None:
        return(email)

def _safe_fetch_json_credentials(json_req):
    username = None
    password = None
    email = None
    req_content = request.get_json()
    try:
        username = req_content['username']
        password = req_content['password']
        email = req_content['email']
    except KeyError:
        return
    if not ((username is None) and (password is None) and (email is None)):
        return UserModel(username, password, email)

@app.route("/create_match")
def create_match():
    match_manager.create_match("ARoomba")
    return "started",200

@app.route('/api/v1', methods=["GET"])
def info_view():
    """List of routes for this API."""
    output = {
            "Server": "placeholder.class",
            "IP": "IP.class"

    }
    return output

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
                'user':userLogin.id,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
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
    
@app.route("/forgotPass", methods = ["POST"]) #This method takes in the user email from Unity. Upon submit, user is sent email
async def forgotPassword():
    email = _safe_fetch_json_email(request.get_json())
    user = UserDbInfo.query.filter_by(email=email).first()
    if user:
        token = jwt.encode({
                'user':user.id,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
            },
                app.config['SECRET_KEY'])
        
        msg = Message(
            subject = "Password Reset",
            recipients = [user.email],
            body = f'''Click the link below to reset your password:\n{url_for('showResetForm', token=token,_external=true)}\nLink expires after 10 minutes'''
            
        )
    
        await mail.send_message(msg)
        return("Password Reset sent"), 200
    else:
        return("Email not found in the database"), 403


@app.route("/resetPassForm/<token>", methods = ["GET", "POST"]) #This form will open once the user clicks the link in the sent email
def showResetForm(token):
    form = PasswordResetForm()
    user = UserDbInfo.verifyToken(token) #Check to see if token is associated with the user
    if user is None:
        flash("Password reset link is expired. Please try again.")
        return render_template('expired.html')
    if form.validate_on_submit(): #Once user hits submit, change their password to what they input
        hashpw = UserModel(None, form.password.data, None).hashed_password #Hash password before storing in database
        user.password = hashpw
        db.session.commit()
        flash("Your password was successfully changed.")
    elif form.submit(): #If passwords do not match on submit, flash an error message
        if form.password.data != form.confirmPassword.data:
            flash("Passwords must match")
    return render_template('index.html', form=form)    
    

# Migrate database on server start
db.create_all()
db.session.commit()

app.run("localhost", 9000)