import pytest
from src.app import create_app
from src.extensions import db
from src.models.doctor import DoctorModel

from src.app import create_app


@pytest.fixture
def app():
    app = create_app()  # Create your Flask app using the factory method
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory test DB
    with app.app_context():
        db.create_all()  # Create all tables in the test database

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()  # Returns a client for making HTTP requests in tests

@pytest.fixture
def db_session(app):
    return db.session  # Provides access to the test database session