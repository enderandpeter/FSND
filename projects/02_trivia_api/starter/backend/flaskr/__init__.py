import os
import sys

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

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
            categories = Category.query.order_by('id').all();
        except Exception:
            error = True

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

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        error = False

        try:
            question = Question.query.get(id)
            if question:
                question.delete()
        except Exception:
            error = True

        if error:
            abort(400)

        return jsonify({'success': True})

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
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

        questionData['category'] = Category.query.get(questionData['category'])
        try:
            question = Question(**questionData)
            question.insert()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            abort(400)

        return jsonify({'success': True})

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

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

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    return app
