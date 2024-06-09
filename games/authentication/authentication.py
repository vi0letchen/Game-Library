from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField, validators, BooleanField, ValidationError
from password_validator import PasswordValidator

import games.authentication.services as services
import games.adapters.repository as repo

# Configure Blueprint
auth_blueprint = Blueprint('auth_bp', __name__)


class PasswordValid:
    def __init__(self):
        # Define all individual error messages
        self.messages = {
            'min_length': u'Your password must be at least 8 characters long.',
            'uppercase': u'Your password must contain at least one upper case letter.',
            'lowercase': u'Your password must contain at least one lower case letter.',
            'digits': u'Your password must contain at least one digit.'
        }

    def __call__(self, form, field):
        schema = PasswordValidator()
        password = field.data

        # Check each criterion and raise specific error messages
        if len(password) < 8:
            raise ValidationError(self.messages['min_length'])

        if not any(char.isupper() for char in password):
            raise ValidationError(self.messages['uppercase'])

        if not any(char.islower() for char in password):
            raise ValidationError(self.messages['lowercase'])

        if not any(char.isdigit() for char in password):
            raise ValidationError(self.messages['digits'])


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired(message='Your user name is required')])
    password = PasswordField('Password', [
        validators.DataRequired(message='Your password is required'),
        PasswordValid()
    ])
    confirm_password = PasswordField('Confirm Password', [validators.EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    user_name_not_unique = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to attempt to add the new user.
        try:
            services.add_user(form.username.data, form.password.data, repo.repo_instance)

            # All is well, redirect the user to the login page.
            return redirect(url_for('auth_bp.login'))
        # Please test after changing
        except services.NameNotUniqueException:
            user_name_not_unique = 'Username is already exist'

    # For a GET or a failed POST request, return the Registration Web page.
    return render_template(
        'register.html',
        title='Register',
        form=form,
        user_name_error_message=user_name_not_unique,
        handler_url=url_for('auth_bp.register'),
    )


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name_not_recognised = None
    password_does_not_match_user_name = None

    if form.validate_on_submit():
        # Successful POST, i.e. the username and password have passed validation checking.
        # Use the service layer to lookup the user.
        try:
            user = services.get_user(form.username.data, repo.repo_instance)

            # Authenticate user.
            services.authenticate_user(user['username'], form.password.data, repo.repo_instance)

            # Initialise session and redirect the user to the home page.
            session.clear()
            session['username'] = user['username']
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home_bp.home'))

        except services.UnknownUserException:
            # Username not known to the system, set a suitable error message.
            user_name_not_recognised = 'Invalid username, please try again'

        except services.AuthenticationException:
            # Authentication failed, set a suitable error message.
            password_does_not_match_user_name = 'Invalid password, please try again'

    # For a GET or a failed POST, return the Login Web page.
    return render_template(
        'login.html',
        title='Login',
        user_name_error_message=user_name_not_recognised,
        password_error_message=password_does_not_match_user_name,
        form=form,
    )


@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('home_bp.home'))


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'username' not in session:
            flash('You should login first!', 'warning')
            return redirect(url_for('auth_bp.login'))
        return view(*args, **kwargs)

    return wrapped_view
