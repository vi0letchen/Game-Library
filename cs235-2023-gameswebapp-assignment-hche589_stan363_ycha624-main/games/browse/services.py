from flask import session

from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Game, Genre, Review
from typing import List
import games.adapters.repository as repo
import games.authentication.services as auth_services

GAMES_PER_PAGE = 15


def get_number_of_games(repo: AbstractRepository):
    return repo.get_number_of_games()


def get_paginated_games(repo: AbstractRepository, page_num: int) -> List[dict]:
    all_games = repo.get_games()
    sorted_games = sorted(all_games, key=lambda x: x.title)
    start_index = (page_num - 1) * GAMES_PER_PAGE
    end_index = start_index + GAMES_PER_PAGE
    games = sorted_games[start_index:end_index]

    game_dicts = []
    for game in games:
        game_dict = {
            'game_id': game.game_id,
            'title': game.title,
            'release_date': game.release_date,
            'price': game.price,
            'publisher': game.publisher,
            'genres': [genre.genre_name for genre in game.genres],
            'image': game.image_url,
        }
        game_dicts.append(game_dict)

    return game_dicts


def get_paginated_games_by_genre(repo: AbstractRepository, genre_name: str, page_num: int) -> List[dict]:
    all_games = repo.get_games_by_genre(genre_name)
    sorted_games = sorted(all_games, key=lambda x: x.title)
    start_index = (page_num - 1) * GAMES_PER_PAGE
    end_index = start_index + GAMES_PER_PAGE
    games = sorted_games[start_index:end_index]

    game_dicts = []
    for game in games:
        game_dict = {
            'game_id': game.game_id,
            'title': game.title,
            'release_date': game.release_date,
            'price': game.price,
            'publisher': game.publisher,
            'genres': [genre.genre_name for genre in game.genres],
            'image': game.image_url,
        }
        game_dicts.append(game_dict)
    return game_dicts


def search_games_by_title(repo: AbstractRepository, title_query: str):
    all_games = repo.get_games()
    return [game for game in all_games if title_query.lower() in game.title.lower()]


def search_games_by_id(repo: AbstractRepository, id_query: int):
    all_games = repo.get_games()
    return [game for game in all_games if game.game_id == id_query]


def search_games_by_price(repo: AbstractRepository, id_query: float):
    all_games = repo.get_games()
    return [game for game in all_games if game.price == id_query]


def search_games_by_genres(repo: AbstractRepository, id_query: str):
    all_games = repo.get_games()

    def get_genres(genres):
        return ', '.join([genre.genre_name for genre in genres])

    return [game for game in all_games if id_query in get_genres(game.genres)]


def search_games_by_publisher(repo: AbstractRepository, id_query: str):
    all_games = repo.get_games()
    return [game for game in all_games if id_query in game.publisher.publisher_name]


def get_all_genres(repo: AbstractRepository) -> List[Genre]:
    return repo.get_all_genres()


def get_games_by_genre(repo: AbstractRepository, genre_name: str, page_num: int) -> List[Game]:
    return repo.get_games_by_genre(genre_name)


def get_title_by_id(repo: AbstractRepository, game_id):
    title = repo.get_title_by_id(game_id)
    if title:
        return title
    else:
        return None


def get_date_by_id(repo: AbstractRepository, game_id):
    release_date = repo.get_date_by_id(game_id)
    if release_date:
        return release_date
    else:
        return None


def get_description_by_id(repo: AbstractRepository, game_id):
    description = repo.get_description_by_id(game_id)
    if description:
        return description
    else:
        return "No description available"


def get_url_by_id(repo: AbstractRepository, game_id):
    url = repo.get_url_by_id(game_id)
    if url:
        return url
    else:
        return None


def get_price_by_id(repo: AbstractRepository, game_id):
    price = repo.get_price_by_id(game_id)
    if price:
        return price
    else:
        return 0


def get_game_by_id(repo: AbstractRepository, game_id):
    game = repo.get_game_by_id(game_id)
    if game:
        return game
    else:
        return None


def get_image_url_by_id(repo: AbstractRepository, game_id):
    game = repo.get_image_url_by_id(game_id)
    if game:
        return game
    else:
        return None


def get_average_rating(reviews):
    if not reviews:
        return 0
    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / len(reviews)
    return round(average_rating, 2)


def add_review(repo: AbstractRepository, user, game, rating, comment):
    review = Review(user, game, rating, comment)
    repo.add_review(review)


def get_reviews_by_user(repo: AbstractRepository, user):
    return repo.get_reviews_by_user(user)


def get_reviews_by_game(repo: AbstractRepository, game):
    return repo.get_reviews_by_game(game)


def get_rated_games_for_user(repo: AbstractRepository, user):
    return repo.get_rated_games_for_user(user)


def user_already_reviewed_game(repo: AbstractRepository, game_id, username):
    reviews = repo.get_reviews_by_game_and_user(game_id, username)
    return len(reviews) > 0


"""
class ReviewService:
    def __init__(self, review_repository):
        self.review_repository = review_repository

    def add_review(self, user, game, rating, comment):
        user = auth_services.get_user_in_user_type(session['username'], repo.repo_instance)
        review = Review(user, game, rating, comment)
        self.review_repository.add_review(review)

    def get_reviews_by_user(self, user):
        return self.review_repository.get_reviews_by_user(user)

    def get_reviews_by_game(self, game):
        return self.review_repository.get_reviews_by_game(game)

    def get_rated_games_for_user(self, user):
        return self.review_repository.get_rated_games_for_user(user)

    def user_already_reviewed_game(self, game_id, username):
        reviews = self.review_repository.get_reviews_by_game_and_user(game_id, username)
        return len(reviews) > 0
"""
