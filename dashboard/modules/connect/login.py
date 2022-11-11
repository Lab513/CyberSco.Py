from flask import render_template
from flask_login import current_user, login_required, logout_user
from dashboard.modules.connect.forms import LoginForm, SignupForm
from dashboard.flask_app import *

@app.route("/", methods=["GET"])
@login_required
def first_page():
    '''
    Page after login..
    '''
    dfp = define_firstpage()
    return render_template( 'index_folder.html', **dfp.__dict__ )


@app.route("/logout")
@login_required
def logout():
    '''
    Return to the login page..
    '''
    print(f'Session finished for use {current_user}')
    print('Returning to the Login page')
    form = SignupForm()
    logout_user()
    return render_template("connect/login.html",
                            form=form,
                            title="Log in.",
                            template="login-page",
                            body="Log in with your User account.", )
