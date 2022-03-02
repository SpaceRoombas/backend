from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

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
    print (request.is_json)
    content = request.get_json()
    print(content)
    print(content['device'])
    print(content['value'])
    print(content['timestamp'])
    return content['timestamp']

app.run("localhost", 9000)