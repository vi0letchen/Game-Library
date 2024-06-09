from abc import ABC
from typing import List, Type, Optional, Any

from sqlalchemy import text, join, select
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound

from games.adapters.orm import wishlist_table, game_wishlist_table, reviews_table, game_genres_table
from games.adapters.repository import AbstractRepository
from games.domainmodel.model import Game, Publisher, Genre, User, Review, Wishlist


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository, ABC):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    # region Game_data
    def get_games(self) -> list[Game]:
        games = self._session_cm.session.query(Game).order_by(Game._Game__game_id).all()
        return games

    def get_game(self, game_id: int) -> Optional[Game]:
        game = None
        try:
            game = self._session_cm.session.query(Game) \
                .filter(Game._Game__game_id == game_id).one()
        except NoResultFound:
            print(f'Game {game_id} was not found')
        return game

    def get_number_of_games(self):
        total_games = self._session_cm.session.query(Game).count()
        return total_games

    def add_game(self, game: Game):
        with self._session_cm as scm:
            scm.session.merge(game)
            scm.commit()

    def add_multiple_games(self, games: List[Game]):
        with self._session_cm as scm:
            for game in games:
                scm.session.merge(game)
            scm.commit()

    # region Publisher data
    def get_publishers(self) -> list[Type[Publisher]]:
        publishers = self._session_cm.session.query(Publisher).all()
        return publishers

    def add_publisher(self, publisher: Publisher):
        with self._session_cm as scm:
            scm.session.merge(publisher)
            scm.commit()

    def add_multiple_publishers(self, publishers: List[Publisher]):
        with self._session_cm as scm:
            for publisher in publishers:
                scm.session.merge(publisher)
            scm.commit()

    # region Genre_data
    def get_all_genres(self) -> list[Type[Genre]]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.merge(genre)
            scm.commit()

    def add_multiple_genres(self, genres: List[str]):
        with self._session_cm as scm:
            for genre in genres:
                scm.session.merge(Genre(genre))
            scm.commit()

    # Game Description region
    def get_game_by_id(self, game_id):
        game = self.get_game(game_id)
        return game

    def get_title_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.title

    def get_date_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.release_date

    def get_description_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.description

    def get_url_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.website_url

    def get_image_url_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.image_url

    def get_price_by_id(self, game_id):
        game = self.get_game(game_id)
        return game.price

    # User region
    def get_user(self, username: str) -> Optional[User]:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(_User__username=username).one()
        except NoResultFound:
            print(f'User {username} was not found')
        return user

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.merge(user)
            scm.commit()

    # wishlist region
    def get_wishlist(self, username):
        # Query the Wishlist table to get wishlist_ids for the given username
        wishlist_ids = self._session_cm.session.query(wishlist_table.c.wishlist_id).filter_by(username=username).all()

        # Extract the wishlist_ids from the query result
        wishlist_ids = [row[0] for row in wishlist_ids]

        if wishlist_ids:
            # Query the game_wishlist table to get the game_ids for the user's wishlists
            game_ids = self._session_cm.session.query(game_wishlist_table.c.game_id) \
                .filter(
                game_wishlist_table.c.wishlist_id.in_(wishlist_ids)
            ).all()

            # Extract the game_ids from the query result
            game_ids = [row[0] for row in game_ids]

            return game_ids

        return []  # Return an empty list if the user's wishlists don't exist

    def add_to_wishlist(self, username, game_id):
        # Create a new wishlist entry
        wishlist_insert = wishlist_table.insert().values(username=username)

        # Execute the insert statement to add the user to the wishlist table
        result = self._session_cm.session.execute(wishlist_insert)

        # Get the wishlist_id from the inserted row
        wishlist_id = result.inserted_primary_key[0]

        # Create a new game_wishlist entry
        game_wishlist_insert = game_wishlist_table.insert().values(game_id=game_id, wishlist_id=wishlist_id)

        # Execute the insert statement to add the game to the user's wishlist
        self._session_cm.session.execute(game_wishlist_insert)

        # Commit the changes
        self._session_cm.session.commit()

    def remove_from_wishlist(self, username, game_id):
        # Query the Wishlist table to get wishlist_ids for the given username
        with self._session_cm as scm:
            wishlist_ids = scm.session.query(wishlist_table.c.wishlist_id).filter_by(username=username).all()

        # Extract the wishlist_ids from the query result
        wishlist_ids = [row[0] for row in wishlist_ids]

        if wishlist_ids:
            delete_statement = game_wishlist_table.delete().where(
                (game_wishlist_table.c.game_id == game_id)
            )

            self._session_cm.session.execute(delete_statement)
            self._session_cm.session.commit()

    # review region
    def add_review(self, review):
        with self._session_cm as scm:
            review.game_id = review.game.game_id
            review.username = review.user.username
            scm.session.add(review)
            scm.commit()

    def get_reviews_by_user(self, user: User) -> list[Review] | None:
        if user is None:
            return None
        with self._session_cm as scm:
            reviews_args = scm.session.query(reviews_table).filter_by(username=user.username).all()
            reviews = []

            for _, comment, rating, game_id, _ in reviews_args:
                game = self.get_game(game_id)
                reviews.append(Review(user, game, rating, comment))
            return reviews

    def get_reviews_by_game(self, game) -> list[Type[Review]]:
        with self._session_cm as scm:
            return scm.session.query(Review).filter_by(game_id=game.game_id).all()

    def get_reviews_by_game_and_user(self, game_id: int, username: str):
        with self._session_cm as scm:
            return scm.session.query(Review).filter_by(game_id=game_id, username=username).all()

    # other
    def get_games_by_genre(self, genre_name: str) -> List[Game]:
        return list(filter(lambda game: genre_name in [genre.genre_name for genre in game.genres], self.get_games()))

    def get_rated_games_for_user(self, user: User) -> List[Game]:
        pass

    def search_games(self, query: str) -> List[Game]:
        pass
