from typing import Optional
from fastapi import APIRouter, Body, status, Depends, HTTPException
from sqlmodel import Session

from api.open_api_responses import open_api_response_error_server, open_api_response_invalid_token
from api.schemas import UserBase, UserResponse
from api.dependencies import get_session, get_current_user
from api.services import (save_characters, get_characters_from_srpg)
from api.models import User
from api.crud import add_connexion_discord, create_user_db, get_user

tags_metadata = [
    {"name": "users", "description": "Operations with users. The **login** logic is also here.", }]
router = APIRouter(tags={"Users"}, prefix='/users')


# -------------------------------------------------#
#               1.User                             #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#

@router.post('', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user",
             responses={**open_api_response_invalid_token(),
                        **open_api_response_error_server()})
def create_user(token_srpg: str = Body(...), id_discord: Optional[int] = Body(None),
                db: Session = Depends(get_session)):
    token_srpg = token_srpg.strip()
    try:
        user = get_user(db, token_srpg=token_srpg)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="value is not unique")

    character_list = get_characters_from_srpg(token_srpg)
    if not character_list:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    try:
        user = create_user_db(db, token_srpg, id_discord)
        save_characters(db, user, character_list)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    return user


@router.get('', response_model=UserBase, status_code=status.HTTP_200_OK, summary="Get user by header")
def get_user_by_header(db: Session = Depends(get_session),
                       user: User = Depends(get_current_user)):
    return UserBase(**user.dict(), mission=True if user.mission_playing else False)
