from fastapi import Body, HTTPException, Header, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from jose import jwt

from config import get_settings, Settings
from tests.conftest import engine_test
from api.core.database import engine

from api.crud import get_user, get_character
from api.models import User, Character


# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.General                          #
#               1.User                             #
#               2.Character                        #
#               3.Mission                          #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               0.General                          #
#                                                  #
# -------------------------------------------------#


def get_session():
    settings: Settings = get_settings()
    if settings.is_test():
        with Session(engine_test) as session:
            try:
                yield session
            except Exception:
                session.rollback()
                raise
    else:
        with Session(engine) as session:
            try:
                yield session
            except Exception:
                session.rollback()
                raise


async def pagination_parameters(desc: bool = False, skip: int = 0, limit: int = 10):
    if desc:
        desc = "DESC"
    else:
        desc = ""
    if skip < 0:
        skip = 0
    if limit <= 0:
        limit = 10
    if skip >= limit:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
            {
                "loc": [
                    "body",
                    "pagination_dependencies",
                    "skip / limit"
                ],
                "msg": "value is not a valid sort",
                "type": "value_error"
            }
        ])
    return {"skip": skip, "limit": limit, "desc": desc}


# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"srpg-token": "Bearer"},
)

oauth_schema = HTTPBearer()


def get_current_user(
        token: HTTPAuthorizationCredentials = Security(oauth_schema),
        front: str = Header("website"),
        db: Session = Depends(get_session)):
    token = token.credentials
    if front == 'bot':
        try:
            settings = get_settings()
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm_hash])
            discord_id = payload.get("discord_id")
            if discord_id is None:
                raise credentials_exception
        except jwt.JWTError:
            raise credentials_exception

        user = get_user(db, discord_id=discord_id)

    else:
        user = get_user(db, token_srpg=token)
    if user is None:
        raise credentials_exception
    return user


# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


def get_my_character_and_user(
        character_name: str = Body(...),
        db: Session = Depends(get_session),
        user: User = Depends(get_current_user)) -> Character:
    try:
        character: Character = get_character(db, name=character_name)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")
    elif user not in character.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character is not yours")
    return {
        'user': user,
        'character': character
    }


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#

def check_if_mission(user: User = Depends(get_current_user)) -> User:
    if not user.mission_playing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission Not Found")
    return user
