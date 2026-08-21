from schemas.user_request import UserRequestModel
from schemas.token_response import TokenResponse
from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from dependencies import db_dependency
from services.auth_service import create_user, login

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserRequestModel, db: db_dependency):
    return create_user(user, db)

@router.post("/login", response_model=TokenResponse)
def login_route(
    form_user: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
    response: Response,
):
    result = login(form_user.username, form_user.password, db)
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        max_age=1200,
        expires=1200,
        samesite="lax",
        secure=False,
        path="/",
    )
    return result

@router.post("/logout")
def logout_route(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"success": True, "message": "Successfully logged out"}