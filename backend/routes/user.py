from fastapi import APIRouter,Depends
from typing import Annotated
from utilities.current_user import get_current_user
from dependencies import db_dependency
router=APIRouter(
    prefix='/user',
    tags=['user']
)
user_dependency=Annotated[dict,Depends(get_current_user)]
@router.get("/my_profile")
def get_profile(user:user_dependency):
    return {
        "success":True,
        "details":user
    }