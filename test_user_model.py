"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase, expectedFailure

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        
        u1 = User.signup(
            username="testuser1",
            email="test1@test.com",
            password="HASHED_PASSWORD1",
            image_url="/static/images/warbler-hero.jpg"
        )
        
        u2 = User.signup(
            username="testuser2",
            email="test2@test.com",
            password="HASHED_PASSWORD2",
            image_url="/static/images/warbler-hero.jpg"
        )
        
        db.session.commit()
        
        self.user1 = u1
        self.user2 = u2

        self.client = app.test_client()
        
    def tearDown(self):
        """Clean up any fouled transaction."""
        
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.user1.messages), 0)
        self.assertEqual(len(self.user1.followers), 0)
        
    def test_user_repr(self):
        """test that the __repr__ method defined on the user class works"""
        
        self.assertEqual(self.user1.__repr__(), f"<User #{self.user1.id}: testuser1, test1@test.com>")
        
    def test_is_following(self):
        """detect if user1 is following user2."""
        
        self.user1.following.append(self.user2)
       
        self.assertIn(self.user2, self.user1.following)
        
    def test_is_not_following(self):
        """detect if user2 is not following user1."""
        
        self.assertNotIn(self.user2, self.user1.following)
        
    def test_is_followed(self):
        """detect if user1 is being followed by user2."""
        
        self.user2.following.append(self.user1)
        
        self.assertIn(self.user2, self.user1.followers)
        
    def test_is_followed(self):
        """detect if user1 is not followed by user2."""
        
        self.assertNotIn(self.user2, self.user1.followers)
        
    def test_create_user(self):
        """detect if a new user is successfully created given valid credentials."""
        
        u3 = User(
            id=3,
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD3"
        )
        
        self.assertEqual(User.query.get(u3), User)
    
    @expectedFailure
    def test_fail_create_user(self):
        """detect if a new user is not successfully created given invalid credentials."""
        
        u3 = User(
            id=1,
            email="test3@test.com",
            username=None,
            password=None
        )
        
        db.session.add(u3)
        db.session.commit()
        
    def test_authenticate_user(self):
        """test that given a valid username and password the user is returned"""
        
        user4 = User.signup(username='testuser4', email='testuser4@test.com', password='HASHED_PASSWORD4', image_url='/static/images/warbler-hero.jpg')
        
        db.session.commit()
        
        au4 = User.authenticate("testuser4", "HASHED_PASSWORD4")
        
        self.assertIs(au4, user4)
        
    def test_authenticate_invalid_username(self):
        """test authentication fails and no user is returned when given an 
        invalid username for testuser1"""
        
        au1 = User.authenticate("testuser4", "HASHED_PASSWORD1")
        
        self.assertIsNot(au1, self.user1)
        
    def test_authenticate_invalid_password(self):
        """test authentication fails and no user is returned when given an 
        invalid password for testuser1"""
        
        au1 = User.authenticate("testuser1", "HASHED_PASSWORD4")
        
        self.assertIsNot(au1, self.user1)

        
        
        