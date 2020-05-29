# for variables and functions that help all requests
import os
import json
from flask import make_response, jsonify


# with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elasticBDConfig.json")) as f:
#     config = json.load(f)
#
# username = config["username"]
# password = config["password"]
#
#
# address = config["elasticAddress"]
# search_address = os.path.join(address, '_search')
# doc_address = os.path.join(address, '_doc')
# update_address = os.path.join(address, '_update')


def format_response(response):
    """
    turns a 'requests' response into appropriate response for api
    :param response: 'requests' package response
    :return: 'flask' response type
    """
    response_json = jsonify(response.json())
    response_code = response.status_code
    return make_response(response_json, response_code)
