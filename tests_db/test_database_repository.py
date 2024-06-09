import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, clear_mappers

from games import map_model_to_tables, mapper_registry
from games.adapters import database_repository, repository_populate
from games.adapters.database_repository import SessionContextManager, SqlAlchemyRepository
from games.domainmodel.model import Game, Publisher, Genre, User, Review, Wishlist
import games.adapters.repository as repo

@pytest.fixture
def session_factory():
    clear_mappers()
    engine = create_engine("sqlite:///games.db")
    mapper_registry.metadata.create_all(engine)

    map_model_to_tables()

    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=engine)

    yield session_factory
    mapper_registry.metadata.drop_all(engine)


def test_get_games(session_factory):
    map_model_to_tables()
    repo = SqlAlchemyRepository(session_factory)
    games = repo.get_games()
    assert len(games) == 0

def test_game_functionality(session_factory):
    map_model_to_tables()
    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]

    game2 = Game(2, "Game 2")
    game2.release_date = "Mar 12, 2018"
    game2.description = "Description for Game 1"
    game2.url = "https://example.com/game1"
    game2.price = 0.99
    game2.genre = ["Action", "Adventure"]

    games_to_add = [game1, game2]

    repo = SqlAlchemyRepository(session_factory)
    repo.add_game(game1)

    repo.add_multiple_games(games_to_add)

    games = repo.get_games()
    assert len(games) == 2

    retrieved_game = repo.get_game(game1.game_id)
    assert retrieved_game is not None
    assert retrieved_game.title == "Game 1"

def test_publisher_functionality(session_factory):
    publisher1 = Publisher("Publisher 1")
    publisher2 = Publisher("Publisher 2")
    publishers_to_add = [publisher1, publisher2]

    repo = SqlAlchemyRepository(session_factory)
    repo.add_publisher(publisher1)

    repo.add_multiple_publishers(publishers_to_add)

    publishers = repo.get_publishers()
    assert len(publishers) == 2


def test_genre_functionality(session_factory):
    genre1 = Genre("Action")
    genre2 = Genre("Adventure")

    repo = SqlAlchemyRepository(session_factory)
    repo.add_genre(genre1)
    repo.add_genre(genre2)

    genres = repo.get_all_genres()
    assert len(genres) == 2

def test_game_attribute_methods(session_factory):
    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]

    repo = SqlAlchemyRepository(session_factory)
    repo.add_game(game1)

    game_id = game1.game_id

    assert repo.get_game_by_id(game_id) == game1
    assert repo.get_title_by_id(game_id) == "Game 1"
    assert repo.get_date_by_id(game_id) == "Mar 12, 2018"
    assert repo.get_description_by_id(game_id) == "Description for Game 1"
    assert repo.get_price_by_id(game_id) == 0.99


def test_user_functionality(session_factory):
    user = User(username="user1", password= "password1")
    repo = SqlAlchemyRepository(session_factory)
    repo.add_user(user)

    retrieved_user = repo.get_user("user1")
    assert retrieved_user is not None
    assert retrieved_user.username == "user1"


def test_wishlist_functionality(session_factory):
    user = User(username="user1", password= "password1")
    game = Game(1, "Game 1")
    game.release_date = "Mar 12, 2018"
    game.description = "Description for Game 1"
    game.url = "https://example.com/game1"
    game.price = 0.99
    game.genre = ["Action", "Adventure"]

    repo = SqlAlchemyRepository(session_factory)
    repo.add_user(user)
    repo.add_game(game)

    repo.add_to_wishlist("user2", game.game_id)

    wishlist = repo.get_wishlist("user2")
    assert game.game_id in wishlist

    repo.remove_from_wishlist("user2", game.game_id)

    wishlist = repo.get_wishlist("user2")
    assert game.game_id not in wishlist


def test_review_functionality(session_factory):
    user = User(username="user1", password="password1")
    game = Game(1, "Game 1")
    game.release_date = "Mar 12, 2018"
    game.description = "Description for Game 1"
    game.url = "https://example.com/game1"
    game.price = 0.99
    game.genre = ["Action", "Adventure"]

    review = Review(
        rating=5,
        comment="Great game!",
        user=user,
        game=game,
    )

    repo = SqlAlchemyRepository(session_factory)
    repo.add_user(user)
    repo.add_game(game)

    repo.add_review(review)

    user_reviews = repo.get_reviews_by_user(user)
    game_reviews = repo.get_reviews_by_game(game)
    game_user_reviews = repo.get_reviews_by_game_and_user(game.game_id, user.username)

    assert review in user_reviews
    assert review in game_reviews
    assert review in game_user_reviews