import os
import sys

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import BadRequest, NotFound, UnprocessableEntity

from models import setup_db, Question, Category, db
from sqlalchemy import func

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, origins='*')

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response

    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.order_by('id').all()
        except Exception:
            print(sys.exc_info())
            abort(400)

        return jsonify([category.format() for category in categories])

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        try:
          questions = Question.query.order_by('id').all()
          categories = Category.query.order_by('id').all()
        except Exception:
            print(sys.exc_info())
            abort(400)

        formatted_questions = [question.format() for question in questions]
        displayed_questions = formatted_questions[start:end]

        return jsonify({
            'total_questions': len(formatted_questions),
            'questions': displayed_questions,
            'categories': [category.format() for category in categories],
            'current_category': None
        })


    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)
            if question:
                question.delete()
            else:
                raise NotFound
        except NotFound:
            abort(404)
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            abort(400)

        return jsonify({'success': True})


    @app.route('/questions', methods=['POST'])
    def create_question():
        error = False

        question_props = [
            'question',
            'answer',
            'difficulty',
            'category'
        ]

        question_data = {
            questionProp: request.get_json()[questionProp]
            for questionProp in question_props
        }

        for prop in question_props:
            value = question_data[prop].strip() if hasattr(question_data[prop], 'strip') else question_data[prop]
            value_length = len(value) if hasattr(value, 'strip') else value

            if value_length == 0 or value_length > 300:
                abort(422)

            if prop == 'difficulty' and (int(value) < 1 or int(value) > 5):
                abort(422)

        try:
            question_data['category'] = Category.query.get(question_data['category'])
            question = Question(**question_data)
            question.insert()
        except Exception:
            db.session.rollback()
            print(sys.exc_info())
            abort(400)

        return jsonify({'success': True})


    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            search_term = request.get_json()['search_term'].strip()
            search_term_length = len(search_term)
            if len(search_term.strip()) == 0:
                raise UnprocessableEntity
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        except (KeyError, UnprocessableEntity):
            abort(422)
        except Exception:
            print(sys.exc_info())
            abort(400)

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'total_questions': len(formatted_questions),
            'questions': formatted_questions,
            'current_category': None
        })

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        try:
            questions = Question.query.filter(Question.category_id == id).order_by('id').all()
        except Exception:
            db.session.rollback()
            abort(400)

        formatted_questions = [question.format() for question in questions]

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'total_questions': len(formatted_questions),
            'questions': formatted_questions,
            'current_category': id
        })

    @app.route('/quizzes', methods=['POST'])
    def manage_quizzes():
        try:
            previous_questions = request.get_json()['previous_questions']
            quiz_category = request.get_json()['quiz_category']

            question_query = Question.query\
                .filter(~Question.id.in_(previous_questions))

            if quiz_category['id']:
                question_query = question_query.filter(Question.category_id == quiz_category['id'])

            question = question_query.order_by(func.random()).first()
        except KeyError:
            abort(422)
        except Exception:
            print(sys.exc_info())
            abort(400)

        return jsonify({
            'question': question.format() if hasattr(question, 'format') else question
        })

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({
            "code": e.code,
            "message": "There was something wrong with the request"
        }), e.code

    @app.errorhandler(UnprocessableEntity)
    def handle_bad_request(e):
        return jsonify({
            "code": e.code,
            "message": "The data provided is not valid"
        }), e.code

    @app.errorhandler(NotFound)
    def handle_bad_request(e):
        return jsonify({
            "code": e.code,
            "message": "Requested resource not found"
        }), e.code

    return app
