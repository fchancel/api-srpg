from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlmodel import Session
from api.crud import create_mission_playing, get_character, get_choice_from_step, get_mission

from api.open_api_responses import (open_api_response_login, open_api_response_no_content, open_api_response_not_found_character, open_api_response_error_server,
                                    open_api_response_already_exist_mission, open_api_response_not_found_mission)
from api.schemas import FinalResult, MissionPlayingCreate, MissionResponse, EnumRank, StepResponse, TimeLeft
from api.dependencies import GetCurrentUser, get_my_character_and_user, get_session, check_if_mission
from api.models import Finality, Mission, MissionPlaying, User, Character
from api.services import check_if_finish_time, check_if_mission_finish, get_result_step, get_time_left, get_random_mission, get_stat_character_from_srpg, make_response_step
from testing import get_finish_time

tags_metadata = [
    {"name": "missions",  "description": "Operations with mission.", }]
router = APIRouter(tags={"Mission"}, prefix='/mission')


@router.post("/",
             summary="Create a random mission for a character according to the Rank and for the character Choice",
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

    end_time = get_time_left(mission_playing.begin_time,
                             rank, mission_playing.additionnal_time)
    return MissionResponse(**mission_db.dict(), begin_time=mission_playing.begin_time, end_time=end_time, character=character)


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
        finish_choice: bool = False
        if user.mission_playing.last_choice and user.mission_playing.last_choice.finalities:
            finish_choice: bool = True
        character: Character = get_character(
            db, id=user.mission_playing.character_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    end_time = get_time_left(user.mission_playing.begin_time,
                             mission_db.rank, user.mission_playing.additionnal_time)

    return MissionResponse(**mission_db.dict(),
                           finish_choice=finish_choice,
                           begin_time=user.mission_playing.begin_time,
                           end_time=end_time,
                           character=character)


@router.get('/in-progress/time-left',
            summary="Get time left in progress mission",
            status_code=status.HTTP_200_OK,
            response_model=TimeLeft,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_mission_time_left(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        mission: Mission = get_mission(db, user.mission_playing.mission_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return get_time_left(get_finish_time(user.mission_playing.begin_time, mission.rank, user.mission_playing.additionnal_time))


@router.get('/in-progress/result',
            summary="Get final result of mission",
            status_code=status.HTTP_200_OK,
            response_model=FinalResult,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_mission_result(user: User = Depends(check_if_mission),
                       db: Session = Depends(get_session)):
    if not user.mission_playing.last_choice or not user.mission_playing.last_choice.finalities:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need take all choice")
    try:
        mission: Mission = get_mission(db, user.mission_playing.mission_id)

        if not check_if_finish_time(user.mission_playing.begin_time, mission.rank, user.mission_playing.additionnal_time):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Time is not over")

        finality: Finality = get_result_step(db, user.mission_playing, mission)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    try:
        pass
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return FinalResult(**finality.dict())


@router.get('/step/in-progress',
            summary="Get the step in mission for an user connecting",
            status_code=status.HTTP_200_OK,
            response_model=StepResponse,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission(),
                **open_api_response_no_content()
            })
def get_step_in_progress(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        choices = get_choice_from_step(db, step_from=user.mission_playing.step)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if len(choices) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    step_response = make_response_step(db, user.mission_playing, choices)

    return step_response

    # @router.put("/in-progress")
    # def update_mission(user: User = Depends(check_if_mission),
    #                 db: Session = Depends(get_session)):
    #     try:
    #         mission = get_mission_db(db, user=user)
    #         mission = update_mission_db(db, mission, )
    #     except:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error Server")


# ASSIGNER UNE MISSION ALEATOIRE À UN PERSONNAGE ET JOUEUR

# RÉCUPÉRER LA MISSION EN COURS

# RÉCUPÉRER L'ÉTAPE ACTUEL DE MISSION

# PRENDRE DES DECISIONS

# TERMINER UNE MISSION

# RÉCUPÉRER LA LISTE DE MISSION ACTUELLEMENT JOUÉ EN CE MOMENT
