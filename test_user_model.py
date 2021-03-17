"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

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

USER_DATA2 = {
    "username": "TestUser2",
    "email": "test2@gmail.com",
    "password": "$2b$12$l1tVCOm8Kit0adveLw61yOMqYPvIqpyB7kXT3UooJjdPQBjFLpfZS"
}

class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user = User(**USER_DATA)
        user2 = User(**USER_DATA2)
        user.followers.append(user2)
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()

        self.user = user
        self.user2 = user2
        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
        User.query.delete()
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does repr work?"""

        self.assertEqual(self.user.__repr__(),
                f"<User #{self.user.id}: {self.user.username}, {self.user.email}>")

    def test_is_following(self):
        """Does is_following work?"""

        self.assertEqual(self.user2.is_following(self.user), True)
        self.assertEqual(self.user.is_following(self.user2), False)

    def test_is_followed_by(self):
        """Does is_followed_by work?"""

        self.assertEqual(self.user.is_followed_by(self.user2), True)
        self.assertEqual(self.user2.is_followed_by(self.user), False)

    def test_signup(self):
        """Does signup method work?"""

        User.signup(
            username="TestNewUser",
            password="password",
            email="newemail@gmail.com",
            image_url="image")

        self.assertEqual(User.query.count(), 3)

        #Tests for failure when null in non nullable field
        self.assertRaises(TypeError, User.signup(
            username=None,
            password="password",
            email="newemail@gmail.com",
            image_url="image"))

    def test_authenticate(self):
        """Test authentication returns correct user"""
        user = User.authenticate(username="TestUser", password="password")

        self.assertEqual(user, self.user)
        self.assertFalse(
            User.authenticate(username="TestUser", password="blah")
        )
        self.assertFalse(
            User.authenticate(username="blah", password="password")
        )

