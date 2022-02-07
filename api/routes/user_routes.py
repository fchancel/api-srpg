from typing import List, TYPE_CHECKING
from datetime import timedelta
from jose import jwt
from fastapi import APIRouter, status, Depends, HTTPException, Request, BackgroundTasks, responses
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from config import get_settings
from api.open_api_responses import open_api_response_error_server, open_api_response_login, open_api_response_not_found_character
from api.schemas import UserResponse, UserCreate, EmailValidation, Token, CharacterBase
from api.dependencies import GetCurrentUser, get_session
from api.services import (save_user, send_validation_email, send_email, adding_data_in_db, save_characters, authenticate_user,
                          create_access_token, check_autorization_authenticate_user, get_characters_from_srpg)
from api.crud import add_connexion_application
from api.crud import get_user
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

@ router.post('', response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_user(request: Request,
                bg_tasks: BackgroundTasks,
                user: UserCreate,
                db: Session = Depends(get_session)):
    try:
        if get_user(db, email=user.email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="value is not unique")
        db_user = save_user(db, user)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    data_email: EmailValidation = send_validation_email(db_user, request)

    bg_tasks.add_task(send_email,
                      data_email.email_body,
                      data_email.to_email,
                      data_email.email_subject)
    return db_user


@ router.get("/verify_email/{token}", summary="Verify user email with a token")
def verify_email(token: str, db: Session = Depends(get_session)):
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.secret_key,
            algorithms=[settings.algorithm_hash])
        try:
            user = get_user(db, id=payload.get('id'))
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
        if not user.email_verified:
            user.email_verified = True
            try:
                adding_data_in_db(db, [user])
            except:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
        return responses.JSONResponse({'detail': 'successfully activated'}, status_code=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return responses.JSONResponse({'detail': 'activation expired'}, status_code=status.HTTP_400_BAD_REQUEST)
    except jwt.JWTError:
        return responses.JSONResponse({'detail': 'invalid token'}, status_code=status.HTTP_400_BAD_REQUEST)


@ router.post("/token", response_model=Token, summary="Create a new authentification token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not check_autorization_authenticate_user(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes_login)
    access_token = create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@ router.post("/connect/srpg/",
              summary="Connect account with SRPG",
              response_model=List[CharacterBase],
              status_code=status.HTTP_201_CREATED,
              responses={
                  **open_api_response_login(),
                  **open_api_response_not_found_character(),
                  **open_api_response_error_server()
              })
def connect_srpg(token_srpg: str,
                 db: Session = Depends(get_session),
                 user: User = Depends(GetCurrentUser())):

    character_list = get_characters_from_srpg(token_srpg)

    if not character_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    try:
        user = add_connexion_application(db, user, token_srpg=token_srpg)
        lst_character = save_characters(db, user, character_list)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return lst_character
