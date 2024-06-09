import pytest
from games import create_app, Game

from games.adapters.memory_repository import MemoryRepository

@pytest.fixture
def sample_repo():
    repo = MemoryRepository()

    game1 = Game(1, "Game 1")
    game1.release_date = "Mar 12, 2018"
    game1.description = "Description for Game 1"
    game1.url = "https://example.com/game1"
    game1.price = 0.99


    game2 = Game(2, "Game 2")
    game2.release_date = "Aug 30, 2023"
    game2.description = "Description for Game 2"
    game2.url = "https://example.com/game2"
    game2.price = 1.99


    repo.add_game(game1)
    repo.add_game(game2)

    return repo



@pytest.fixture
def client():
    app = create_app(testing=True)
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    with app.test_request_context():
        yield client


def test_user_registration(client):
    response = client.post('/register', data={'username': 'testuser', 'password': 'TestPass123', 'confirm_password': 'TestPass123'})

    assert response.status_code == 302
    assert response.location.endswith('/login')


def test_user_login(client):
    client.post('/register', data={'username': 'testuser', 'password': 'TestPass123', 'confirm_password': 'TestPass123'})
    response = client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})

    assert response.status_code == 302
    assert response.location.endswith('/')


def test_user_logout(client):
    response = client.get('/logout')

    assert response.status_code == 302
    assert response.location.endswith('/')


def test_browsing_games(client):
    response = client.get('/browse')

    assert response.status_code == 200
    assert b'Search for games...' in response.data



def test_add_game_to_wishlist(client):
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})

    game_id = "7940"
    response = client.post(f'/add_to_wishlist/{game_id}', follow_redirects=True)

    assert response.status_code == 200
    assert b'<a id="wishlist" href="/wishlist">Wishlist</a>' in response.data


def test_remove_game_from_wishlist(client):
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})

    game_id = "7940"
    client.post(f'/add_to_wishlist/{game_id}', follow_redirects=True)
    response = client.post(f'/remove/{game_id}', follow_redirects=True)


    assert response.status_code == 200
    assert b'<a id="wishlist" href="/wishlist">Wishlist</a>' in response.data



def test_view_wishlist(client):

    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})

    response = client.get('/wishlist')


    assert response.status_code == 302
    assert b'Redirecting...' in response.data



def test_end_to_end(client):
    # User registration
    response = client.post('/register', data={'username': 'testuser', 'password': 'TestPass123', 'confirm_password': 'TestPass123'})
    assert response.status_code == 302
    assert response.location.endswith('/login')

    # User login
    client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})
    response = client.post('/login', data={'username': 'testuser', 'password': 'TestPass123'})
    assert response.status_code == 302
    assert response.location.endswith('/')

    # Browsing games
    response = client.get('/browse')
    assert response.status_code == 200
    assert b'Search for games...' in response.data

    # Adding a game to the wishlist
    game_id = "7940"
    response = client.post(f'/add_to_wishlist/{game_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'<a id="wishlist" href="/wishlist">Wishlist</a>' in response.data

    # Removing a game from the wishlist
    response = client.post(f'/remove/{game_id}')
    assert response.status_code == 302
    assert b'Redirecting...' in response.data

    # Viewing the wishlist
    response = client.get('/wishlist')
    assert response.status_code == 200
    assert b'<a id="wishlist" href="/wishlist">Wishlist</a>' in response.data

    # User logout
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location.endswith('/')


