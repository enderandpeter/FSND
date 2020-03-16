import os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import BadRequest
import json
from flask_cors import CORS

from models import setup_db, Drink
from auth import AuthError, requires_auth


def create_app():
    app = Flask(__name__)
    setup_db(app)
    CORS(app, origins='*', methods=['GET'], allow_headers=['Authorization'])

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    ## ROUTES
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks')
    def get_drinks():
        response = []
        try:
            drinks = Drink.query.all()
            response = {
                'success': True,
                'drinks': [drink.format() for drink in drinks]
            }
        except Exception:
            abort(400)

        return json.dumps(response)

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''


    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''


    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''


    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''


    ## Error Handling
    '''
    Example error handling for unprocessable entity
    '''

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({
            "code": e.code,
            "message": "There was something wrong with the request"
        }), e.code

    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404
    
    '''

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above 
    '''


    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''

    return app
