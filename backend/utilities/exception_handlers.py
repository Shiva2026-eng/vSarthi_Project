import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from jose import JWTError


# 1. Standard HTTP errors (400, 401, 403, 404, etc.)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# 2. Input/Body Validation errors (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# 3. Database unique constraint errors (e.g. duplicate email) (409 Conflict)
async def db_integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "A record with these details already exists."},
    )


# 4. General Database errors (DB down, connection lost, query fail) (500)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database connection error. Please try again later."},
    )


# 5. JWT / Token authentication errors (401)
async def jwt_exception_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid or expired authentication token."},
    )


# 6. External API errors (e.g. Microsoft Outlook or LLM network calls) (502)
async def external_api_exception_handler(request: Request, exc: httpx.HTTPError):
    return JSONResponse(
        status_code=502,
        content={"detail": "External service communication error. Please try again later."},
    )


# 7. File not found on disk errors (404)
async def file_not_found_exception_handler(request: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "Requested file not found on server."},
    )


# 8. File permission errors (500)
async def permission_exception_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=500,
        content={"detail": "File permission error on server."},
    )


# 9. Value/Format parsing errors (e.g. invalid UUID format) (400)
async def value_error_exception_handler(request: Request, exc: ValueError):
    error_message = str(exc) if str(exc) else "Invalid value provided."
    return JSONResponse(
        status_code=400,
        content={"detail": error_message},
    )


# 10. Catch-all for any other unexpected error (500)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# Function to register all handlers to the FastAPI app
def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, db_integrity_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(JWTError, jwt_exception_handler)
    app.add_exception_handler(httpx.HTTPError, external_api_exception_handler)
    app.add_exception_handler(FileNotFoundError, file_not_found_exception_handler)
    app.add_exception_handler(PermissionError, permission_exception_handler)
    app.add_exception_handler(ValueError, value_error_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
