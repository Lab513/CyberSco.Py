"""Routes for user authentication."""
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from interface.flask_app import *

from interface.modules.connect.forms import LoginForm, SignupForm
from interface.modules.connect.models import User, db


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    dfp = define_firstpage()
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data, email=form.email.data, website=form.website.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return render_template(
                'intro_page.html', **dfp.__dict__
            )
        flash("A user already exists with that email address.")

    return render_template( "connect/signup.html",
                            title="Create an Account.",
                            form=form,
                            template="signup-page",
                            body="Sign up for a user account.",
                        )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    dfp = define_firstpage()
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return render_template('intro_page.html', **dfp.__dict__)

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return render_template('intro_page.html', **dfp.__dict__)
        flash("Invalid username/password combination")
        return render_template( "connect/login.html",
                                form=form,
                                title="Log in.",
                                template="login-page",
                                body="Log in with your User account.", )

    return render_template( "connect/login.html",
                            form=form,
                            title="Log in.",
                            template="login-page",
                            body="Log in with your User account.", )


@login_manager.user_loader
def load_user(user_id):
    '''
    Check if user is logged-in upon page load
    '''
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    '''
    Redirect unauthorized users to Login page
    '''
    flash("You must be logged in to view that page.")
    form = LoginForm()
    return render_template("connect/login.html",
                            form=form,
                            title="Log in.",
                            template="login-page",
                            body="Log in with your User account.", )
