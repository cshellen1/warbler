"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
            
            
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text == "Hello").all()
            self.assertEqual(msg[0].text, "Hello")

    def test_messages_show(self):
        """test the the view to make sure messages are diplayed"""
        
        resp = self.client.get(f"/messages/{self.test_message.id}")
        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<p class="single-message">{self.test_message.text}</p>', html)
        
    def test_messages_destroy(self):
        """test to make sure a message can be deleted and redirects to the correct place"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            new_message = Message(
                text = "delete test message",
                user_id = self.testuser.id
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            resp = c.post(f"/messages/{new_message.id}/delete")
            html = resp.get_data(as_text=True)
            
            # make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # make sure it redirects to the correct place
            self.assertIn(f'<a href="/users/{sess[CURR_USER_KEY]}">/users/{sess[CURR_USER_KEY]}</a>', html)
            # make sure the message no longer exists
            self.assertFalse(Message.query.get(new_message.id))
            
    def test_unauth_message_destroy():
        """test that you can """        
            