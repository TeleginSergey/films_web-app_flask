from datetime import date, datetime
from uuid import UUID, uuid4
import pycountry
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


db = SQLAlchemy()

class UUIDMixin:
    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

class FilmToActor(UUIDMixin, db.Model):
    __tablename__ = 'films_actors'

    film_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('films.id'))
    actor_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('actors.id'))

    film = relationship('Film', back_populates='actors')
    actor = relationship('Actor', back_populates='films')

    __table_args__ = (
        UniqueConstraint('film_id', 'actor_id', name='films_actors_film_actor_ids_unique'),
    )



all_countries = [country.name for country in pycountry.countries]
countries_sql =''
for country in all_countries:
    if "'" in country:
        country = country.replace("'", "")
    countries_sql += f"'{country}',"
countries_sql = countries_sql[:-1]


class Film(UUIDMixin, db.Model):
    __tablename__ = 'films'

    title = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    country = db.Column(db.String)
    status = db.Column(db.String)
    genre = db.Column(db.String(150))
    actors = relationship('FilmToActor', back_populates='film')

    # __table_args__ = (
    #     CheckConstraint('CHAR_LENGTH(title) < 200', name='films_check_length_title'),
    #     CheckConstraint('CHAR_LENGTH(genre) < 150', name='films_check_length_genre'),
    #     CheckConstraint('CHAR_LENGTH(description) < 1000', name='films_check_length_description'),
    #     CheckConstraint('year < extract(year from CURRENT_DATE) + 1', name='films_range_check_year'),
    #     CheckConstraint(f'country IN ({countries_sql})', name='films_check_country'),
    #     CheckConstraint("status IN ('completed', 'continues', 'announcement')", name='films_check_valid_status'),
    # )

class Actor(UUIDMixin, db.Model):
    __tablename__ = 'actors'

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = db.Column(db.String)
    birth_date = db.Column(db.Date)
    sex = db.Column(db.String)
    death = db.Column(db.Date)
    country = db.Column(db.String)

    films = relationship('FilmToActor', back_populates='actor')

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = datetime.today().date()
        if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
            return today.year - self.birth_date.year - 1
        return today.year - self.birth_date.year

    @property
    def all_films(self):
        return len(self.films)

    # __table_args__ = (
    #     CheckConstraint("sex IN ('Male', 'Female')", name='actors_check_valid_sex'),
    #     CheckConstraint('birth_date <= current_date', name='actors_check_birth_date_not_in_future'),
    #     CheckConstraint('death <= current_date', name='actors_check_death_date_not_in_future'),
    #     CheckConstraint('death IS NULL OR death >= birth_date', name='actors_check_death_after_birth'),
    #     CheckConstraint(f'country IN ({countries_sql})', name='actors_check_country'),
    # )
