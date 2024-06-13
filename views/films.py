from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import delete, select, update
from datetime import datetime
from werkzeug.exceptions import BadRequest, NotFound, Conflict
import pycountry

from utils import get_rating_movie
from models import FilmToActor, db, Film, Actor

films_app = Blueprint('films_app', __name__)


GET = 'GET'
all_countries = [country.name for country in pycountry.countries]

@films_app.get('/', endpoint='list')
def get_films():

    films = db.session.scalars(select(Film))
    return render_template('films/films_list.html', films=films)


@films_app.get('/film/<uuid:film_id>/', endpoint='detail')
def detail(film_id):
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(
        select(Film).where(
            Film.id == film_id
        )
    )

    if not film:
        raise NotFound(f'Film with id:"{film_id}" not found!')
    
    movie_data = get_rating_movie(film.title)

    if movie_data['docs']:
        imbd_rating = movie_data['docs'][0]['rating']['kp']
    else:
        imbd_rating = None

    actors = [film_actor.actor for film_actor in film.actors]

    return render_template('films/film_detail.html', film=film, actors=actors, imbd_rating=imbd_rating)


@films_app.route('/add/', methods=['GET', 'POST'], endpoint='add')
def add_film():

    if request.method == 'GET':
        return render_template('films/film_create.html', countries=all_countries)

    title = request.form['film-title']
    description = request.form['film-description']
    country = request.form['film-country']
    year = request.form['film-year']
    rating = request.form['film-rating']
    status = request.form['film-status']
    genre = request.form['film-genre']

    if len(title) >= 200:
        return BadRequest('Length of title must not be greater than 200 symbols')
    
    if len(description) >= 1000:
        return BadRequest('Length of description must not be greater than 1000 symbols')

    if len(genre) >= 150:
        return BadRequest('Length of genre must not be greater than 150 symbols')

    if int(year) > datetime.today().year:
        return BadRequest("Film's year cannot be in the future.")

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')
    
    if status not in ('completed', 'continues', 'announcement'):
        return BadRequest('This status does not exists, please one of this: completed, continues, announcement')
    

    film = Film(title=title, description=description, year=year, rating=rating, status=status, country=country, genre=genre)
    db.session.add(film)
    db.session.commit()

    return redirect(url_for('films_app.detail', film_id=film.id))


@films_app.route('/update/<uuid:film_id>', methods=['GET', 'POST'], endpoint='update')
def update_film(film_id):
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(select(Film).where(Film.id==film_id))

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

    if len(title) >= 200:
        return BadRequest('Length of title must not be greater than 200 symbols')
    
    if len(description) >= 1000:
        return BadRequest('Length of description must not be greater than 1000 symbols')

    if len(genre) >= 150:
        return BadRequest('Length of genre must not be greater than 150 symbols')

    if int(year) > datetime.today().year:
        return BadRequest("Film's year cannot be in the future.")

    if country not in all_countries:
        return BadRequest('This country does not exists, please write full name of your country')
    
    if status not in ('completed', 'continues', 'announcement'):
        return BadRequest('This status does not exists, please one of this: completed, continues, announcement')

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
    if not film_id:
        return BadRequest('Missing required parameters')

    film = db.session.scalar(select(Film).where(
        Film.id == film_id
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
        )
    )

    if film_to_actor_exist:
        raise Conflict(f'Actor is already matched with this film')

    film_to_actor = FilmToActor(film_id=film_id, actor_id=actor_id)
    db.session.add(film_to_actor)
    db.session.commit()

    url_detail = url_for('films_app.detail', film_id=film_id)
    return redirect(url_detail)


@films_app.route('/delete_actor/<uuid:film_id>/<uuid:actor_id>', methods=['POST'])
def delete_actor(film_id, actor_id):

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
