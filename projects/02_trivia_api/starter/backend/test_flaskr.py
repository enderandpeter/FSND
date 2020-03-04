import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import json
from sqlalchemy import create_engine, text

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
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
        connection.execute('drop table if exists categories')
        connection.execute('drop table if exists questions')

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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
