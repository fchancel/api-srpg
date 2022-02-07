from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List


from api.open_api_responses import open_api_response_error_server, open_api_response_login, open_api_response_not_found_character
from api.dependencies import get_session, GetCurrentUser
from api.models import User
from api.crud import get_characters_db
from api.schemas import CharacterBase
from api.services import delete_connexion_with_character, save_characters, delete_connexion_with_character, get_characters_from_srpg

tags_metadata = [
    {"name": "characters",  "description": "Operations with characters.", }]
router = APIRouter(tags={"Characters"}, prefix='/characters')


@router.put('/{token_srpg}',
            summary="Update characters of user from SRPG",
            status_code=status.HTTP_200_OK,
            response_model=List[CharacterBase],
            responses={
                **open_api_response_login(),
                **open_api_response_not_found_character(),
                **open_api_response_error_server()
            })
def update_characters(token_srpg: str,
                      db: Session = Depends(get_session),
                      user: User = Depends(GetCurrentUser())):

    list_character_srpg = get_characters_from_srpg(token_srpg)

    if not list_character_srpg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    try:
        list_characters = save_characters(db, user, list_character_srpg, refresh=True)
        delete_connexion_with_character(db, user, list_character_srpg, list_characters)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
        
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
                   user: User = Depends(GetCurrentUser())):
    try:
        characters_list = get_characters_db(db, user.id)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not characters_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character Not Found")

    return characters_list

