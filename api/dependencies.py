from typing import TYPE_CHECKING
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from jose import jwt

from config import get_settings
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
    with Session(engine) as session:
        try:
            yield session
        except:
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


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/users/token", auto_error=False)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class GetCurrentUser:

    def decode(self, token: str, db: Session):
        try:
            settings = get_settings()
            payload = jwt.decode(token, settings.secret_key,
                                 algorithms=[settings.algorithm_hash])
            if payload.get("bot"):
                data_connexion = payload.get("id")
            else:
                data_connexion = payload.get("srpg")
            if data_connexion is None:
                raise credentials_exception
        except jwt.JWTError as e:
            raise credentials_exception
        if payload.get('bot'):
            user = get_user(db, discord_id=data_connexion)
        else:
            user = get_user(db, token_srpg=data_connexion)
        if user is None:
            raise credentials_exception
        return user

    def __call__(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user: User = self.decode(token, db)
        return user


# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


def get_my_character_and_user(character_name: str, db: Session = Depends(get_session), user: User = Depends(GetCurrentUser())) -> Character:
    try:
        character: Character = get_character(db, name=character_name)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    if not character:
        raise HTTPException(
            tatus_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")
    elif not user in character.users:
        raise HTTPException(tatus_code=status.HTTP_403_FORBIDDEN,
                            detail="Character is not yours")
    return {
        'user': user,
        'character': character
    }


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#

def check_if_mission(user: User = Depends(GetCurrentUser())) -> User:
    if not user.mission_playing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mission Not Found")
    return user
