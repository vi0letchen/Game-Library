import pytest
from werkzeug.security import check_password_hash

from games.adapters.memory_repository import MemoryRepository
import games.browse.services as services
from games.domainmodel.model import Genre, Publisher, Game, Review, User
import games.authentication.services as auth_services
import games.wishlist.service as wishlist_services


@pytest.fixture
def empty_repo():
    return MemoryRepository()


@pytest.fixture
def sample_repo():
    repo = MemoryRepository()
    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99
    game1.genre = ["Action", "Adventure"]

    game2 = Game(2, "Game 2")
    game2.release_date = "Aug 30, 2023"
    game2.description = "Description for Game 2"
    game2.url = "https://example.com/game2"
    game2.price = 1.99
    game2.genre = ["Adventure"]

    repo.add_game(game1)
    repo.add_game(game2)


    user1 = User("user1", "password1")
    user2 = User("user2", "password2")


    review1 = Review(user1, game1, 4, "Good game")
    review2 = Review(user2, game1, 5, "Excellent!")
    review3 = Review(user1, game2, 3, "Decent game")


    repo.add_review(review1)
    repo.add_review(review2)
    repo.add_review(review3)

    return repo

def test_get_correct_number_of_games(sample_repo):
    num_games = services.get_number_of_games(sample_repo)
    assert num_games == 2


def test_get_paginated_games(sample_repo):
    games = services.get_paginated_games(sample_repo, page_num=1)
    assert len(games) == 2


def test_get_paginated_games_for_pagination2(sample_repo):
    games = services.get_paginated_games(sample_repo, page_num=2)
    assert games == []


def test_get_games_by_nonexistent_genre(sample_repo):
    games = services.get_paginated_games_by_genre(sample_repo, genre_name="Nonexistent Genre", page_num=1)
    assert games == []


def test_search_games_by_genre(sample_repo):
    games = services.get_games_by_genre(sample_repo, genre_name="Action", page_num=10)
    assert len(games) == 0


def test_get_nonexistent_game(sample_repo):
    game = services.get_title_by_id(sample_repo, game_id=999)
    assert game is None


def test_get_date_by_id_nonexistent_game(sample_repo):
    release_date = services.get_date_by_id(sample_repo, game_id=999)
    assert release_date is None


def test_get_description_by_id_nonexistent_game(sample_repo):
    description = services.get_description_by_id(sample_repo, game_id=999)
    assert description == "No description available"


def test_get_url_by_id_nonexistent_game(sample_repo):
    url = services.get_url_by_id(sample_repo, game_id=999)
    assert url is None


def test_get_price_by_id_nonexistent_game(sample_repo):
    price = services.get_price_by_id(sample_repo, game_id=999)
    assert price == 0


def test_get_games_by_genre_pagination(sample_repo):
    games = services.get_games_by_genre(sample_repo, genre_name="Action", page_num=2)
    assert games == []


def test_search_games_by_title_existing_game(sample_repo):
    games = services.search_games_by_title(sample_repo, "Game")
    assert len(games) == 2
    assert games[0].title == "Game 1"


def test_search_games_by_title_existing_game2(sample_repo):
    games = services.search_games_by_title(sample_repo, "Game 1")
    assert len(games) == 1
    assert games[0].title == "Game 1"


def test_search_games_by_title_nonexistent_game(sample_repo):
    games = services.search_games_by_title(sample_repo, "Nonexistent Game")
    assert len(games) == 0


sample_user = User("e", "eeeeeeeee")


def test_get_game_by_invalid_id(sample_repo):
    game = services.get_game_by_id(sample_repo, 1)
    assert game is None


def test_get_average_rating():
    reviews = [
        Review(sample_user, Game(1, "Game 1"), 4, "Good game"),
        Review(sample_user, Game(1, "Game 1"), 5, "Excellent!"),
        Review(sample_user, Game(2, "Game 2"), 3, "Decent game"),
    ]
    average_rating = services.get_average_rating(reviews)
    assert average_rating == 4.0


def test_get_reviews_by_nonexistent_game(sample_repo):
    user1 = User("user1", "password1")
    user2 = User("user2", "password2")
    review1 = Review(user1, Game(1, "Game 1"), 4, "Good game")
    review2 = Review(user2, Game(1, "Game 1"), 5, "Excellent!")
    sample_repo.add_user(user1)
    sample_repo.add_user(user2)

    sample_repo.add_review(review1)
    sample_repo.add_review(review2)


    reviews = services.get_reviews_by_game(sample_repo, (Game(3, "Game 3")))
    assert reviews == []

def test_add_review(sample_repo):
    user = User("user1", "password1")
    auth_services.add_user("user1", "new_password", sample_repo)
    sample_repo.add_review(Review(user,Game(1, "Game 1"), 5, "Excellent!"))
    assert len(sample_repo._MemoryRepository__reviews) == 4

def test_get_review_from_nonexistent_user(sample_repo):
    user = User("user5", "password1")
    assert services.get_reviews_by_user(sample_repo, user) == []

def test_add_user(sample_repo):

    auth_services.add_user("new_user", "new_password", sample_repo)
    assert len(sample_repo._MemoryRepository__users) == 1


def test_get_user(sample_repo):
    user = auth_services.get_user_in_user_type("nonexistent_user", sample_repo)
    assert user == None


def test_get_user_in_user_type(sample_repo):

    auth_services.add_user("new_user", "new_password", sample_repo)
    user = sample_repo._MemoryRepository__users[0]

    user = auth_services.get_user_in_user_type(user.username, sample_repo)
    assert user.username == "new_user"


def test_get_user_password(sample_repo):
    auth_services.add_user("new_user", "new_password", sample_repo)
    user = sample_repo._MemoryRepository__users[0]

    user = auth_services.get_user_in_user_type(user.username, sample_repo)
    assert check_password_hash(user.password, "new_password")


def test_authenticate_user(sample_repo):

    auth_services.add_user("new_user", "new_password", sample_repo)
    user = sample_repo._MemoryRepository__users[0]
    auth_services.authenticate_user(user.username, "new_password", sample_repo)


    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user("sample_user", "new_password", sample_repo)


    with pytest.raises(auth_services.AuthenticationException):
        auth_services.authenticate_user("nonexistent_user", "new_password", sample_repo)

def test_user_to_dict(sample_repo):
    auth_services.add_user("new_user", "new_password", sample_repo)
    user = sample_repo._MemoryRepository__users[0]
    user_dict = auth_services.user_to_dict(user)
    assert user_dict == {'username': user.username, 'password': user._User__password }


def test_get_reviews_by_user(sample_repo):

    user = User("user1", "password1")
    user1_reviews = services.get_reviews_by_user(sample_repo, user)
    assert len(user1_reviews) == 2
    assert user1_reviews[0].rating == 4
    assert user1_reviews[1].rating == 3

def test_get_reviews_by_game(sample_repo):
    game = Game(1, "Game 1")
    game1_reviews = services.get_reviews_by_game(sample_repo, game)
    assert len(game1_reviews) == 2
    assert game1_reviews[0].rating == 4
    assert game1_reviews[1].rating == 5

def test_get_rated_games_for_user(sample_repo):
    user1 = User("user1", "password1")
    user1_rated_games = services.get_rated_games_for_user(sample_repo, user1)
    assert len(user1_rated_games) == 2
    assert "Game 1" in [game.title for game in user1_rated_games]
    assert "Game 2" in [game.title for game in user1_rated_games]

def test_user_already_reviewed_game(sample_repo):
    user1 = User("user1", "password1")
    assert services.user_already_reviewed_game(sample_repo, 1, user1) is False
    assert services.user_already_reviewed_game(sample_repo, 1, "nonexistent_user") is False


def test_add_to_wishlist(sample_repo):

    wishlist_services.add_game_to_wishlist(sample_repo, "user1", 1)
    wishlist_services.add_game_to_wishlist(sample_repo, "user1", 2)
    user_wishlist = wishlist_services.get_game_wishlist(sample_repo, "user1")
    assert len(user_wishlist) == 2


def test_remove_from_wishlist(sample_repo):


    wishlist_services.add_game_to_wishlist(sample_repo, "user1", 1)
    wishlist_services.add_game_to_wishlist(sample_repo,"user1", 2)
    wishlist_services.add_game_to_wishlist(sample_repo,"user1", 3)


    wishlist_services.remove_game_from_wishlist(sample_repo,"user1", 2)
    user_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user1")
    assert len(user_wishlist) == 2


    wishlist_services.remove_game_from_wishlist(sample_repo,"user1", 4)
    user_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user1")
    assert len(user_wishlist) == 2

def test_get_user_wishlist(sample_repo):

    wishlist_services.add_game_to_wishlist(sample_repo,"user1", 1)
    wishlist_services.add_game_to_wishlist(sample_repo,"user1", 2)

    wishlist_services.add_game_to_wishlist(sample_repo,"user2", 3)
    wishlist_services.add_game_to_wishlist(sample_repo,"user2", 4)

    user1_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user1")
    assert len(user1_wishlist) == 2

    user2_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user2")
    assert len(user2_wishlist) == 2

    user3_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user3")
    assert user3_wishlist == []

    user4_wishlist = wishlist_services.get_game_wishlist(sample_repo,"user4")
    assert user4_wishlist == []


def test_get_user_activities_with_data(sample_repo):
    user2 = User("user1", "password1")
    auth_services.add_user("user2", "new_password", sample_repo)
    sample_repo.add_review(Review(user2, Game(1, "Game 1"), 5, "Excellent!"))


    wishlist_services.add_game_to_wishlist(sample_repo, "user2", 1)

    # Test when the user has activities
    activities = auth_services.get_user_activities("user2", sample_repo)

    assert 'rated_games' in activities
    assert 'reviews' in activities
    assert 'wishlist' in activities

    assert len(activities['rated_games'])== 1
    assert len(activities['reviews']) == 1
    assert len(activities['wishlist']) == 1

    assert activities['rated_games'][0].game.game_id == 1
    assert activities['reviews'][0].game.game_id == 1
