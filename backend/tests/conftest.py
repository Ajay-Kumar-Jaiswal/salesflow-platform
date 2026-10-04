import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.customer import Customer
from app.core.security import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    user = User(
        name="Admin User",
        email="admin@salesflow.com",
        hashed_password=get_password_hash("AdminPass123!"),
        role="ADMIN"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sales_rep_user(db):
    user = User(
        name="Alex Rep",
        email="alex@salesflow.com",
        hashed_password=get_password_hash("RepPass123!"),
        role="SALES_REP"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": admin_user.email, "user_id": admin_user.id, "role": "ADMIN"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def rep_headers(sales_rep_user):
    token = create_access_token({"sub": sales_rep_user.email, "user_id": sales_rep_user.id, "role": "SALES_REP"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_customer(db, sales_rep_user):
    customer = Customer(
        name="Acme Corporation",
        email="contact@acme.com",
        phone="+1-555-0199",
        company="Acme Corp",
        industry="Technology",
        status="QUALIFIED",
        assigned_to=sales_rep_user.id,
        notes="High priority enterprise client"
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
