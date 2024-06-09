from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Text, Float, ForeignKey
)
from sqlalchemy.orm import registry, relationship, clear_mappers

from games.domainmodel.model import Game, Publisher, Genre, User, Review, Wishlist

# global variable giving access to the MetaData (schema) information of the database
mapper_registry = registry()

publishers_table = Table(
    'publishers', mapper_registry.metadata,
    # We only want to maintain those attributes that are in our domain model
    # For publisher, we only have name.
    Column('name', String(255), primary_key=True)  # nullable=False, unique=True)
)

games_table = Table(
    'games', mapper_registry.metadata,
    Column('game_id', Integer, primary_key=True),
    Column('game_title', Text, nullable=False),
    Column('game_price', Float, nullable=False),
    Column('release_date', String(50), nullable=False),
    Column('game_description', String(255), nullable=True),
    Column('game_image_url', String(255), nullable=True),
    Column('game_website_url', String(255), nullable=True),
    Column('publisher_name', ForeignKey('publishers.name')),
)

genres_table = Table(
    'genres', mapper_registry.metadata,
    # For genre again we only have name.
    Column('genre_name', String(64), primary_key=True, nullable=False)
)

game_genres_table = Table(
    'game_genres', mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('game_id', ForeignKey('games.game_id')),
    Column('genre_name', ForeignKey('genres.genre_name'))
)

users_table = Table(
    'users', mapper_registry.metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
)

reviews_table = Table(
    'reviews', mapper_registry.metadata,
    Column('review_id', Integer, primary_key=True, autoincrement=True),
    Column('comment', String(255), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('game_id', ForeignKey('games.game_id')),
    Column('username', ForeignKey('users.username')),
)

wishlist_table = Table(
    'wishlist', mapper_registry.metadata,
    Column('wishlist_id', Integer, primary_key=True, autoincrement=True),
    Column('username', ForeignKey('users.username')),

)

game_wishlist_table = Table(
    'game_wishlist', mapper_registry.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique=False),
    Column('game_id', ForeignKey('games.game_id')),
    Column('wishlist_id', ForeignKey('wishlist.wishlist_id')),
)


def map_model_to_tables():
    clear_mappers()

    mapper_registry.map_imperatively(Game, games_table, properties={
        '_Game__game_id': games_table.c.game_id,
        '_Game__game_title': games_table.c.game_title,
        '_Game__price': games_table.c.game_price,
        '_Game__release_date': games_table.c.release_date,
        '_Game__description': games_table.c.game_description,
        '_Game__image_url': games_table.c.game_image_url,
        '_Game__website_url': games_table.c.game_website_url,
        '_Game__publisher': relationship(Publisher),
        '_Game__reviews': relationship(Review, back_populates='_Review__game_id'),
        '_Game__genres': relationship(Genre, secondary=game_genres_table),

    })

    mapper_registry.map_imperatively(Publisher, publishers_table, properties={
        '_Publisher__publisher_name': publishers_table.c.name,
    })

    mapper_registry.map_imperatively(Genre, genres_table, properties={
        '_Genre__genre_name': genres_table.c.genre_name,
    })

    mapper_registry.map_imperatively(User, users_table, properties={
        '_User__username': users_table.c.username,
        '_User__password': users_table.c.password,
        '_User__reviews': relationship(Review, back_populates='_Review__username'),
        '_User__wishlist': relationship(Wishlist, back_populates='_Wishlist__username'),
    })

    mapper_registry.map_imperatively(Review, reviews_table, properties={
        '_Review__comment': reviews_table.c.comment,
        '_Review__rating': reviews_table.c.rating,
        '_Review__game_id':relationship(Game, back_populates='_Game__reviews'),
        '_Review__username': relationship(User, back_populates='_User__reviews'),
    })

    mapper_registry.map_imperatively(Wishlist, wishlist_table, properties={
        '_Wishlist__list_of_games': relationship(Game, secondary=game_wishlist_table),
        '_Wishlist__username': relationship(User, back_populates='_User__wishlist'),
    })

