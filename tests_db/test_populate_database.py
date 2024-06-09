import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine.reflection import Inspector

from games import create_app, mapper_registry


@pytest.fixture
def app():
    app = create_app(testing=True)
    return app

@pytest.fixture
def database_engine(app):
    return create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

def test_database_populate_inspect_table_names(database_engine):
    inspector = Inspector.from_engine(database_engine)
    assert inspector.get_table_names() == ['game_genres', 'game_wishlist', 'games', 'genres', 'publishers', 'reviews', 'users', 'wishlist']


def test_database_populate_select_all_users(database_engine):
    new_user_info = {
        'username': 'new_user',
        'password': 'password123'
    }

    with database_engine.connect() as connection:
        users_table = mapper_registry.metadata.tables['users']
        insert_statement = users_table.insert().values(new_user_info)
        connection.execute(insert_statement)
        select_statement = select(users_table.c.username)
        result = connection.execute(select_statement)

        all_usernames = [row[0] for row in result]

        assert all_usernames[0] == "new_user"



def test_database_populate_select_publisher(database_engine):
    new_publisher_info = {
        'name': 'New Publisher'
    }

    with database_engine.connect() as connection:
        publishers_table = mapper_registry.metadata.tables['publishers']
        insert_statement = publishers_table.insert().values(new_publisher_info)
        connection.execute(insert_statement)
        select_statement = select(publishers_table.c.name)
        result = connection.execute(select_statement)

        all_publisher_names = [row[0] for row in result]

        assert all_publisher_names[0] == 'New Publisher'


def test_database_populate_select_wishlist(database_engine):

    new_wishlist_info = {
        'username': 'user1'
    }

    with database_engine.connect() as connection:
        wishlist_table = mapper_registry.metadata.tables['wishlist']
        insert_statement = wishlist_table.insert().values(new_wishlist_info)
        connection.execute(insert_statement)
        select_statement = select(wishlist_table.c.username)
        result = connection.execute(select_statement)

        all_usernames = [row[0] for row in result]

        assert all_usernames[0] == 'user1'


def test_database_populate_select_reviews(database_engine):
    new_review_info = {
        'comment': 'Great game!',
        'rating': 5,
        'game_id': 1,
        'username': 'user1'
    }

    with database_engine.connect() as connection:
        reviews_table = mapper_registry.metadata.tables['reviews']
        insert_statement = reviews_table.insert().values(new_review_info)
        connection.execute(insert_statement)
        select_statement = select(reviews_table.c.comment)
        result = connection.execute(select_statement)

        all_comments = [row[0] for row in result]

        assert all_comments[0] == 'Great game!'


def test_database_populate_select_genres(database_engine):
    new_genre_info = {
        'genre_name': 'New Genre'
    }

    with database_engine.connect() as connection:
        genres_table = mapper_registry.metadata.tables['genres']
        insert_statement = genres_table.insert().values(new_genre_info)
        connection.execute(insert_statement)
        select_statement = select(genres_table.c.genre_name)
        result = connection.execute(select_statement)

        all_genre_names = [row[0] for row in result]

        assert all_genre_names[0] == 'New Genre'

def test_database_populate_select_games(database_engine):
    new_game_info = {
        'game_title': 'New Game',
        'game_price': 19.99,
        'release_date': '2023-01-01',
        'game_description': 'Description',
        'game_image_url': 'image_url',
        'game_website_url': 'website_url',
        'publisher_name': 'Publisher1'
    }

    with database_engine.connect() as connection:
        games_table = mapper_registry.metadata.tables['games']
        insert_statement = games_table.insert().values(new_game_info)
        connection.execute(insert_statement)
        select_statement = select(games_table.c.game_title)
        result = connection.execute(select_statement)

        all_game_titles = [row[0] for row in result]

        assert all_game_titles[0] == 'New Game'


def test_database_populate_select_game_genres(database_engine):
    new_game_genre_info = {
        'game_id': 1,
        'genre_name': 'New Genre'
    }

    with database_engine.connect() as connection:
        game_genres_table = mapper_registry.metadata.tables['game_genres']
        insert_statement = game_genres_table.insert().values(new_game_genre_info)
        connection.execute(insert_statement)
        select_statement = select(game_genres_table.c.game_id, game_genres_table.c.genre_name)
        result = connection.execute(select_statement)

        all_game_genre_associations = [row for row in result]

        assert all_game_genre_associations == [(1, 'New Genre')]

def test_database_populate_select_game_wishlist(database_engine):
    new_game_wishlist_info = {
        'game_id': 1,
        'wishlist_id': 1
    }

    with database_engine.connect() as connection:
        game_wishlist_table = mapper_registry.metadata.tables['game_wishlist']
        insert_statement = game_wishlist_table.insert().values(new_game_wishlist_info)
        connection.execute(insert_statement)
        select_statement = select(game_wishlist_table.c.game_id, game_wishlist_table.c.wishlist_id)
        result = connection.execute(select_statement)

        all_game_wishlist_associations = [row for row in result]

        assert all_game_wishlist_associations == [(1, 1)]