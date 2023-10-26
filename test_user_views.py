"""tests for user views"""

import pdb
import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        
        m = Message(
            text = "test message",
            user_id = self.testuser.id
        )
        
        db.session.add(m)
        db.session.commit()
        
        self.test_message = m

    def test_following_authentication(self):
        """test that the logged in user is not able to see another users following page"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get("/users/99999999/following")
            html = resp.get_data(as_text=True)
            
            # make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # make sure it redirects to the correct place
            self.assertIn('<a href="/">/</a>', html)
            
    def test_followers_authentication(self):
        """test that the logged in user is not able to see another users followed page"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get("/users/99999999/followers")
            html = resp.get_data(as_text=True)
            
            # make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # make sure it redirects to the correct place
            self.assertIn('<a href="/">/</a>', html)
            
    def test_list_users(self):
        """test that all users are displayed"""
        
        resp = self.client.get("/users")
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<div class="card user-card">', html)
        
    def test_users_show(self):
        """ Test that a user profile is displayed including the users messages."""
        
        resp = self.client.get(f"/users/{self.testuser.id}")
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<h4 id="sidebar-username">@{self.testuser.username}</h4>', html)
        self.assertIn(f'<p>{self.test_message.text}</p>', html)
        
            
    
            
            
            