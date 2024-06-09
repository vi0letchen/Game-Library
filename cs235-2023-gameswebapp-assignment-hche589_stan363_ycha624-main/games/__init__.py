"""Initialize Flask app."""

from pathlib import Path
from flask import Flask
from sqlalchemy import create_engine, NullPool, inspect
from sqlalchemy.orm import sessionmaker, clear_mappers

import games.adapters.repository as repo
from games.adapters.database_repository import SqlAlchemyRepository
from games.adapters.repository_populate import populate

from games.adapters.orm import map_model_to_tables, mapper_registry



def create_app(testing=False):
    """Construct the core application."""

    # Create the Flask app object.
    app = Flask(__name__)

    database_uri = 'sqlite:///games.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Create a database engine and connect it to the specified database
    database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                    echo=False)

    # Create the database session factory using session-maker (this has to be done once, in a global manner)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)

    # Create the SQLAlchemy DatabaseRepository instance for an sqlite3-based repository.
    repo.repo_instance = SqlAlchemyRepository(session_factory)
    data_path = Path('games') / 'adapters' / 'data' / 'games.csv'

    if testing:
        app.config['TESTING'] = True

    if app.config['TESTING'] == 'True' or len(inspect(database_engine).get_table_names()) == 0:
        print("REPOPULATING DATABASE...")
        # For testing, or first-time use of the web application, reinitialise the database.
        clear_mappers()

        # Conditionally create database tables.
        mapper_registry.metadata.create_all(database_engine)
        # Remove any data from the tables.
        for table in reversed(mapper_registry.metadata.sorted_tables):
            with database_engine.connect() as conn:
                conn.execute(table.delete())

        # Generate mappings that map domain model classes to the database tables.
        map_model_to_tables()

        populate(data_path, repo.repo_instance)
        print("REPOPULATING DATABASE... FINISHED")

    else:
        # Solely generate mappings that map domain model classes to the database tables.
        map_model_to_tables()



    with app.app_context():
        # Register the browse blueprint to the app instance.
        from .browse import browse
        app.register_blueprint(browse.browse_blueprint)

        # Register the home blueprint to the app instance.
        from .home import home
        app.register_blueprint(home.home_blueprint)

        # Register the authentication blueprint to the app instance.
        from .authentication import authentication
        app.register_blueprint(authentication.auth_blueprint)

        # Register the wishlist blueprint to the app instance.
        from .wishlist import wishlist
        app.register_blueprint(wishlist.wishlist_blueprint)

        # Register the profile blueprint to the app instance.
        from .profile import profile
        app.register_blueprint(profile.profile_blueprint)

        # Register a callback the makes sure that database sessions are associated with http requests
        # We reset the session inside the database repository before a new flask request is generated
        @app.before_request
        def before_flask_http_request_function():
            if isinstance(repo.repo_instance, SqlAlchemyRepository):
                repo.repo_instance.reset_session()

        # Register a tear-down method that will be called after each request has been processed.
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if isinstance(repo.repo_instance, SqlAlchemyRepository):
                repo.repo_instance.close_session()

    return app


"""
    # Create the MemoryRepository implementation for a memory-based repository.
    repo.repo_instance = MemoryRepository()
    # fill the repository from the provided CSV file
    populate(repo.repo_instance)
"""

