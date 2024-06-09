import pytest
from games.domainmodel.model import Game, Review, User
from games.adapters.memory_repository import MemoryRepository



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

def test_add_and_retrieve_game(sample_repo):
    game = Game(3, "Game 3")
    sample_repo.add_game(game)
    retrieved_game = sample_repo.get_games()[2]
    assert retrieved_game == game

def test_get_number_of_games(sample_repo):
    assert sample_repo.get_number_of_games() == 2

def test_get_unique_genres(sample_repo):
    genres = sample_repo.get_all_genres()
    assert len(genres) == 0

def test_get_nonexistent_game_title_by_id(sample_repo):
    game_id = 1
    game_title = sample_repo.get_title_by_id(game_id)
    assert game_title is None

def test_get_nonexistent_date_by_id(sample_repo):
    game_id = 1
    game_date = sample_repo.get_date_by_id(game_id)
    assert game_date is None

def test_search_games_by_title(sample_repo):
    games_found = sample_repo.search_games("Game 1")
    assert len(games_found) == 1
    assert games_found[0].title == "Game 1"

def test_search_games_by_genre_name(sample_repo):
    genre_name = "Action"
    games_found = sample_repo.get_games_by_genre(genre_name)
    assert all(genre_name in game.genres for game in games_found)

def test_get_nonexistent_game_by_id(sample_repo):
    game_id = 999  # Assuming 999 doesn't correspond to any existing game
    game_title = sample_repo.get_title_by_id(game_id)
    assert game_title is None

def test_get_nonexistent_game_date_by_id(sample_repo):
    game_id = 999
    game_date = sample_repo.get_date_by_id(game_id)
    assert game_date is None

def test_get_nonexistent_game_description_by_id(sample_repo):
    game_id = 999
    game_description = sample_repo.get_description_by_id(game_id)
    assert game_description is None

def test_get_nonexistent_game_url_by_id(sample_repo):
    game_id = 999
    game_url = sample_repo.get_url_by_id(game_id)
    assert game_url is None

def test_get_nonexistent_game_price_by_id(sample_repo):
    game_id = 999
    game_price = sample_repo.get_price_by_id(game_id)
    assert game_price is None

def test_search_nonexistent_game_by_title(sample_repo):
    games_found = sample_repo.search_games("Nonexistent Game")
    assert len(games_found) == 0

def test_search_games_by_nonexistent_genre_name(sample_repo):
    genre_name = "Nonexistent Genre"
    games_found = sample_repo.get_games_by_genre(genre_name)
    assert len(games_found) == 0


def test_add_user(sample_repo):
    user = User("new_user", "password123")
    sample_repo.add_user(user)
    assert sample_repo.get_user("new_user") == user

def test_get_user_nonexistent(sample_repo):
    assert sample_repo.get_user("nonexistent_user") is None

def test_get_game_by_id_nonexistent(sample_repo):
    game = sample_repo.get_game_by_id(999)
    assert game is None

def test_add_review(sample_repo):
    # Test adding a review for a nonexistent game
    user = User("new_user", "password123")
    game = Game(999, "Nonexistent Game")
    sample_repo.add_review(Review(user, game, 5, "Awesome!"))
    review = sample_repo.get_reviews_by_game(game)
    assert len(review) == 1


def test_get_reviews_by_user(sample_repo):
    # Test getting reviews by user
    user1 = User("user1", "password1")
    reviews = sample_repo.get_reviews_by_user(user1)

    assert len(reviews) == 2
    assert all(review.user == user1 for review in reviews)


def test_get_reviews_by_game(sample_repo):
    # Test getting reviews by game
    game1 = Game(1, "Game 1")
    reviews = sample_repo.get_reviews_by_game(game1)

    assert len(reviews) == 2
    assert all(review.game == game1 for review in reviews)

def test_get_reviews_by_game_and_user(sample_repo):
    repo = sample_repo
    reviews = repo.get_reviews_by_game_and_user(1, "user1")
    assert len(reviews) == 1
    assert reviews[0].rating == 4
    assert reviews[0].user.username == "user1"
    assert reviews[0].game.title == "Game 1"

def test_add_to_wishlist(sample_repo):
    repo = sample_repo
    username = "user1"
    game_id = 1
    repo.add_to_wishlist(username, game_id)
    user_wishlist = repo.get_wishlist(username)
    assert game_id in user_wishlist


def test_remove_from_wishlist(sample_repo):
    repo = sample_repo

    repo.add_to_wishlist("user1", 1)
    repo.add_to_wishlist("user1", 2)

    repo.remove_from_wishlist("user1", 1)

    user_wishlist = repo.get_wishlist("user1")
    assert 1 not in user_wishlist
    assert 2 in user_wishlist
    repo.remove_from_wishlist("user1", 3)

    user_wishlist = repo.get_wishlist("user1")
    assert 2 in user_wishlist


def test_get_wishlist(sample_repo):
    repo = sample_repo
    repo.add_to_wishlist("user1", 1)
    repo.add_to_wishlist("user1", 2)
    repo.add_to_wishlist("user2", 3)

    user1_wishlist = repo.get_wishlist("user1")
    assert user1_wishlist == [1, 2]

    user2_wishlist = repo.get_wishlist("user2")
    assert user2_wishlist == [3]

    user3_wishlist = repo.get_wishlist("user3")
    assert user3_wishlist == []

    user4_wishlist = repo.get_wishlist("user4")
    assert user4_wishlist == []



