import pytest
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose import JWTError
from utilities.exception_handlers import register_exception_handlers


@pytest.fixture
def exception_test_app():
    test_app = FastAPI()
    register_exception_handlers(test_app)

    class UserInput(BaseModel):
        name: str
        age: int

    @test_app.get("/test-http-error")
    def trigger_http_error():
        raise HTTPException(status_code=403, detail="Forbidden access")

    @test_app.post("/test-validation-error")
    def trigger_validation_error(data: UserInput):
        return {"name": data.name, "age": data.age}

    @test_app.get("/test-integrity-error")
    def trigger_integrity_error():
        raise IntegrityError("UNIQUE constraint failed: user.email", params={}, orig=Exception())

    @test_app.get("/test-db-error")
    def trigger_db_error():
        raise SQLAlchemyError("Database connection lost")

    @test_app.get("/test-jwt-error")
    def trigger_jwt_error():
        raise JWTError("Signature verification failed")

    @test_app.get("/test-external-api-error")
    def trigger_external_api_error():
        raise httpx.ConnectError("Could not connect to external API")

    @test_app.get("/test-file-not-found")
    def trigger_file_not_found():
        raise FileNotFoundError("uploads/doc_123.pdf")

    @test_app.get("/test-permission-error")
    def trigger_permission_error():
        raise PermissionError("Access denied to write file")

    @test_app.get("/test-value-error")
    def trigger_value_error():
        raise ValueError("Invalid UUID string format")

    @test_app.get("/test-unexpected-error")
    def trigger_unexpected_error():
        raise RuntimeError("Something unexpected broke")

    return test_app


@pytest.fixture
def exception_client(exception_test_app):
    return TestClient(exception_test_app, raise_server_exceptions=False)


def test_http_exception_handler(exception_client):
    response = exception_client.get("/test-http-error")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden access"}


def test_validation_exception_handler(exception_client):
    response = exception_client.post("/test-validation-error", json={"name": 123})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)


def test_integrity_error_handler(exception_client):
    response = exception_client.get("/test-integrity-error")
    assert response.status_code == 409
    assert response.json() == {"detail": "A record with these details already exists."}


def test_database_exception_handler(exception_client):
    response = exception_client.get("/test-db-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Database connection error. Please try again later."}


def test_jwt_exception_handler(exception_client):
    response = exception_client.get("/test-jwt-error")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired authentication token."}


def test_external_api_exception_handler(exception_client):
    response = exception_client.get("/test-external-api-error")
    assert response.status_code == 502
    assert response.json() == {"detail": "External service communication error. Please try again later."}


def test_file_not_found_exception_handler(exception_client):
    response = exception_client.get("/test-file-not-found")
    assert response.status_code == 404
    assert response.json() == {"detail": "Requested file not found on server."}


def test_permission_exception_handler(exception_client):
    response = exception_client.get("/test-permission-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "File permission error on server."}


def test_value_error_exception_handler(exception_client):
    response = exception_client.get("/test-value-error")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID string format"}


def test_generic_exception_handler(exception_client):
    response = exception_client.get("/test-unexpected-error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error. Please try again later."}
