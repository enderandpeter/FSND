from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()


def setup_db(app):
    """
    Binds a flask application and a SQLAlchemy service
    """
    app.config.from_object('config')
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


class Drink(Model, db.Model):
    """
    A persistent drink entity
    """

    __tablename__ = 'drinks'
    # Autoincrementing, unique primary key
    id = Column(Integer(), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe = Column(String(180), nullable=False)

    def format(self):
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }
