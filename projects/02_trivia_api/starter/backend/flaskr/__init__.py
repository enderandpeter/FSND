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
        error = False

        try:
            categories = Category.query.order_by('id').all()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
            abort(400)

        return jsonify([category.format() for category in categories])

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        error = False

        try:
          questions = Question.query.order_by('id').all()
          categories = Category.query.order_by('id').all()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
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
        error = False

        try:
            question = Question.query.get(id)
            if question:
                question.delete()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
            abort(400)

        return jsonify({'success': True})


    @app.route('/questions', methods=['POST'])
    def create_question():
        error = False

        questionProps = [
            'question',
            'answer',
            'difficulty',
            'category'
        ]

        questionData = {
            questionProp: request.get_json()[questionProp]
            for questionProp in questionProps
        }

        for prop in questionProps:
            value = questionData[prop].strip()
            valueLength = len(value)
            if valueLength == 0 or valueLength > 300:
                abort(422)

            if prop == 'difficulty' and (int(value) < 1 or int(value) > 5):
                abort(422)

        try:
            questionData['category'] = Category.query.get(questionData['category'])
            question = Question(**questionData)
            question.insert()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
            abort(400)

        return jsonify({'success': True})


    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        error = False

        try:
            search_term = request.get_json()['searchTerm'].strip()
            search_term_length = len(search_term)
            if len(search_term.strip()) == 0:
                abort(422)
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        except ValueError:
            abort(422)
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
            abort(400)

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'total_questions': len(formatted_questions),
            'questions': formatted_questions,
            'current_category': None
        })

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        error = False

        try:
            questions = Question.query.filter(Question.category_id == id).order_by('id').all()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
            abort(400)

        formatted_questions = [question.format() for question in questions]

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'total_questions': len(formatted_questions),
            'questions': formatted_questions,
            'current_category': id
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def manage_quizzes():
        error = False

        try:
            previous_questions = request.get_json()['previous_questions']
            quiz_category = request.get_json()['quiz_category']

            question_query = Question.query\
                .filter(~Question.id.in_(previous_questions))

            if quiz_category['id']:
                question_query = question_query.filter(Question.category_id == quiz_category['id'])

            question = question_query.order_by(func.random()).first()
        except ValueError:
            abort(422)
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        if error:
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
