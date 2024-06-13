import unittest
import datetime
from app import create_app, db
from models import Actor

class ActorsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_actors(self):
        response = self.client.get('/actors/')
        self.assertEqual(response.status_code, 200)

    def test_add_actor(self):
        data = {
            'actor-full-name': 'John Doe',
            'actor-birth-date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'actor-sex': 'Male',
            'actor-country': 'United States',
            'actor-death': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        response = self.client.post('/actors/add/', data=data)
        self.assertEqual(response.status_code, 302)

        actor = db.session.query(Actor).filter_by(full_name='John Doe').first()
        self.assertIsNotNone(actor)

    def test_update_actor(self):
        actor = Actor(full_name='Jane Smith', birth_date=datetime.datetime(1990, 5, 20), sex='Female', country='Canada')
        db.session.add(actor)
        db.session.commit()

        data = {
            'actor-new-full-name': 'Jane Johnson',
            'actor-new-birth-date': datetime.datetime(1992, 7, 15).strftime('%Y-%m-%d'),
            'actor-new-sex': 'Female',
            'actor-new-country': 'United Kingdom',
            'actor-new-death': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        response = self.client.post(f'/actors/update/{actor.id}', data=data)
        self.assertEqual(response.status_code, 302)

        updated_actor = db.session.query(Actor).filter_by(full_name='Jane Johnson').first()
        self.assertIsNotNone(updated_actor)
        self.assertEqual(updated_actor.country, 'United Kingdom')

    def test_delete_actor(self):
        actor = Actor(full_name='Alice Brown', birth_date=datetime.datetime(1985, 3, 10), sex='Female', country='Australia')
        db.session.add(actor)
        db.session.commit()

        response = self.client.post(f'/actors/delete/{actor.id}')
        self.assertEqual(response.status_code, 302)

        deleted_actor = db.session.query(Actor).filter_by(full_name='Alice Brown').first()
        self.assertIsNone(deleted_actor)

if __name__ == '__main__':
    unittest.main()
