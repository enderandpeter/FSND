import sys
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException, BadRequest, UnprocessableEntity, NotFound
import json
from flask_cors import CORS

from errors import DrinkNotFound
from models import setup_db, db, update, Drink, DRINK_RECIPE_MAX, DRINK_TITLE_MAX
from auth import requires_auth


def create_app():
    app = Flask(__name__)
    setup_db(app)
    CORS(
        app,
        origins='*',
        methods=['GET', 'POST', 'DELETE', 'PATCH'],
        allow_headers=['Authorization', 'Content-Type']
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, PATCH')
        return response

    # ROUTES
    @app.route('/drinks')
    def get_drinks():
        response = []
        try:
            drinks = Drink.query.order_by('id').all()
            response = {
                'success': True,
                'drinks': [drink.short() for drink in drinks]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/drinks-detail')
    @requires_auth(permission='get:drinks-detail')
    def get_drink_detail():
        response = []
        try:
            drinks = Drink.query.order_by('id').all()
            response = {
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    def validate_drink(title=None, recipe=None, updating=None):
        check_title = True if not updating and title is not None else False
        check_recipe = True if not updating and recipe is not None else False

        drink_data = {}

        if check_title:
            drink_data = {
                'title': title.strip()
            }

            drink_title_length = len(drink_data['title'])
            if drink_title_length == 0 or drink_title_length > DRINK_TITLE_MAX:
                raise UnprocessableEntity(description="Please check drink title length")

        if check_recipe:
            drink_data['recipe'] = recipe

            drink_recipe_length = len(json.dumps(drink_data['recipe']))

            if 0 == drink_recipe_length or drink_recipe_length > DRINK_RECIPE_MAX:
                raise UnprocessableEntity(description="Please check field lengths")

            for recipe in drink_data['recipe']:
                if 'name' not in recipe or \
                        'color' not in recipe or \
                        'parts' not in recipe:
                    raise UnprocessableEntity(description="A recipe is missing a property")

            drink_data['recipe'] = json.dumps(drink_data['recipe']);

        return drink_data

    @app.route('/drinks', methods=['POST'])
    @requires_auth(permission='post:drinks')
    def create_drink():
        response = ''
        try:
            drink_data = {
                'title': request.get_json()['title'],
                'recipe': request.get_json()['recipe']
            }

            drink_data = validate_drink(**drink_data)

            drink = Drink(**drink_data)
            drink.insert()
            response = {
                'success': True,
                'drinks': [drink.long()]
            }
        except UnprocessableEntity:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    @app.route('/drinks/<int:id>', methods=['PATCH'])
    @requires_auth(permission='patch:drinks')
    def patch_drink(id):
        response = ''
        try:
            drink = Drink.query.get(id)
            if not drink:
                raise DrinkNotFound

            drink_data = {
                'title': request.get_json()['title'] if 'title' in request.get_json() else None,
                'recipe': request.get_json()['recipe'] if 'recipe' in request.get_json() else None
            }

            drink_data = validate_drink(**drink_data)

            for prop, val in drink_data.items():
                setattr(drink, prop, val)

            update()
            response = {
                'success': True,
                'drinks': [drink.long()]
            }
        except (NotFound, UnprocessableEntity):
            raise
        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            raise

        return jsonify(response)

    @app.route('/drinks/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:drinks')
    def delete_drink(id):
        response = ''
        try:
            drink = Drink.query.get(id)
            if not drink:
                raise DrinkNotFound

            drink.delete()
            response = {
                'success': True,
                'delete': id
            }
        except NotFound:
            raise
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return jsonify(response)

    ## Error Handling
    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        code = e.code if hasattr(e, 'code') else 500
        description = e.description if hasattr(e, 'description') else 'Please contact the server admin'
        response_body = {
            "code": code,
            "description": description,
        }

        if hasattr(e, 'message'):
            response_body['message'] = e.message

        return jsonify(response_body), code

    return app
