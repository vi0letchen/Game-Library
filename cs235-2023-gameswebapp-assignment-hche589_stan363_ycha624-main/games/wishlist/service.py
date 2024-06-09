from games.adapters.repository import AbstractRepository


def get_game_wishlist(repo: AbstractRepository, username):
    wishlist = list()
    for game_id in repo.get_wishlist(username):
        wishlist.append(repo.get_game_by_id(game_id))
    return wishlist


def add_game_to_wishlist(repo: AbstractRepository, username, game_id):
    repo.add_to_wishlist(username, game_id)


def remove_game_from_wishlist(repo: AbstractRepository, username, game_id):
    repo.remove_from_wishlist(username, game_id)


"""
class WishlistService:
    def __init__(self):
        self.wishlist_repo = WishlistRepository()

    def add_to_wishlist(self, username, game_id):
        self.wishlist_repo.add_to_wishlist(username, game_id)

    def remove_from_wishlist(self, username, game_id):
        self.wishlist_repo.remove_from_wishlist(username, game_id)

    def get_user_wishlist(self, username):
        return self.wishlist_repo.get_wishlist(username)
"""
