import os
import sys
from datetime import datetime
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.jwt import create_access_token
from src.database import Base, get_db
from src.main import app
from src.models import User
from src.users.email import email_service
from src.utils import hash

USERNAME = "sanjeebsubedi"
USER_EMAIL = "sanjeebsubedi4@gmail.com"
USER_PASSWORD = "sanjeeb123"

engine = create_engine("sqlite:///./demake.db")
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_session() -> Generator:
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def app_test():
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(app_test, test_session):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_db] = _test_db
    email_service.config.SUPPRESS_SEND = 1
    return TestClient(app_test)


@pytest.fixture(scope="function")
def auth_client(app_test, test_session, user):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_db] = _test_db
    email_service.config.SUPPRESS_SEND = 1
    # data = _generate_tokens(user, test_session)
    data = create_access_token(data={"user_id": str(user.email)})
    client = TestClient(app_test)
    client.headers["Authorization"] = f"Bearer {data['access_token']}"
    return client


@pytest.fixture(scope="function")
def unverified_user(test_session):
    model = User()
    model.username = USERNAME
    model.email = USER_EMAIL
    model.password = hash(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_verified = False
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model


@pytest.fixture(scope="function")
def verified_user(test_session):
    model = User()
    model.username = USERNAME
    model.email = USER_EMAIL
    model.password = hash(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_verified = True
    test_session.add(model)
    test_session.commit()
    test_session.refresh(model)
    return model
