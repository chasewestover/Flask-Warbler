# Warbler

Warbler is a Twitter clone that uses Flask, PostgreSQL, and SQLAlchemy on the back-end and Jinja templating, jQuery, and Axios on the front-end. I built this application off of a semi-functioning clone.

Key components I worked on:
* squashing bugs in the user profile, logout, and homepage routes
* adding profile editing functionality
* adding the ability to like a Warble
* adding private profiles and follow requests for private profiles
* testing

You can view a deployed version [here](https://warbler-warbler-warbler.herokuapp.com/).

## Installation and Setup Instructions

1. Clone this repository
2. Create a virtual environment
    * `python3 -m venv venv`
    * `source venv/bin/activate`
    * `pip3 install -r requirements.txt`
3. Create the database
    * `createdb warbler warbler-test`
    * `python3 seed.py`
4. Start the server
    * `flask run`

## Technologies Used

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Web Development
  Framework
* [Flask-WTForms](https://flask-wtf.readthedocs.io/en/stable/) - integration of
  Flask and WTForms library, including CSRF protection
* [PostgreSQL Database](https://www.postgresql.org/) - SQL database management
  system
* [SQLAlchemy](https://www.sqlalchemy.org/) - database ORM
* [Jinja](https://palletsprojects.com/p/jinja/) - templating engine 

## Authors

My partner for this project was [Kevin Huang](https://github.com/kehuang805). 