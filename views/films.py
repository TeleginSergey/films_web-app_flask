"""
Module to manage films data within the database.

The module includes functionality for:
    Listing films
    Viewing film details
    Adding a new film
    Updating an existing film
    Deleting a film
    Adding an actor to a film
    Deleting an actor from a film

It uses SQLAlchemy and Flask to interact with the database and render HTML templates.

This module is designed to provide a user-friendly interface
for managing films and associated actors in the system.
"""
from datetime import datetime

import pycountry
from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import delete, select, update
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from models import Actor, Film, FilmToActor, db
from utils import get_rating_movie

films_app = Blueprint('films_app', __name__)

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MAX_GENRE_LENGTH = 150
GET = 'GET'
all_countries = [country.name for country in pycountry.countries]
valid_statuses = {'completed', 'continues', 'announcement'}


@films_app.get('/', endpoint='list')
def get_films():
    """Get a list of films.

    Returns:
        A rendered template displaying a list of films.
    """
    films = db.session.scalars(select(Film))
    return render_template('films/films_list.html', films=films)


@films_app.get('/film/<uuid:film_id>/', endpoint='detail')
def detail(film_id):
    """Get details of a specific film.

    Args:
        film_id (uuid): The unique identifier of the film.

    Returns:
        A rendered template displaying details of the specified film.

    Raises:
        NotFound: If the film with the provided ID is not found.
    """
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(
        select(Film).where(
            Film.id == film_id,
        ),
    )

    if not film:
        raise NotFound(f'Film with id:"{film_id}" not found!')

    movie_data = get_rating_movie(film.title)

    if movie_data['docs']:
        imbd_rating = movie_data['docs'][0]['rating']['kp']
    else:
        imbd_rating = None

    actors = [film_actor.actor for film_actor in film.actors]

    return render_template(
        'films/film_detail.html',
        film=film,
        actors=actors,
        imbd_rating=imbd_rating,
    )


@films_app.route('/add/', methods=['GET', 'POST'], endpoint='add')
def add_film():
    """
    Add a new film to the database.

    Returns:
        GET: Render the film creation template.
        POST: Redirect to the detail page of the newly added film.
    """
    if request.method == 'GET':
        return render_template('films/film_create.html', countries=all_countries)

    title = request.form['film-title']
    description = request.form['film-description']
    country = request.form['film-country']
    year = request.form['film-year']
    rating = request.form['film-rating']
    status = request.form['film-status']
    genre = request.form['film-genre']

    if len(title) >= MAX_TITLE_LENGTH:
        return BadRequest('Length of title must not be greater than 200 symbols')

    if len(description) >= MAX_DESCRIPTION_LENGTH:
        return BadRequest('Length of description must not be greater than 1000 symbols')

    if len(genre) >= MAX_GENRE_LENGTH:
        return BadRequest('Length of genre must not be greater than 150 symbols')

    if int(year) > datetime.today().year:
        return BadRequest("Film's year cannot be in the future.")

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')

    if status not in valid_statuses:
        return BadRequest(
            "This status doesn't exist, use one of these: completed, continues, announcement",
        )

    film = Film(
        title=title,
        description=description,
        year=year,
        rating=rating,
        status=status,
        country=country,
        genre=genre,
    )
    db.session.add(film)
    db.session.commit()

    return redirect(url_for('films_app.detail', film_id=film.id))


@films_app.route('/update/<uuid:film_id>', methods=['GET', 'POST'], endpoint='update')
def update_film(film_id):
    """
    Update an existing film in the database.

    Args:
        film_id (uuid): The unique identifier of the film to be updated.

    Returns:
        GET: Render the film update template.
        POST: Redirect to the detail page of the updated film.

    Raises:
        NotFound: If no film is found with the specified film_id.
    """
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(select(Film).where(
        Film.id == film_id,
    ))

    if not film:
        raise NotFound(f'Film with id "{film_id}" not found!')

    if request.method == 'GET':
        return render_template('films/film_update.html', countries=all_countries)

    title = request.form['film-new-title']
    description = request.form['film-new-description']
    country = request.form['film-new-country']
    year = request.form['film-new-year']
    rating = request.form['film-new-rating']
    status = request.form['film-new-status']
    genre = request.form['film-new-genre']

    if len(title) >= MAX_TITLE_LENGTH:
        return BadRequest('Length of title must not be greater than 200 symbols')

    if len(description) >= MAX_DESCRIPTION_LENGTH:
        return BadRequest('Length of description must not be greater than 1000 symbols')

    if len(genre) >= MAX_GENRE_LENGTH:
        return BadRequest('Length of genre must not be greater than 150 symbols')

    if int(year) > datetime.today().year:
        return BadRequest("Film's year cannot be in the future.")

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')

    if status not in valid_statuses:
        return BadRequest(
            'This status does not exists, please one of this: completed, continues, announcement',
        )

    db.session.execute(
        update(Film).where(Film.id == film.id).values
        (
            title=title,
            description=description,
            country=country,
            year=year,
            rating=rating,
            status=status,
            genre=genre,
        ),
    )

    db.session.commit()
    url_detail = url_for(
        'films_app.detail', film_id=film.id,
    )
    return redirect(url_detail)


@films_app.route('/delete/<uuid:film_id>', methods=['GET', 'POST'], endpoint='delete')
def delete_film(film_id):
    """
    Delete a film from the database.

    Args:
        film_id (uuid): The unique identifier of the film to be deleted.

    Returns:
        Redirect to the list page of films after successfully deleting the film.

    Raises:
        NotFound: If no film is found with the specified film_id.
    """
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.get(Film, film_id)
    if not film:
        raise NotFound(f'Film with id "{film_id}" not found!')

    db.session.execute(
        delete(FilmToActor).where(FilmToActor.film_id == film.id),
    )

    db.session.delete(film)

    db.session.commit()
    return redirect(url_for('films_app.list'))


@films_app.route('/add_actor/<uuid:film_id>', methods=['GET', 'POST'], endpoint='add_actor')
def add_actor(film_id):
    """
    Add an actor to the list of actors associated with a film in the database.

    Args:
        film_id (uuid): The unique identifier of the film to which the actor will be added.

    Returns:
        GET: Render the add actor template.
        POST: Redirect to the detail page of the film after successfully adding the actor.

    Raises:
        NotFound: If no film or actor is found with the specified film_id or actor_id.
        Conflict: If the actor is already associated with the film.
    """
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(select(Film).where(
        Film.id == film_id,
    ))

    if not film:
        raise NotFound(f'Film with id "{film_id}" not found!')

    if request.method == 'GET':
        actors = db.session.scalars(select(Actor))
        return render_template('films/add_actor.html', actors=actors)

    actor_id = request.form['film-actor']

    actor = db.session.scalar(select(Actor).where(
        Actor.id == actor_id,
    ))

    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    film_to_actor_exist = db.session.scalar(
        select(FilmToActor).where(
            FilmToActor.actor_id == actor_id,
            FilmToActor.film_id == film_id,
        ),
    )

    if film_to_actor_exist:
        raise Conflict('Actor is already matched with this film')

    film_to_actor = FilmToActor(film_id=film_id, actor_id=actor_id)
    db.session.add(film_to_actor)
    db.session.commit()

    url_detail = url_for('films_app.detail', film_id=film_id)
    return redirect(url_detail)


@films_app.route('/delete_actor/<uuid:film_id>/<uuid:actor_id>', methods=['POST'])
def delete_actor(film_id, actor_id):
    """
    Delete an actor association with a film from the database.

    Args:
        film_id (uuid): The id film from which the actor association will be deleted.
        actor_id (uuid): The id actor to be removed from the film's list of associated actors.

    Returns:
        Redirect to the detail page of the film after successfully removing the actor association.
    """
    if not film_id:
        return BadRequest('Missing required parameters')

    if not actor_id:
        return BadRequest('Missing required parameters')

    film_to_actor = db.session.scalar(select(FilmToActor).where(
        FilmToActor.actor_id == actor_id,
        FilmToActor.film_id == film_id,
    ))

    if film_to_actor:
        db.session.delete(film_to_actor)
        db.session.commit()

    url_detail = url_for('films_app.detail', film_id=film_id)
    return redirect(url_detail)
