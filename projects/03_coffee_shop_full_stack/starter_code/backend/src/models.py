from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()


def setup_db(app, database_path=''):
    """
    Binds a flask application and a SQLAlchemy service
    """
    app.config.from_object('config')
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path \
        if len(database_path) > 0 else app.config["SQLALCHEMY_DATABASE_URI"]
    migrate = Migrate(app, db)
    db.app = app
    db.init_app(app)


def update():
    """
    updates a new model into a database
    the model must exist in the database
    EXAMPLE
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.title = 'Black Coffee'
        drink.update()
    """
    db.session.commit()


class Model:
    def insert(self):
        """
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
        """
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {}

    def __repr__(self):
        return json.dumps(self.format())


DRINK_TITLE_MAX = 80
DRINK_RECIPE_MAX = 180

class Drink(Model, db.Model):
    """
    A persistent drink entity
    """
    __tablename__ = 'drinks'
    # Autoincrementing, unique primary key
    id = Column(Integer(), primary_key=True)
    # String Title
    title = Column(String(DRINK_TITLE_MAX), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe = Column(String(DRINK_RECIPE_MAX), nullable=False)

    '''
        short()
            short form representation of the Drink model
        '''

    def short(self):
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    '''
    long()
        long form representation of the Drink model
    '''

    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }
