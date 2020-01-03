# TODO add logging
import os
import requests
from src.api.settings import api
from src.api.models.token_models import *
from src.api.helpers import *
from flask_restplus import Resource
from flask import request


ns = api.namespace('token', description='Operations related to creating and updating tokens')


@ns.route('/')
class UpdateTokens(Resource):

    @api.response(201, "Search type successfully created")
    @api.expect(token_model_id)
    def post(self):
        """
        creates new music with tags
        """
        data = request.json
        response = requests.post(doc_address, auth=(username, password), json=data)
        return format_response(response)


@ns.route('/<string:id>')
@api.response(404, "id or update_list not found")
class UpdateId(Resource):

    @api.response(200, "Search type successfully updated")
    @api.expect(token_model)
    def put(self, id):
        """
        overwrites existing search instance
        :param id: id of search instance want to change
        :return: standard response
        """
        data = request.json
        response = requests.put(os.path.join(doc_address, id), auth=(username, password), json=data)
        return format_response(response)

    @api.response(200, "Search type successfully deleted")
    def delete(self, id):
        """
        deletes existing search instance
        :param id: id of search instance
        :return: standard response
        """
        response = requests.delete(os.path.join(doc_address, id), auth=(username, password))
        return format_response(response)

