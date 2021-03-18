"""Message model tests."""


import os
from unittest import TestCase

from models import db, Message, User
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

USER_DATA = {
    "username": "TestUser",
    "email": "test@gmail.com",
    "password": "$2b$12$l1tVCOm8Kit0adveLw61yOMqYPvIqpyB7kXT3UooJjdPQBjFLpfZS",
}

class MessageModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        user = User(**USER_DATA)
        db.session.add(user)
        db.session.commit()

        self.user = user
        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        db.session.commit()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test message",
        )

        self.user.messages.append(m)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(m.user, self.user)

    def test_message_repr(self):
        """Does basic model work?"""

        m = Message(
            text="test message",
        )

        self.user.messages.append(m)
        db.session.commit()

        self.assertEqual(m.__repr__(), f"<Message #{m.id}: {m.text}, {m.user_id}>")

