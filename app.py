"""
This module sets up a Flask application for managing actors and films in a database.

It configures the application, initializes the database, and registers blueprints
for actor and film-related operations.
"""

from os import getenv

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate

from models import db
from views.actors import actors_app
from views.films import films_app

load_dotenv()


def create_app(config_class: str) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_class (str): The configuration class to use for the Flask application.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    app.register_blueprint(actors_app, url_prefix='/actors')
    app.register_blueprint(films_app, url_prefix='/films')

    return app


app = create_app('config.Config')
migrate = Migrate(app, db)


@app.route('/')
def homepage():
    """
    Render the homepage.

    Returns:
        str: Rendered HTML template for the homepage.
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=getenv('FLASK_PORT'), debug=False)
