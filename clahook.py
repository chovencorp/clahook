# Copyright @ 2016 Choven Corp.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# enabling imports from hooks folder
import sys
from config import  PULL_ACTIONS, PORT

GITHUB_EVENT_HEADER = "X-GitHub-Event"
GITHUB_PULL_REQUEST_EVENT = "pull_request"
PING_EVENT = "ping"

from validator import validate_pull_request

from flask import Flask, request,jsonify
from os import environ

app = Flask(__name__)

# routing method of flask app
@app.route("/",methods=["POST"])
def index():
    if is_ping_event(request):
        return handle_ping_event(request)
    elif can_handle_request(request):
        return handle_request(request)
    else:
        return "Server can't handle this request", 501

def is_ping_event(rq):
    try:
        event = rq.headers.get(GITHUB_EVENT_HEADER)
        return event == PING_EVENT
    except:
        return False

def handle_ping_event(rq):
        return "ping", 200

def handle_request(rq):
    """Return response"""
    try:
        resp = jsonify(validate_pull_request(rq.get_json()))
        return resp, 200
    except Exception as e:
        return str(e), 500


def can_handle_request(rq):
    """ 
    Checks if current request and payload 
    belong to pull request and action is in PULL_ACTIONS
    """
    try:
        event = rq.headers.get(GITHUB_EVENT_HEADER)
        return event == GITHUB_PULL_REQUEST_EVENT and rq.get_json()["action"] in PULL_ACTIONS
    except:
        return False

if __name__=="__main__":
     app.run(host='0.0.0.0', port=PORT, debug=True)

