"""Message model tests"""

import os
from unittest import TestCase, expectedFailure
from models import db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.drop_all()
db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for messages."""
    
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        
        u1 = User(
            id = 1,
            username="testuser1",
            email="test1@test.com",
            password="HASHED_PASSWORD1",
            image_url="/static/images/warbler-hero.jpg"
        )
        
        m1 = Message(
            text = "test message 1",
            user_id = 1
        )
    
        db.session.add(u1)
        db.session.add(m1)
        db.session.commit()
        
        self.user1 = u1
        self.message1 = m1

        self.client = app.test_client()
    
    def tearDown(self):
        """clean up any broken transactions"""
        
        db.session.rollback()
        
    def test_message_model(self):
        """basic test to make sure the message model is working"""
        
        self.assertEqual(self.message1.user_id, 1)
        self.assertEqual(self.message1.text, "test message 1")
        self.assertTrue(self.message1.timestamp)
        self.assertTrue(self.message1.id)
        
    def test_create_message(self):
        """given valid credentials a new message is returned"""
        
        m2 = Message(
            text = "test message 2",
            user_id = 1
        )
        
        db.session.add(m2)
        db.session.commit()
        
        self.assertTrue(Message.query.get(m2.id))
        
    @expectedFailure
    def test_text_fail_create_message(self):
        """detect if a new message missing the text component is not successfully created."""
        
        m3 = Message(
            text=None,
            user_id=1
        )
        
        db.session.add(m3)
        db.session.commit()

    @expectedFailure        
    def test_user_fail_create_message(self):
            """detect if a new message which is missing a valid user is not successfully created."""
        
            m4 = Message(
            text="test message 4",
            user_id=3
            )
        
            db.session.add(m4)
            db.session.commit()
            
    def test_message_user_association(self):
        """test that a user is returned when accessing message.user"""
        
        self.assertIsInstance(self.message1.user, User)
        
        