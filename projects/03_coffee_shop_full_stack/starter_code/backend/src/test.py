import unittest
from flask_migrate import upgrade, downgrade

from api import create_app
from models import setup_db, db


class CoffeeTestCase(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "coffeeshop_test"
        self.database_path = self.app.config['SQLALCHEMY_TEST_DATABASE_URI']
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            upgrade()

    def tearDown(self):
        with self.app.app_context():
            downgrade()

    def test_index(self):
        response = self.client().get('/')
        self.assertEqual('ho', response.data)


if __name__ == '__main__':
    unittest.main()
