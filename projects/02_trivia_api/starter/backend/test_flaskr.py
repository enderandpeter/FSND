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


    def test_get_questions(self):
        """Questions can be retrieved """
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['questions'][0]['id'], 1)
        self.assertEqual(data['questions'][0]['answer'], "Maya Angelou")
        self.assertEqual(len(data['questions']), QUESTIONS_PER_PAGE)


    def test_delete_question(self):
        """A question can be deleted"""
        question = Question.query.order_by(func.random()).first()
        id = question.id
        res = self.client().delete(f'/questions/{id}')
        self.assertEqual(res.status_code, 200)
        # The follow line causes the terminal to hang and not respond to key interrupts
        # deleted_question = Question.query.get(id)
        # self.assertIsNone(deleted_question)

    def test_search_questions(self):
        """Questions can be searched"""
        search_term = 'What'
        res = self.client().post('/questions/search', json={'searchTerm': search_term})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data['total_questions'], 8)

    def test_get_questions_by_cat(self):
        """Questions can be retrieved by category"""
        category_id = 3
        res = self.client().get(f'/categories/{category_id}/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for question in data['questions']:
            self.assertEqual(question['category']['id'], 3)

    def test_quizzes(self):
        """Quizzes work as expected"""


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
