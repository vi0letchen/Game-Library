from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from games.authentication.authentication import login_required
import games.adapters.repository as repo
import games.wishlist.service as wishlist_service

wishlist_blueprint = Blueprint('wishlist_bp', __name__)


@wishlist_blueprint.route('/add_to_wishlist/<game_id>')
@login_required
def add_game_to_wishlist(game_id):
    username = session['username']
    try:
        wishlist_service.add_game_to_wishlist(repo.repo_instance, username, game_id)
    except ValueError as e:
        pass
    return redirect(url_for('games_bp.show_game_detail', game_id=game_id))


@wishlist_blueprint.route('/remove/<game_id>', methods=['POST'])
@login_required
def remove_from_wishlist(game_id):
    username = session['username']
    wishlist_service.remove_game_from_wishlist(repo.repo_instance, username, game_id)
    flash('Game removed from wishlist!', 'success')
    redirect_url = request.form.get('redirect_url')
    return redirect(redirect_url)


@wishlist_blueprint.route('/wishlist')
@login_required
def get_wishlist():
    username = session['username']
    wishlist = wishlist_service.get_game_wishlist(repo.repo_instance, username)
    # wishlist_with_titles = [get_game_by_id(repo.repo_instance, game_id) for game_id in wishlist]

    return render_template('wishlist.html', wishlist=wishlist)
