# My Triva API

## Requirements

* Python 3.7
* Postgres 12.1

## Installation

1. Clone this repo

### Backend
1. Go to the `backend` folder
2. Run `pip install -r requirements.txt`
3. Set the following environment variables:
   * `FLASK_APP=flaskr`
4. Copy `config.py.example` to `config.py` and set the DB URI for the main and test DBs
5. Run `flask run`. The tables will be created
6. Run a command like `psql trivia < trivia_data.psql` or `psql -d [dbname] -f trivia_data.psql` to seed the DB
7. Run the tests to confirm that the backend is ready

### Frontend
1. Go to the `frontend` folder
2. Copy `config.js.example` to `config.js` and make sure it has the right backend server host set
2. Run `npm install`
3. Run `npm start`

### Tests
1. Run `python -m unittest test_flaskr.py`

# API Documentation

All requests and responses are JSON, as you might guess.

## Datatypes
The base types are all standard JSON types

* __category__: Object
  * _id_: int
  * _type_: string
  
* __question__: Object
  * _id_: int
  * _question_: string
  * _answer_: string
  * _category_: category
  * _difficulty_: int

## Errors

### Responses

* __error__: Object
  * __code__: int
  * __message__: string

#### Examples
##### Bad Request
The request was formatted in a way that the application could not make sense of... or maybe something else happened.
```json
{
    "code": 400,
    "message": "There was something wrong with the request"
}
```

##### Unprocessable Entity
The request has missing or invalid data.
```json
{
    "code": 422,
    "message": "The data provided is not valid"
}
```

##### Not Found
The request was for something that the application could not find
```json
{
    "code": 404,
    "message": "Requested resource not found"
}
```

## GET /categories

Return an array of quiz categories

### Response

* _category[]_

### Example

````json
[
  {
    "id": 1, 
    "type": "Science"
  }, 
  {
    "id": 2, 
    "type": "Art"
  }, 
  {
    "id": 3, 
    "type": "Geography"
  }, 
  {
    "id": 4, 
    "type": "History"
  }, 
  {
    "id": 5, 
    "type": "Entertainment"
  }, 
  {
    "id": 6, 
    "type": "Sports"
  }
]

````

### Errors
* Bad Request

## GET /questions[?page=1]

Return an object of data related to quiz questions. You can request pages that contain a max of ten questions.

* __page__: _int_ - Optional. If a page is requested that will not contain questions, then __questions__ will be empty

### Response

* __categories__: _category[]_
* __current_category__: _null_
* __questions__: _question[]_
* __total_questions__: _int_

### Example

````json
{
  "categories": [
    {
      "id": 1, 
      "type": "Science"
    }, 
    {
      "id": 2, 
      "type": "Art"
    }, 
    {
      "id": 3, 
      "type": "Geography"
    }, 
    {
      "id": 4, 
      "type": "History"
    }, 
    {
      "id": 5, 
      "type": "Entertainment"
    }, 
    {
      "id": 6, 
      "type": "Sports"
    }
  ], 
  "current_category": null, 
  "questions": [
    {
      "answer": "The sound of one hand clapping", 
      "category": {
        "id": 1, 
        "type": "Science"
      }, 
      "difficulty": 1, 
      "id": 1, 
      "question": "What is the difference between a duck?"
    }, 
    {
      "answer": "Apollo 13", 
      "category": {
        "id": 5, 
        "type": "Entertainment"
      }, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },    
    ...
  ], 
  "total_questions": 19
}
````

### Errors

* Bad Request

## POST /questions

Create a new question

### Request

* __question__: _string_ - Required.
* __answer__: _string_ - Required.
* __difficulty__: _int_ - Required.
* __category__: _int_ - Required.

#### Example
````json
{
  "question": "What is your name?",
  "answer": "King Arthur",
  "difficulty": 5,
  "category": 3
}
````

### Response

* __success__: _true_

#### Example
````json
{
 "success": true
}
````

### Errors

* Bad Request
* Unprocessable Entity

## DELETE /questions/[id]

Delete a question of the specified id.

* __id__: _int_ - Required.

## Response

* __success__: _true_

### Example

````json
{
 "success": true
}
````

### Errors

* Bad Request
* Not Found

## POST /questions/search

Search for questions based on the provided search term

### Request

* __search_term__: _string_ - Required.

#### Example
```json
{
  "search_term": "pe"
}
```

### Response

* __total_questions__: _int_
* __questions__: _question[]_
* __current_category__: _null_

#### Example
```json
{
  "current_category": null,
  "questions": [{
      "answer": "George Washington Carver",
      "category": {
        "id": 4,
        "type": "History"
      },
      "difficulty": 2,
      "id": 8,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Scarab",
      "category": {
        "id": 4,
        "type": "History"
      },
      "difficulty": 4,
      "id": 19,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    }
  ],
  "total_questions": 2
}
```

### Errors

* Bad Request
* Unprocessable Entity

## GET /categories/[id]/questions

Show all questions in the category specified by the id. 

* __id__: _int_ - Required.

## Response

* __total_questions__: _int_
* __questions__: _question[]_
* __current_category__: _int_

## Example
```json
{
  "current_category": 3, 
  "questions": [
    {
      "answer": "Lake Victoria", 
      "category": {
        "id": 3, 
        "type": "Geography"
      }, 
      "difficulty": 2, 
      "id": 9, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": {
        "id": 3, 
        "type": "Geography"
      }, 
      "difficulty": 3, 
      "id": 10, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }, 
    {
      "answer": "Agra", 
      "category": {
        "id": 3, 
        "type": "Geography"
      }, 
      "difficulty": 2, 
      "id": 11, 
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ], 
  "total_questions": 3
}
```

### Errors

* Bad Request
* Not Found

## POST /quizzes

Retrieve a question from a category that is not in the list of previous questions.

### Request

* __previous_questions__: _int[]_
* __quiz_category__: _category_

Every request will return a random question from the category whose question ID is not listed
among __previous_questions__.

#### Example
```json
{
  "previous_questions": [ 5, 7, 11],
  "quiz_category": {
    "type": "Art",
    "id": 2
  }
}
```

### Response

* __total_questions__: _int_
* __questions__: _question[]_ | _null_
* __current_category__: _null_

__questions__ returns _null_ when there are no more questions in the category 

#### Example
```json
{
  "question": {
    "answer": "The Windbreaker",
      "category": {
        "id": 2,
        "type": "Art"
      },
      "difficulty": 4,
      "id": 12,
      "question": "Who fights the wind?"
  }
}
```

### Errors

* Bad Request
* Unprocessable Entity

# Original Readme

# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET ...
POST ...
DELETE ...

GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}

```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
