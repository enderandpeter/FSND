import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
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
    
    def tearDown(self):
        """Executed after reach test"""
        self.db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
