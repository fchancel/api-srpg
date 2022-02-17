from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List


from api.open_api_responses import (open_api_response_error_server, open_api_response_login,
                                    open_api_response_not_found_character)
from api.dependencies import get_session, get_current_user
from api.models import Character, User
from api.crud import get_character, get_characters_db
from api.schemas import CharacterBase
from api.services import (save_characters, delete_connexion_with_character, get_characters_from_srpg)

tags_metadata = [
    {"name": "characters", "description": "Operations with characters.", }]
router = APIRouter(tags={"Characters"}, prefix='/characters')


@router.patch('/',
              summary="Update characters of user from SRPG",
              status_code=status.HTTP_200_OK,
              response_model=List[CharacterBase],
              responses={
                  **open_api_response_login(),
                  **open_api_response_not_found_character(),
                  **open_api_response_error_server()
              })
def update_characters(db: Session = Depends(get_session),
                      user: User = Depends(get_current_user)):

    list_character_srpg = get_characters_from_srpg(user.token_srpg)

    if not list_character_srpg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    try:
        list_characters = save_characters(
            db, user, list_character_srpg, refresh=True)
        delete_connexion_with_character(
            db, user, list_character_srpg, list_characters)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return list_characters


@router.get("/mine",
            summary="Get all character of a user connected",
            status_code=status.HTTP_200_OK,
            response_model=List[CharacterBase],
            responses={
                **open_api_response_login(),
                **open_api_response_not_found_character(),
                **open_api_response_error_server()
            })
def get_characters(db: Session = Depends(get_session),
                   user: User = Depends(get_current_user)):
    try:
        characters_list = get_characters_db(db, user.id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not characters_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    return characters_list


@router.get("/{id}",
            summary="Get one character of mine by id",
            status_code=status.HTTP_200_OK,
            response_model=CharacterBase)
def get_one_character(id: int,
                      db: Session = Depends(get_session),
                      user: User = Depends(get_current_user)):
    try:
        character: Character = get_character(db, id=id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    for user_character in character.users:
        if user_character.id == user.id:
            return CharacterBase(**character.dict())

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Your not the owner")


@router.get("/{family_name}-{first_name}",
            summary="Get one character of mine by name",
            status_code=status.HTTP_200_OK,
            response_model=CharacterBase)
def get_one_character_by_name(family_name: str,
                              first_name: str,
                              db: Session = Depends(get_session),
                              user: User = Depends(get_current_user)):
    try:
        character: Character = get_character(db, name=f"{family_name} {first_name}")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    for user_character in character.users:
        if user_character.id == user.id:
            return CharacterBase(**character.dict())

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Your not the owner")
