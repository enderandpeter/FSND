import sys
from functools import wraps
from urllib.request import urlopen

from flask import Flask, request, jsonify
from jose import jwt
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, UnprocessableEntity, NotFound
import json
from flask_cors import CORS

from config import AUTH0_DOMAIN, API_AUDIENCE, ALGORITHMS
from models import setup_db, update, Drink, DRINK_RECIPE_MAX, DRINK_TITLE_MAX
from auth import requires_auth


def create_app():
    app = Flask(__name__)
    setup_db(app)
    CORS(app, origins='*', methods=['GET'], allow_headers=['Authorization'])

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    class TokenExpired(BadRequest):
        message = 'token_expired'
        description = 'Token has expired'

    class PermissionsNotFound(BadRequest):
        message = 'no_permissions'
        description = 'Permissions not included in JWT.'

    class AuthHeaderMissing(Unauthorized):
        message = 'authorization_header_missing'
        description = 'Authorization header is expected.'

    class AuthHeaderInvalid(BadRequest):
        message = 'invalid_header'
        description = 'Authorization header must start with "Bearer".'

    def get_token_auth_header():
        """
        Obtains the access token from the authorization header
        """
        auth = request.headers.get('Authorization', None)
        if not auth:
            raise AuthHeaderMissing

        parts = auth.split()
        if parts[0].lower() != 'bearer':
            raise AuthHeaderInvalid

        elif len(parts) == 1:
            raise AuthHeaderInvalid(description='Token not found')

        elif len(parts) > 2:
            raise AuthHeaderInvalid(description='Authorization header must be bearer token.')

        token = parts[1]
        return token

    def verify_decode_jwt(token):
        jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        if 'kid' not in unverified_header:
            raise AuthHeaderInvalid(description='Authorization malformed.')

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=f'https://{AUTH0_DOMAIN}/'
                )

                return payload

            except jwt.ExpiredSignatureError:
                raise TokenExpired

            except jwt.JWTClaimsError:
                raise AuthHeaderInvalid(description='Incorrect claims. Please, check the audience and issuer.')
            except Exception:
                raise AuthHeaderInvalid(description='Unable to parse authentication token.')
        raise AuthHeaderInvalid(description='Unable to find the appropriate key.')

    def check_permissions(permission, payload):
        if 'permissions' not in payload:
            raise PermissionsNotFound

        if permission not in payload['permissions']:
            raise Unauthorized(description='Permission not found.')
        return True

    def requires_auth(permission=''):
        def requires_auth_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                token = get_token_auth_header()

                payload = verify_decode_jwt(token)

                check_permissions(permission, payload)

                return f(payload, *args, **kwargs)

            return wrapper

        return requires_auth_decorator

    ## ROUTES
    @app.route('/drinks')
    def get_drinks():
        response = []
        try:
            drinks = Drink.query.all()
            response = {
                'success': True,
                'drinks': [drink.short() for drink in drinks]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return json.dumps(response)

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks-detail')
    @requires_auth(permission='get:drinks-detail')
    def get_drink_detail():
        response = []
        try:
            drinks = Drink.query.all()
            response = {
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            }
        except Exception:
            print(sys.exc_info())
            raise BadRequest

        return json.dumps(response)

    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks', methods=['POST'])
    @requires_auth(permission='post:drinks')
    def create_drink():
        response = ''
        try:
            drink_data = {
                'title': request.get_json()['title'].strip(),
                'recipe': request.get_json()['recipe'].strip()
            }

            drink_title_length = len(drink_data['title'])
            drink_recipe_length = len(drink_data['recipe'])

            if drink_title_length == 0 or drink_title_length > DRINK_TITLE_MAX \
                    or 0 == drink_recipe_length or drink_recipe_length > DRINK_RECIPE_MAX:
                raise UnprocessableEntity

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

        return json.dumps(response)

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
    @app.route('/drinks/<int:id>', methods=['PATCH'])
    @requires_auth(permission='patch:drinks')
    def patch_drink(id):
        response = ''
        try:
            drink = Drink.query.get(id)
            if not drink:
                raise NotFound

            drink_data = {
                'title': request.get_json()['title'].strip(),
                'recipe': request.get_json()['recipe'].strip()
            }

            drink_title_length = len(drink_data['title'])
            drink_recipe_length = len(drink_data['recipe'])

            if drink_title_length == 0 or drink_title_length > DRINK_TITLE_MAX \
                    or 0 == drink_recipe_length or drink_recipe_length > DRINK_RECIPE_MAX:
                raise UnprocessableEntity

            drink.title = drink_data['title']
            drink.recipe = drink_data['recipe']
            update()
            response = {
                'success': True,
                'drinks': [drink.long()]
            }
        except (NotFound, UnprocessableEntity):
            raise

        return json.dumps(response)
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
    @app.route('/drinks/<int:id>', methods=['DELETE'])
    @requires_auth(permission='delete:drinks')
    def delete_drink(id):
        response = ''
        try:
            drink = Drink.query.get(id)
            if not drink:
                raise NotFound

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

        return json.dumps(response)

    ## Error Handling
    @app.errorhandler(HTTPException)
    def handle_bad_request(e):
        response_body = {
            "code": e.code,
            "description": e.description
        }

        if hasattr(e, 'message'):
            response_body['message'] = e.message

        return jsonify(response_body), e.code

    return app
