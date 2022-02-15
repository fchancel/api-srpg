from datetime import datetime
import traceback
from fastapi import APIRouter, Body, Depends, status, HTTPException, Response
from sqlmodel import Session
from api.crud import create_mission_playing, create_stat_admin_mission, delete_mission_playing_db, get_character, get_characters_db, get_choice, get_choice_from_step, get_first_step, get_mission, get_mission_playing, get_step, update_mission_playing, update_rank_stat

from api.open_api_responses import (open_api_response_login, open_api_response_not_found_character, open_api_response_error_server,
                                    open_api_response_already_exist_mission, open_api_response_not_found_choice, open_api_response_not_found_mission)
from api.schemas import CharacterBase, FinalResult, MissionPlayingCreate, MissionPlayingResponse, MissionResponse, EnumRank, StatAdminMissionBase, StepResponse, TimeLeft
from api.dependencies import get_my_character_and_user, get_session, check_if_mission
from api.models import Choice, Finality, Mission, MissionPlaying, Step, User, Character
from api.services import MISSION_RANK_PERCENT, get_finish_time, check_if_finish_time,  get_additional_time, get_choice_value, get_result_step, get_time_left, get_random_mission, get_stat_character_from_srpg, make_response_step, make_url_endpoint


tags_metadata = [
    {"name": "games",  "description": "Operations with gameplay.", }]
router = APIRouter(tags={"games"}, prefix='/games')


@router.post("/start",
             summary="Start game with a random mission for a character according to the Rank and for the character Choice",
             status_code=status.HTTP_201_CREATED,
             response_model=MissionPlayingResponse,
             responses={
                 **open_api_response_login(),
                 **open_api_response_not_found_character(),
                 **open_api_response_error_server(),
                 **open_api_response_already_exist_mission()
             })
def start_game(rank: EnumRank = Body(...),
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
                'total'],
            step_id=get_first_step(db).id, user_id=user.id))
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    end_time = get_finish_time(mission_playing.begin_time,
                               rank, mission_playing.additionnal_time)
    return MissionPlayingResponse(begin_time=mission_playing.begin_time,
                                  end_time=end_time,
                                  mission=make_url_endpoint(
                                      'games/missions', mission_playing.mission_id),
                                  character=make_url_endpoint('characters', mission_playing.character_id))


@router.get('/in-progress',
            summary="Get game in progress according to user connect",
            status_code=status.HTTP_200_OK,
            response_model=MissionPlayingResponse,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_game_in_progress(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):

    try:
        mission_playing = get_mission_playing(db, user=user)
        mission_db: Mission = get_mission(db, mission_playing.mission_id)
        finish_choice: bool = False
        if mission_playing.last_choice and mission_playing.last_choice.finalities:
            finish_choice: bool = True
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    end_time = get_finish_time(mission_playing.begin_time,
                               mission_db.rank, mission_playing.additionnal_time)

    return MissionPlayingResponse(finish_choice=finish_choice,
                                  begin_time=mission_playing.begin_time,
                                  end_time=end_time,
                                  mission=make_url_endpoint(
                                      'games/missions', mission_playing.mission_id),
                                  character=make_url_endpoint('characters', mission_playing.character_id))


@router.get('/in-progress/time-left',
            summary="Get time left in progress game",
            status_code=status.HTTP_200_OK,
            response_model=TimeLeft,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_game_time_left(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        mission_playing = get_mission_playing(db, user=user)
        mission: Mission = get_mission(db, mission_playing.mission_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return TimeLeft(time=get_time_left(get_finish_time(mission_playing.begin_time, mission.rank, mission_playing.additionnal_time)))


@router.get('/in-progress/result',
            summary="Get final result of game",
            status_code=status.HTTP_200_OK,
            response_model=FinalResult,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission()
            })
def get_game_result(user: User = Depends(check_if_mission),
                    db: Session = Depends(get_session)):
    try:
        mission_playing: MissionPlaying = get_mission_playing(db, user=user)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    if not mission_playing.last_choice or not mission_playing.last_choice.finalities:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need take all choice")
    try:
        mission: Mission = get_mission(db, mission_playing.mission_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not check_if_finish_time(mission_playing.begin_time, mission.rank, mission_playing.additionnal_time):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Time is not over")
    try:
        finality: Finality = get_result_step(db, mission_playing, mission)
        character: Character = get_character(
            db, id=mission_playing.character_id)
    except :
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    try:
        delete_mission_playing_db(db, mission_playing)
        if finality.value == 'win':
            update_rank_stat(db, character, mission.rank, win=1)
        else:
            update_rank_stat(db, character, mission.rank, fail=1)
        create_stat_admin_mission(db, StatAdminMissionBase(
                mission_name=mission.title,
                mission_rank=mission.rank,
                mission_village=character.village,
                character_name=character.name,
                percent_mission=MISSION_RANK_PERCENT[mission.rank],
                percent_character=mission_playing.percent_character,
                percent_choice=mission_playing.percent_choice,
                result=finality.value
            ))
        # AJOUT CASH
        finality: Finality = get_result_step(db, mission_playing, mission)
    except :
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return FinalResult(**finality.dict(),
                       mission=make_url_endpoint(
                           'games/missions', mission_playing.mission_id),
                       character=make_url_endpoint('characters', mission_playing.character_id))


@router.get('/step/in-progress',
            summary="Get the step in mission for an user connecting",
            status_code=status.HTTP_200_OK,
            response_model=StepResponse,
            responses={
                **open_api_response_login(),
                **open_api_response_error_server(),
                **open_api_response_not_found_mission(),
            })
def get_step_game_in_progress(user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        mission_playing: MissionPlaying = get_mission_playing(db, user=user)
        choices = get_choice_from_step(db, step_from=mission_playing.step)
        step = get_step(db, mission_playing.step_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if not choices:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    step_response = make_response_step(db, mission_playing, step, choices)

    return step_response


@router.patch('/in-progress/step',
              summary="Edit which step where are the player during a mission",
              status_code=status.HTTP_200_OK,
              responses={
                  **open_api_response_login(),
                  **open_api_response_error_server(),
                  **open_api_response_not_found_mission(),
                  **open_api_response_not_found_choice()
              })
def edit_position(id_choice: int, user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        mission_playing: MissionPlaying = get_mission_playing(db, user=user)
        choices = get_choice_from_step(db, step_from=mission_playing.step)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    list_id = [value.id for value in choices]

    if not id_choice in list_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="")
    try:
        character: Character = get_character(
            db, mission_playing.character_id)
        choice: Choice = get_choice(db, id_choice)
        next_step: Step = get_step(db, choice.step_to_id)
        mission_playing = update_mission_playing(db,
                                                 mission_playing,
                                                 percent_choice=mission_playing.percent_choice +
                                                 get_choice_value(
                                                     db, choice, character),
                                                 step=next_step,
                                                 additional_time=get_additional_time(
                                                     choice),
                                                 last_choice=choice)

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
    return


@router.get('/missions/{id}',
            summary="Get mission",
            status_code=status.HTTP_200_OK,
            response_model=MissionResponse)
def read_mission(id: int, user: User = Depends(check_if_mission), db: Session = Depends(get_session)):
    try:
        mission_playing: MissionPlaying = get_mission_playing(db, user=user)
        character = Character = get_character(db, id=mission_playing.character_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    if id != mission_playing.mission_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Mission not according to your character")
    try:
        mission = get_mission(db, id)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

    return MissionResponse(**mission.dict(),village=character.village )
