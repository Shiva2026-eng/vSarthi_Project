import os
import sys

# Ensure backend root directory is on sys.path for direct pytest invocation
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set environment variables for testing before importing application modules
os.environ["SECRET_KEY"] = "test_secret_key_12345"

os.environ["ALGORITHM"] = "HS256"
os.environ["TENANT_ID"] = "common"
os.environ["CLIENT_ID"] = "test-client-id"
os.environ["CLIENT_SECRET"] = "test-client-secret"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from uuid import uuid4
from passlib.context import CryptContext

from database import Base
from dependencies import get_db
from main import app
from models.User import User
from utilities.accessToken import create_access_token
from datetime import timedelta

# SQLite in-memory engine with StaticPool to keep connection open across threads
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user_id = uuid4()
    user = User(
        id=user_id,
        name="Test User",
        email=f"test_{user_id.hex[:6]}@example.com",
        password_hash=bcrypt_context.hash("testpassword123"),
        connected_account={"outlook": False},
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(
        email=test_user.email,
        user_id=test_user.id,
        life=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}
