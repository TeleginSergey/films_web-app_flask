"""Module for testing films view."""
import datetime
import unittest

from app import create_app, db
from models import Film


class FilmsTestCase(unittest.TestCase):
    """Test case for testing Film related functionalities."""

    def setUp(self):
        """Set up testing environment before running each test method."""
        self.app = create_app('config.TestConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down testing environment after running each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_films(self):
        """Test the endpoint to get a list of films."""
        response = self.client.get('/films/')
        self.assertEqual(response.status_code, 200)

    def test_add_film(self):
        """Test adding a new film to the database."""
        data = {
            'film-title': 'Test Film',
            'film-description': 'Test description',
            'film-country': 'United States',
            'film-year': str(datetime.datetime.now().year),
            'film-rating': '8.5',
            'film-status': 'completed',
            'film-genre': 'Action',
        }
        response = self.client.post('films/add/', data=data)
        self.assertEqual(response.status_code, 302)

        film = db.session.query(Film).filter_by(title='Test Film').first()
        self.assertIsNotNone(film)

    def test_update_film(self):
        """Test updating an existing film in the database."""
        film = Film(title='Old Title', description='Old Description', year=2000)
        db.session.add(film)
        db.session.commit()

        data = {
            'film-new-title': 'New Title',
            'film-new-description': 'New Description',
            'film-new-country': 'United Kingdom',
            'film-new-year': '1995',
            'film-new-rating': '9.0',
            'film-new-status': 'continues',
            'film-new-genre': 'Comedy',
        }
        response = self.client.post(f'films/update/{film.id}', data=data)
        self.assertEqual(response.status_code, 302)

        updated_film = db.session.query(Film).filter_by(title='New Title').first()
        self.assertIsNotNone(updated_film)
        self.assertEqual(updated_film.year, 1995)

    def test_delete_film(self):
        """Test deleting an existing film from the database."""
        film = Film(title='Test Film', description='Test description', year=2005)
        db.session.add(film)
        db.session.commit()

        response = self.client.post(f'films/delete/{film.id}')
        self.assertEqual(response.status_code, 302)

        deleted_film = db.session.query(Film).filter_by(title='Test Film').first()
        self.assertIsNone(deleted_film)


if __name__ == '__main__':
    unittest.main()
