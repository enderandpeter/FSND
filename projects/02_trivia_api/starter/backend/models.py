from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=''):
    app.config.from_object('config')
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path \
        if len(database_path) > 0 else app.config["SQLALCHEMY_DATABASE_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question

'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category_id = Column(
        Integer,
        ForeignKey('categories.id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category.format(),
            'difficulty': self.difficulty
        }


'''
Category
'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    questions = db.relationship('Question', backref='category', cascade="all, delete-orphan")

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
