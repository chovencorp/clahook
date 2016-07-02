# Copyright @ 2016 Choven Corp.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from config import (PERSONAL_ACCESS_TOKEN, CLA_PATTERN,
    CONTRIBUTORS_FILE_NAME, FAILURE_MESSAGE, SUCCESS_MESSAGE, CONTEXT_NAME)

import requests
import base64
import json


def file_contains_agreement(file_content, name):
    """ Check if file contains username """
    substring = CLA_PATTERN.replace("{username}", name)
    return file_content.find(substring) != -1

def validate_pull_request(payload):
    pull_url = payload["pull_request"]["url"]
    pull_status_url = payload["pull_request"]["statuses_url"]
    username = payload["pull_request"]["user"]["login"]
    head_commit = payload["pull_request"]["head"]["sha"]

    contents_url = payload["pull_request"]["head"]["repo"]["contents_url"]

    contributors_url = contents_url.replace("{+path}", CONTRIBUTORS_FILE_NAME)

    # Creating authorized session using personal access token from github
    session = requests.Session();
    session.headers.update({"Authorization":"token %s" % PERSONAL_ACCESS_TOKEN})

    try:
        # get contributor file base64 contents
        contrib_file_json = session.get(contributors_url, params={'ref': head_commit}).json()["content"]

        # decoding base64 content of contributors file path
        contrib_file_content = base64.b64decode(contrib_file_json)

        # checking of user string in contributors file
        if not file_contains_agreement(contrib_file_content, username):
            # set failure status for not validated
            r = session.post(pull_status_url,json={"state":"failure","description": FAILURE_MESSAGE,"context":CONTEXT_NAME})
            return r.json() # return status response
    except Exception as e:
            # set failure status for file not found exception
            r = session.post(pull_status_url,json={"state":"failure","description": FAILURE_MESSAGE,"context":CONTEXT_NAME})
            return r.json() #return status response

    # if no erros occured set status to success
    r = session.post(pull_status_url,json={"state":"success","description":SUCCESS_MESSAGE,"context":CONTEXT_NAME})
    status = r.json()
    return status # return status response