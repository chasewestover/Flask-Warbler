"""User View tests."""

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

from app import app, do_login, do_logout
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

class UserViewTestCase(TestCase):
    """Test views for users"""

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

    def test_user_signup_success(self):
        """Does user signup work?"""

        with self.client as client:
            resp = client.post("/signup",
                data={
                    "username": "TestNewUser",
                    "email": "testnew@gmail.com",
                    "password": "password"},
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.count(), 3)
            self.assertIn("<p>@TestNewUser</p", html)

    # def test_user_signup_dupe_user_fail(self):
    #     """Does user signup return failed signup properly when same username"""

    #     with self.client as client:
    #         url = "/signup"
    #         data = {
    #             "username": "TestUser",
    #             "email": "testnew@gmail.com",
    #             "password": "password"
    #         }
    #         resp = client.post(url, data=data, follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertEqual(User.query.count(), 2)
    #         # self.assertIn("Username already taken", html)

    def test_user_signup_password_fail(self):
        """Does user signup return failed signup properly when pw too short"""

        with self.client as client:
            url = "/signup"
            data = {
                "username": "TestNewUser",
                "email": "testnew@gmail.com",
                "password": "pass"
            }
            resp = client.post(url, data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.count(), 2)
            self.assertIn("Field must be at least 6 characters long.", html)

    def test_user_followers_page(self):
        """ Can you see follower pages for every user when logged in"""

        with self.client as client:
            #Check that you can't access if logged out
            resp = client.get(f"/users/{self.user2.id}/following")
            self.assertEqual(resp.status_code, 403)

            do_login(self.user)
            resp = client.get(f"/users/{self.user2.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.user.username}", html)

    def test_user_following_page(self):
        """ Can you see following page for every user when logged in"""

        with self.client as client:
            #Check that you can't access if logged out
            resp = client.get(f"/users/{self.user2.id}/followers")
            self.assertEqual(resp.status_code, 403)

            do_login(self.user)
            resp = client.get(f"/users/{self.user.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.user2.username}", html)

    def test_user_add_message(self):
        """ Can user add message properly when user logged in"""

        with self.client as client:
            #Check that you can't post if logged out
            url = "/messages/new"
            resp = client.post(url, data={"text": "Test message"})
            self.assertEqual(resp.status_code, 403)

            do_login(self.user)
            resp = client.post(url, data={"text": "Test message"})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test message", html)

