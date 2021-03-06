import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from functools import wraps

from forms import UserAddForm, LoginForm, MessageForm, EditUserForm, ChangePasswordForm
from models import db, connect_db, User, Message

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL_CORRECTED', 'postgresql:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/"), 403
        return func(*args, **kwargs)
    return wrapper


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    # access g in templates, g only lives for life of request
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Successfully logged out", "success")
    return redirect('/')

##############################################################################
# General user routes:


@app.route('/users')
@authenticate
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
@authenticate
def users_show(user_id):
    """Show user profile."""

    # check whether private, if private, check whether logged in user following the account
    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/following')
@authenticate
def show_following(user_id):
    """Show list of people this user is following."""


    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
@authenticate
def users_followers(user_id):
    """Show list of followers of this user."""

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
@authenticate
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    want_to_follow_user = User.query.get_or_404(follow_id)
    if want_to_follow_user.private:
        # =========== NEED TO IMPLEMENT ====================
        # send them a request to follow
        want_to_follow_user.from_users.append(g.user) 
        db.session.commit()
        flash("Your request has been sent", "success")
        return redirect(f"/users/{g.user.id}/following")

    g.user.following.append(want_to_follow_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")

@app.route('/users/approve/<int:made_request_id>/<int:approver_id>')
@authenticate
def approve_follow(made_request_id, approver_id):
    """Appprove a follow for the currently-logged-in user."""

    if not g.user.id == approver_id:
        flash("Access unauthorized.", "danger")
        return redirect("/"), 403

    wanted_to_follow_user = User.query.get_or_404(made_request_id)
    g.user.followers.append(wanted_to_follow_user)
    g.user.from_users.remove(wanted_to_follow_user)
    db.session.commit()

    flash(f"Follow request from {wanted_to_follow_user.username} approved.", "success")
    return redirect(f"/users/{g.user.id}/followers")

@app.route('/users/reject/<int:made_request_id>/<int:approver_id>')
@authenticate
def reject_follow(made_request_id, approver_id):
    """Reject a follow for the currently-logged-in user."""

    if not g.user.id == approver_id:
        flash("Access unauthorized.", "danger")
        return redirect("/"), 403

    wanted_to_follow_user = User.query.get_or_404(made_request_id)
    g.user.from_users.remove(wanted_to_follow_user)
    db.session.commit()
    flash(f"Follow request from {wanted_to_follow_user.username} rejected.", "success")

    return redirect(f"/users/{g.user.id}")

@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
@authenticate
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
@authenticate
def profile():
    """Update profile for current user."""

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data
            g.user.header_image_url = form.header_image_url.data
            g.user.bio = form.bio.data
            g.user.private = form.private.data
            db.session.commit()
            return redirect(f'/users/{g.user.id}')
        flash('Incorrect password', 'danger')
    return render_template('users/edit.html', user_id=g.user.id, form=form)

@app.route('/users/delete', methods=["POST"])
@authenticate
def delete_user():
    """Delete user."""

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

@app.route('/users/<int:user_id>/likes')
@authenticate
def show_likes(user_id):
    """Show list of user's likes"""


    user = User.query.get_or_404(user_id)

    return render_template('users/likes.html', user=user)

@app.route('/users/<int:user_id>/password', methods=["GET", "POST"])
@authenticate
def change_password(user_id):
    """Change password"""

    if g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/"), 403

    form = ChangePasswordForm()

    if form.validate_on_submit():
        if g.user.validate_change_password(form.cur_pass.data, form.new_pass1.data, form.new_pass2.data):
            db.session.commit()
            flash("Successfully changed password", "success")
            return redirect("/")

    return render_template("/users/change_pass.html", form=form)


##############################################################################
# Messages routes:


@app.route('/messages/<int:message_id>', methods=["GET"])
@authenticate
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
@authenticate
def messages_destroy(message_id):
    """Delete a message."""

    msg = Message.query.get_or_404(message_id)

    if g.user != msg.user:
        flash("Access unauthorized.", "danger")
        return redirect("/"), 403

    # Bug Found added 404 Need to check if user is the author
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

# MESSAGE API's

@app.route('/api/messages/new', methods=["POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return jsonify({'result': 'fail'}), 403

    text = request.json["text"]
    msg = Message(text=text)
    g.user.messages.append(msg)
    db.session.commit()

    return jsonify({'result': 'success',
                    'msg': msg.serialize(),
                    'user': g.user.serialize()})

@app.route('/api/messages/<int:message_id>/like', methods=["POST"])
def messages_toggle_like(message_id):
    """ Like a message """

    if not g.user:
        return jsonify({'result': 'fail'}), 403

    msg = Message.query.get_or_404(message_id)

    if msg in g.user.likes:
        g.user.likes.remove(msg)
    else:
        g.user.likes.append(msg)
    db.session.commit()

    return jsonify({'result': 'success'}), 200



##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users and logged in user
    """

    if g.user:
        # wth going on here?
        ids_to_pull_from = [fol_user.id for fol_user in g.user.following] + [g.user.id]
        messages = (Message
                    .query
                    # need filter for in and like
                    # filter_by doesn't need the object passed again
                    .filter(Message.user_id.in_(ids_to_pull_from))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
