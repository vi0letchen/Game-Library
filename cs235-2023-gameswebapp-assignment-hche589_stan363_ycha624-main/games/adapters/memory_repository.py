from typing import List
from games.domainmodel.model import Game, Genre, User, Review, Wishlist
from games.adapters.repository import AbstractRepository
from games.adapters.datareader.csvdatareader import GameFileCSVReader
from bisect import insort_left

import os

GAMES_PER_PAGE = 15


class MemoryRepository(AbstractRepository):

    def __init__(self):
        self.__games = list()
        self.__dataset_of_genres = list()
        self.__dataset_of_games = list()
        self.__users = list()
        self.__reviews = list()
        self.__wishlist = dict()

    def add_game(self, game: Game):
        if isinstance(game, Game):
            # When inserting the game, keep the game list sorted alphabetically by the id.
            # Games will be sorted by game due to __lt__ method of the Game class.
            insort_left(self.__games, game)

    def get_games(self) -> List[Game]:
        return self.__games

    def get_number_of_games(self):
        return len(self.__games)

    def set_genres(self, genres):
        self.__dataset_of_genres = genres

    def set_games(self, games):
        self.__dataset_of_games = games

    def search_games(self, query: str) -> List[Game]:
        return [game for game in self.__games if query.lower() in game.title.lower()]

    def get_all_genres(self) -> List[Genre]:
        return list(self.__dataset_of_genres)

    def get_games_by_genre(self, genre_name: str) -> List[Game]:
        return [game for game in self.__dataset_of_games if genre_name in game.genres]

    def get_title_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                return game.title

    def get_date_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                return game.release_date

    def get_description_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                return game.description

    def get_url_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                return game.url

    def get_price_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                if game.price is None:
                    return 0
                return game.price

    def add_user(self, user: User):
        self.__users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self.__users if user.username == username), None)

    def get_game_by_id(self, game_id):
        for game in self.__dataset_of_games:
            if game_id == game.game_id:
                return game

    def add_review(self, review):
        self.__reviews.append(review)

    def get_wishlist(self, username):
        if username not in self.__wishlist:
            self.__wishlist[username] = []
        return self.__wishlist[username]

    def add_to_wishlist(self, username, game_id):
        if username not in self.__wishlist:
            self.__wishlist[username] = []
        if int(game_id) not in self.__wishlist[username]:
            self.__wishlist[username].append(int(game_id))

    def remove_from_wishlist(self, username, game_id):
        if username in self.__wishlist and int(game_id) in self.__wishlist[username]:
            self.__wishlist[username].remove(int(game_id))

    def get_reviews_by_user(self, user):
        return [review for review in self.__reviews if review.user == user]

    def get_reviews_by_game(self, game):
        return [review for review in self.__reviews if review.game == game]

    def get_reviews_by_game_and_user(self, game_id: int, username: str):
        filtered_reviews = [
            review for review in self.__reviews
            if review.game.game_id == game_id and review.user.username == username
        ]

        return filtered_reviews


def populate(repo: AbstractRepository):
    dir_name = os.path.dirname(os.path.abspath(__file__))
    games_file_name = os.path.join(dir_name, "data/games.csv")
    reader = GameFileCSVReader(games_file_name)

    reader.read_csv_file()

    games = reader.dataset_of_games
    genres = reader.dataset_of_genres

    # Add games to the repo
    for game in games:
        repo.add_game(game)

    repo.__dataset_of_genres = genres
    repo.__dataset_of_games = games
    repo.set_genres(genres)
    repo.set_games(games)
