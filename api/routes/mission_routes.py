from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from api.crud import create_mission_playing, get_mission

from api.open_api_responses import (open_api_response_login, open_api_response_not_found_character, open_api_response_error_server,
                                    open_api_response_already_exist_mission, open_api_response_not_found_mission)
from api.schemas import MissionPlayingCreate, MissionResponse, EnumRank
from api.dependencies import get_my_character_and_user, get_session, check_if_mission
from api.models import Mission, MissionPlaying, User, Character
from api.services import check_if_decision_finish, check_if_finish_time, check_if_mission_finish, get_end_time, get_random_mission, get_stat_character_from_srpg

tags_metadata = [
    {"name": "missions",  "description": "Operations with mission.", }]
router = APIRouter(tags={"Mission"}, prefix='/mission')


@router.post("/random",
             summary="Create a random mission for a character",
             status_code=status.HTTP_201_CREATED,
             response_model=MissionResponse,
             responses={
                 **open_api_response_login(),
                 **open_api_response_not_found_character(),
                 **open_api_response_error_server(),
                 **open_api_response_already_exist_mission()
             })
def create_mission(rank: EnumRank,
                   user_character: dict = Depends(get_my_character_and_user),
                   db: Session = Depends(get_session)):

    user: User = user_character['user']
    character: Character = user_character['character']

    if user.mission_playing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Mission Already Exist")

    try:
        mission_db: Mission = get_random_mission(db, rank, character.village)
        mission_playing: MissionPlaying = create_mission_playing(db, MissionPlayingCreate(
            mission_id=mission_db.id, character_id=character.id, begin_time=datetime.now(),
            percent_character=get_stat_character_from_srpg(character)[
                'detail'],
            step_id=mission_db.id, user_id=user.id))
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    end_time = get_end_time(mission_playing.begin_time,
                            rank, mission_playing.additionnal_time)
    return MissionResponse(**mission_db.dict(), begin_time=mission_playing.begin_time, end_time=end_time, character=mission_db.character)


@router.get('/in-progress',
            summary="Get mission in progress according to user connect",
            status_code=status.HTTP_200_OK,
            response_model=MissionResponse,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_mission_in_progress(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):

    try:
        mission_db: Mission = get_mission(db, user.mission_playing.mission_id)
        finish_choice: bool = check_if_decision_finish(
            db, user.mission_playing)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    end_time = get_end_time(user.mission_playing.begin_time,
                            mission_db.rank, user.mission_playing.additionnal_time)

    return MissionResponse(**mission_db.dict(),
                           finish_choice=finish_choice,
                           begin_time=user.mission_playing.begin_time,
                           end_time=end_time,
                           character=mission_db.character)

    # @router.put("/in-progress")
    # def update_mission(user: User = Depends(check_if_mission),
    #                 db: Session = Depends(get_session)):
    #     try:
    #         mission = get_mission_db(db, user=user)
    #         mission = update_mission_db(db, mission, )
    #     except:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Server")
