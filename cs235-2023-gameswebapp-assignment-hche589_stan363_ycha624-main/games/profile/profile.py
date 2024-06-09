from flask import Blueprint, render_template, redirect, url_for, session, flash
import games.adapters.repository as repo
from games.authentication.authentication import login_required
from games.profile import services

profile_blueprint = Blueprint(
    'profile_bp', __name__)


@profile_blueprint.route('/profile')
@login_required  # Ensure only authenticated users can access this view
def profile():
    try:
        user = services.get_user(session['username'], repo.repo_instance)
    except services.UnknownUserException:
        flash('Username not found, please login again', 'warning')
        return redirect(url_for('auth_bp.login'))
    activities = services.get_user_activities(user['username'], repo.repo_instance)
    return render_template('profile.html', user=user, activities=activities)

