from typing import List, TYPE_CHECKING, Optional
from datetime import timedelta
from jose import jwt
from fastapi import APIRouter, status, Depends, HTTPException, Request, BackgroundTasks, responses
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from config import get_settings
from api.open_api_responses import open_api_response_error_server, open_api_response_invalid_token, open_api_response_login, open_api_response_not_found_character
from api.schemas import UserResponse, Token, CharacterBase
from api.dependencies import GetCurrentUser, get_session
from api.services import (save_characters, authenticate_user,
                          create_access_token, check_autorization_authenticate_user, get_characters_from_srpg)
from api.crud import add_connexion_discord, create_user_db, get_user
from api.models import User

tags_metadata = [
    {"name": "users",  "description": "Operations with users. The **login** logic is also here.", }]
router = APIRouter(tags={"Users"}, prefix='/users')


# -------------------------------------------------#
#               1.User                             #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#

@ router.post('', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user", responses={
    **open_api_response_invalid_token(),
    **open_api_response_error_server()
})
def create_user(token_srpg: str,
                id_discord: Optional[int],
                db: Session = Depends(get_session)):
    try:
        if get_user(db, token_srpg=token_srpg):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="value is not unique")
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    character_list = get_characters_from_srpg(token_srpg)
    if not character_list:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
    try:
        user = create_user_db(db, token_srpg, id_discord)
        save_characters(db, user, character_list)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    return user


@ router.post("/token", response_model=Token, summary="Create a new authentification token", responses={
    **open_api_response_invalid_token()
})
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = get_user(db, token_srpg=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes_login)
    access_token = create_access_token(
        data={"srpg": user.token_srpg}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
