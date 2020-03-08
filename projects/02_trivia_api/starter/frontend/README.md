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
# Full Stack Trivia API  Frontend

## Getting Setup

> _tip_: this frontend is designed to work with [Flask-based Backend](../backend). It is recommended you stand up the backend first, test using Postman or curl, update the endpoints in the frontend, and then the frontend should integrate smoothly.

### Installing Dependencies

#### Installing Node and NPM

This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

#### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run:

```bash
npm install
```

>_tip_: **npm i** is shorthand for **npm install**

## Required Tasks

## Running Your Frontend in Dev Mode

The frontend app was built using create-react-app. In order to run the app in development mode use ```npm start```. You can change the script in the ```package.json``` file. 

Open [http://localhost:3000](http://localhost:3000) to view it in the browser. The page will reload if you make edits.<br>

```bash
npm start
```

## Request Formatting

The frontend should be fairly straightforward and disgestible. You'll primarily work within the ```components``` folder in order to edit the endpoints utilized by the components. While working on your backend request handling and response formatting, you can reference the frontend to view how it parses the responses. 

After you complete your endpoints, ensure you return to and update the frontend to make request and handle responses appropriately: 
- Correct endpoints
- Update response body handling 

## Optional: Styling

In addition, you may want to customize and style the frontend by editing the CSS in the ```stylesheets``` folder. 

## Optional: Game Play Mechanics

Currently, when a user plays the game they play up to five questions of the chosen category. If there are fewer than five questions in a category, the game will end when there are no more questions in that category. 

You can optionally update this game play to increase the number of questions or whatever other game mechanics you decide. Make sure to specify the new mechanics of the game in the README of the repo you submit so the reviewers are aware that the behavior is correct. 
