from games.adapters.repository import AbstractRepository
from games.domainmodel.model import User


def get_user_activities(username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    wishlist = list()
    for game_id in repo.get_wishlist(username):
        wishlist.append(repo.get_game_by_id(game_id))
    activities = {
        'reviews': repo.get_reviews_by_user(user),
        'wishlist': wishlist
    }
    return activities


def get_user(username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException
    return user_to_dict(user)


def user_to_dict(user: User):
    user_dict = {
        'username': user.username,
        'password': user.password
    }
    return user_dict


class UnknownUserException(Exception):
    pass
