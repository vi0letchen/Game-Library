import pytest
from sqlalchemy import create_engine, text, Table, Column, Integer, String, Text, Float, ForeignKey
from games import map_model_to_tables, mapper_registry
from games.domainmodel.model import Game, Publisher, Genre, User, Review, Wishlist

from sqlalchemy.orm import Session, sessionmaker, clear_mappers


@pytest.fixture
def empty_session():
    clear_mappers()
    engine = create_engine('sqlite://')
    mapper_registry.metadata.create_all(engine)

    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory()
    mapper_registry.metadata.drop_all(engine)


def test_saving_game(empty_session: Session):
    map_model_to_tables()

    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]

    empty_session.add(game1)
    empty_session.commit()

    retrieved_game = empty_session.query(
        Game).filter(Game._Game__game_id == 1).one()

    assert retrieved_game is not None
    assert retrieved_game.title == "Game 1"


def test_saving_publisher(empty_session: Session):
    map_model_to_tables()

    publisher = Publisher(publisher_name="Sample Publisher")

    empty_session.add(publisher)
    empty_session.commit()

    retrieved_publisher = empty_session.query(Publisher).all()

    assert retrieved_publisher is not None
    assert retrieved_publisher[0].publisher_name == "Sample Publisher"


def test_saving_genre(empty_session: Session):
    map_model_to_tables()

    genre = Genre(genre_name="Action")

    empty_session.add(genre)
    empty_session.commit()

    retrieved_genre = empty_session.query(Genre).one()

    assert retrieved_genre is not None
    assert retrieved_genre.genre_name == "Action"


def test_saving_review(empty_session: Session):
    map_model_to_tables()
    user = User(username="user1", password="password1")

    game1 = Game(game_id=1, game_title="Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]

    review = Review(comment="Great game!", rating=5, game=game1, user=user)

    empty_session.add(review)
    empty_session.commit()

    retrieved_review = empty_session.query(Review).one()

    assert retrieved_review is not None
    assert retrieved_review.comment == "Great game!"


def test_saving_user(empty_session: Session):
    map_model_to_tables()

    user = User(username="user1", password="password1")

    empty_session.add(user)
    empty_session.commit()

    retrieved_user = empty_session.query(User).one()

    assert retrieved_user is not None
    assert retrieved_user.username == "user1"


def test_saving_wishlist(empty_session: Session):
    map_model_to_tables()

    user = User(username="user1", password="password1")

    game1 = Game(game_id=1, game_title="Game 1")

    wishlist = Wishlist(user=user)
    wishlist.add_game(game1)

    retrieved_wishlist = empty_session.query(Wishlist).all()

    assert retrieved_wishlist is not None
    assert len(wishlist.list_of_games) == 1


def test_saving_genre_relationship(empty_session: Session):
    map_model_to_tables()

    genre = Genre(genre_name="Action")
    retrieved_game1 = Game(game_id=1, game_title="Game 1")
    retrieved_game1.genres.append(genre)
    empty_session.add(genre)
    empty_session.commit()

    retrieved_genre = empty_session.query(Genre).one()

    assert retrieved_genre is not None
    assert retrieved_genre.genre_name == "Action"
    assert retrieved_game1.genres[0].genre_name == "Action"


def test_game_publisher_relationship(empty_session: Session):
    map_model_to_tables()

    publisher = Publisher(publisher_name="Sample Publisher")

    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]
    game1.publisher = publisher

    empty_session.add(game1)
    empty_session.commit()

    retrieved_game = empty_session.query(
        Game).filter(Game._Game__game_id == 1).one()

    assert retrieved_game is not None
    assert retrieved_game.publisher.publisher_name == "Sample Publisher"


def test_review_user_game_relationship(empty_session: Session):
    map_model_to_tables()

    user = User(username="user1", password="password1")

    game1 = Game(game_id=1, game_title="Game 1")

    review = Review(comment="Great game!", rating=5, game=game1, user=user)

    empty_session.add(review)
    empty_session.commit()

    retrieved_review = empty_session.query(Review).one()

    assert retrieved_review is not None
    assert retrieved_review.game.title == "Game 1"
    assert retrieved_review.user.username == "user1"


def test_wishlist_user_game_relationship(empty_session: Session):
    map_model_to_tables()

    user = User(username="user1", password="password1")

    game1 = Game(game_id=1, game_title="Game 1")

    wishlist = Wishlist(user=user)
    wishlist.add_game(game1)

    retrieved_wishlist = empty_session.query(Wishlist).all()

    assert retrieved_wishlist is not None
    assert len(wishlist.list_of_games) == 1
    assert wishlist.list_of_games[0].title == "Game 1"
