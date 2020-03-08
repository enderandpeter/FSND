import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import json
from sqlalchemy import create_engine, text
from sqlalchemy.sql.expression import func

from flaskr import create_app, QUESTIONS_PER_PAGE
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = self.app.config['SQLALCHEMY_TEST_DATABASE_URI']
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # Seed the DB
        with open('trivia_data.psql') as f:
            engine = create_engine(self.database_path)
            escaped_sql = text(f.read())
            engine.execute(escaped_sql)

    def dropTables(self):
        connection = create_engine(self.database_path)
        connection.execute('drop table if exists questions')
        connection.execute('drop table if exists categories')

    def tearDown(self):
        self.dropTables()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Categories can be retrieved """
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['type'], "Science")
        self.assertEqual(len(data), 6)

        self.dropTables()
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 400)


    def test_get_questions(self):
        """Questions can be retrieved """
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['questions'][0]['id'], 1)
        self.assertEqual(data['questions'][0]['answer'], "Maya Angelou")
        self.assertEqual(len(data['questions']), QUESTIONS_PER_PAGE)

        self.dropTables()
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 400)

    def test_delete_question(self):
        """A question can be deleted"""
        question = Question.query.order_by(func.random()).first()
        id = question.id
        res = self.client().delete(f'/questions/{id}')
        self.assertEqual(res.status_code, 200)

        res = self.client().delete(f'/questions/{id}')
        self.assertEqual(res.status_code, 404)

        self.dropTables()
        res = self.client().delete(f'/questions/{id}')
        self.assertEqual(res.status_code, 400)

    def test_search_questions(self):
        """Questions can be searched"""
        search_term = 'What'
        res = self.client().post('/questions/search', json={'search_term': search_term})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['total_questions'], 8)

        res = self.client().post('/questions/search', json={'searchterm': search_term})
        self.assertEqual(res.status_code, 422)

        res = self.client().post('/questions/search', json={'search_term': ''})
        self.assertEqual(res.status_code, 422)

    def test_get_questions_by_cat(self):
        """Questions can be retrieved by category"""
        category_id = 3
        res = self.client().get(f'/categories/{category_id}/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for question in data['questions']:
            self.assertEqual(question['category']['id'], 3)

        res = self.client().get(f'/categories/5000/questions')
        self.assertEqual(res.status_code, 404)

        self.dropTables()
        res = self.client().get(f'/categories/{category_id}/questions')
        self.assertEqual(res.status_code, 400)

    def test_quizzes(self):
        """Quizzes work as expected"""
        categories = Category.query.all()
        for category in categories:
            category_questions = Question.query.filter(category.id == Question.category_id).all()
            category_question_ids = [question.id for question in category_questions]

            previous_questions = []
            last_question_id = 0
            for question_id in category_question_ids:
                res = self.client().post('/quizzes', json={
                    "previous_questions": previous_questions,
                    "quiz_category": {
                        "type": category.type,
                        "id": category.id
                    }
                })
                data = json.loads(res.data)
                last_question_id = data['question']['id']
                self.assertNotIn(last_question_id, previous_questions)
                previous_questions.append(last_question_id)

        res = self.client().post('/quizzes', json={
            "previousquestions": [],
            "quiz_category": {
                "type": "Something",
                "id": 1
            }
        })
        self.assertEqual(res.status_code, 422)

        res = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {
                "type": "Something",
            }
        })
        self.assertEqual(res.status_code, 422)

        self.dropTables()
        res = self.client().post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {
                "type": "Something",
                "id": 1
            }
        })
        self.assertEqual(res.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
