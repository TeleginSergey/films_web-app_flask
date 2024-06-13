"""
Main module to manage actors and films data within the database.

The module includes functionality for:
    Listing actors
    Viewing actor details
    Adding a new actor
    Updating an existing actor
    Deleting an actor
    Adding a film to an actor
    Deleting a film from an actor

It uses SQLAlchemy and Flask to interact with the database and render HTML templates.

This module is designed to provide a user-friendly interface
for managing actors and films in the system.
"""
from datetime import datetime

import pycountry
from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import delete, select, update
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from models import Actor, Film, FilmToActor, db

actors_app = Blueprint('actors_app', __name__)


GET = 'GET'
all_countries = [country.name for country in pycountry.countries]


@actors_app.get('/', endpoint='list')
def get_actors():
    """
    Retrieve a list of actors from the database and render them in the actors_list.html template.

    Returns:
        actors: List of Actor objects

    Template:
        actors_list.html
    """
    actors = db.session.scalars(select(Actor))
    return render_template('actors/actors_list.html', actors=actors)


@actors_app.get('/actor/<uuid:actor_id>/', endpoint='detail')
def detail(actor_id):
    """
    Get details of a specific actor based on the given actor_id.

    Args:
        actor_id (uuid): The unique identifier for the actor.

    Returns:
        rendered HTML displaying details of the actor and the films they have been a part of.

    Raises:
        NotFound: If no actor is found with the provided actor_id.
    """
    if not actor_id:
        return BadRequest('Missing required parameters')

    actor = db.session.scalar(
        select(Actor).where(
            Actor.id == actor_id,
        ),
    )

    if not actor:
        raise NotFound(f'Actor with id:"{actor_id}" not found!')

    films = [film_actor.film for film_actor in actor.films]

    return render_template('actors/actor_detail.html', actor=actor, films=films)


@actors_app.route('/add/', methods=['GET', 'POST'], endpoint='add')
def add_actor():
    """
    Add a new actor to the database.

    Returns:
        GET: Render the actor creation template.
        POST: Redirect to the detail page of the newly added actor.
    """
    if request.method == 'GET':
        return render_template('actors/actor_create.html', countries=all_countries)

    full_name = request.form['actor-full-name']
    birth_date_str = request.form['actor-birth-date']
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    sex = request.form['actor-sex']
    country = request.form['actor-country']
    death_str = request.form['actor-death']
    death = datetime.strptime(death_str, '%Y-%m-%d').date()

    if birth_date > datetime.today().date():
        return BadRequest('Birth date cannot be in the future.')

    if birth_date > death:
        return BadRequest('Birth date cannot bigger than death')

    if death > datetime.today().date():
        return BadRequest('Death date cannot be in the future.')

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')

    actor = Actor(
        full_name=full_name,
        birth_date=birth_date,
        sex=sex,
        country=country,
        death=death,
    )
    db.session.add(actor)
    db.session.commit()

    return redirect(url_for('actors_app.detail', actor_id=actor.id))


@actors_app.route('/update/<uuid:actor_id>', methods=['GET', 'POST'], endpoint='update')
def update_actor(actor_id):
    """
    Update an existing actor in the database.

    Args:
        actor_id (uuid): The unique identifier of the actor to be updated.

    Returns:
        GET: Render the actor update template.
        POST: Redirect to the detail page of the updated actor.

    Raises:
        NotFound: If no actor is found with the specified actor_id.
    """
    if not actor_id:
        return BadRequest('Missing required parameters')

    actor = db.session.scalar(select(Actor).where(
        Actor.id == actor_id,
    ))

    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    if request.method == 'GET':
        return render_template('actors/actor_update.html', countries=all_countries)

    full_name = request.form['actor-new-full-name']
    birth_date_str = request.form['actor-new-birth-date']
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    sex = request.form['actor-new-sex']
    country = request.form['actor-new-country']
    death_str = request.form['actor-new-death']
    death = datetime.strptime(death_str, '%Y-%m-%d').date()

    if birth_date > datetime.today().date():
        return BadRequest('Birth date cannot be in the future.')

    if birth_date > death:
        return BadRequest('Birth date cannot bigger than death')

    if death > datetime.today().date():
        return BadRequest('Death date cannot be in the future.')

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')

    db.session.execute(
        update(Actor).where(Actor.id == actor.id).values
        (
            full_name=full_name,
            birth_date=birth_date,
            sex=sex,
            country=country,
            death=death,
        ),
    )

    db.session.commit()
    url_detail = url_for(
        'actors_app.detail', actor_id=actor.id,
    )
    return redirect(url_detail)


@actors_app.route('/delete/<uuid:actor_id>', methods=[GET, 'POST'], endpoint='delete')
def delete_actor(actor_id):
    """
    Delete an existing actor from the database.

    Args:
        actor_id (uuid): The unique identifier of the actor to be deleted.

    Returns:
        Redirect to the list page of actors after successful deletion.

    Raises:
        NotFound: If no actor is found with the specified actor_id.
    """
    if not actor_id:
        return BadRequest('Missing required parameters')

    actor = db.session.get(Actor, actor_id)
    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    db.session.execute(
        delete(FilmToActor).where(FilmToActor.actor_id == actor.id),
    )

    db.session.delete(actor)

    db.session.commit()
    return redirect(url_for('actors_app.list'))


@actors_app.route('/add_film/<uuid:actor_id>', methods=['GET', 'POST'], endpoint='add_film')
def add_film(actor_id):
    """
    Add a film to the list of films associated with an actor in the database.

    Args:
        actor_id (uuid): The unique identifier of the actor to which the film will be added.

    Returns:
        GET: Render the add film template.
        POST: Redirect to the detail page of the actor after successfully adding the film.

    Raises:
        NotFound: If no actor or film is found with the specified actor_id or film_id.
        Conflict: If the film is already associated with the actor.
    """
    if not actor_id:
        return BadRequest('Missing required parameters')

    actor = db.session.scalar(select(Actor).where(
        Actor.id == actor_id,
    ))

    if not actor:
        raise NotFound(f'Actor with id "{actor_id}" not found!')

    if request.method == 'GET':
        films = db.session.scalars(select(Film))
        return render_template('actors/add_film.html', films=films)

    film_id = request.form['actor-film']

    film = db.session.scalar(select(Film).where(
        Film.id == film_id,
    ))

    film_to_actor_exist = db.session.scalar(
        select(FilmToActor).where(
            FilmToActor.actor_id == actor_id,
            FilmToActor.film_id == film_id,
        ),
    )

    if film_to_actor_exist:
        raise Conflict('Film is already matched with this actor')

    if not film:
        raise NotFound(f'Actor with id "{film_id}" not found!')

    film_to_actor = FilmToActor(film_id=film_id, actor_id=actor_id)
    db.session.add(film_to_actor)
    db.session.commit()

    url_detail = url_for('actors_app.detail', actor_id=actor_id)
    return redirect(url_detail)


@actors_app.route('/delete_film/<uuid:actor_id>/<uuid:film_id>', methods=['POST'])
def delete_film(actor_id, film_id):
    """
    Delete a film association with an actor from the database.

    Args:
        actor_id (uuid): The id actor from which the film association will be deleted.
        film_id (uuid): The id film to be removed from the actor's list of associated films.

    Returns:
        Redirect to the detail page of the actor after successfully removing the film association.
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

    url_detail = url_for('actors_app.detail', actor_id=actor_id)
    return redirect(url_detail)
