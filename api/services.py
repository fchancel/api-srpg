
from datetime import timedelta, datetime
from math import floor
from random import randint, shuffle
from typing import List, Optional
import requests
import json

from sqlmodel import Session
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from jose import jwt

from config import get_settings, log

from api.schemas import ChoiceResponse, StepResponse, CharacterCreate
from api.models import Mission, MissionPlaying, Step, User, Character, Choice
from api.crud import create_rank_stat, get_finality_from_choice, get_missions, create_character, get_character, edit_character

# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.General                          #
#               1.User                             #
#               2.Character                        #
#               3.Mission                          #
#               4.Stats                            #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               0.General                          #
#                                                  #
# -------------------------------------------------#

MISSION_RANK = ["C", "B", "A", "S"]

MISSION_RANK_TIME = {
    "C": 3,
    "B": 6,
    "A": 8,
    "S": 10
}

MISSION_RANK_PERCENT = {
    "C": 70,
    "B": 50,
    "A": 35,
    "S": 20
}


def adding_data_in_db(db: Session, datas=[], refresh: bool = False) -> None:
    for data in datas:
        db.add(data)
    db.commit()
    if refresh:
        for data in datas:
            db.refresh(data)


def deleting_data_in_db(db: Session, datas=[]) -> None:
    for data in datas:
        db.delete(data)
    db.commit()


async def send_email(email_body: str, to_email: List[EmailStr], email_subject: str) -> None:
    if get_settings().is_dev():
        log.info(email_body)
    else:
        message = MessageSchema(
            subject=email_subject,
            recipients=to_email,
            body=email_body,
            subtype="html"
        )
        fm = FastMail(get_settings().mail_conf)
        await fm.send_message(message)


def make_422_response(loc=[], msg="", type_error=""):
    return {
        "loc": loc,
        "msg": msg,
        'type': type_error
    }


def make_url_endpoint(theme: str, id: int):
    return f"{get_settings().app_url}api/{theme}/{id}"

# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm_hash)
    return encoded_jwt


# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


def get_characters_from_srpg(token: str):
    url = requests.get(get_settings().SRPG_URL_CHARACTERS_TOKEN + token)
    datas = json.loads(url.text)
    if len(datas) == 0:
        return None
    else:
        for data in datas:
            data['avatar'] = get_settings().SRPG_URL_BASE + data['avatar']
    return datas


def get_stat_character_from_srpg(character):
    url = requests.get(
        f"{get_settings().SRPG_URL_MISSION_PERCENT}{character.id_srpg}")
    datas = json.loads(url.text)
    return datas


def save_characters(db: Session, user: User, list_character: list(), refresh: bool = False) -> List[Character]:
    character_db_list = []
    for character in list_character:
        character_in_db = get_character(db, id_srpg=character['id'])
        # If character doesn't exist in the database, add it
        if not character_in_db:
            rank_stat_lst = []
            for rank in MISSION_RANK:
                rank_stat_lst.append(create_rank_stat(db, rank))
            character_in_db = create_character(db,
                                               CharacterCreate(id_srpg=character['id'],
                                                               name=character['name'],
                                                               url_avatar=character['avatar'],
                                                               village=character['village']),
                                               user, rank_stat_lst)
            character_db_list.append(character_in_db)

        # If character already exist in database, update it and add user connexion
        else:
            if not refresh:
                character_db_list.append(edit_character(
                    db, character_in_db, village=character['village'], url_avatar=character['avatar'], user=user))
            else:
                village = None if character_in_db.village == character[
                    'village'] else character['village']
                url_avatar = None if character_in_db.url_avatar == character[
                    'avatar'] else character['avatar']
                if village or url_avatar:
                    character_db_list.append(edit_character(
                        db, character_in_db, village=village, url_avatar=url_avatar))
    return character_db_list


def delete_connexion_with_character(db: Session, user: User, list_character_srpg: list(), list_character_db: List[Character]):
    list_of_all_values = [value for elem in list_character_srpg
                          for value in elem.values()]
    for character in list_character_db:
        if not character.name in list_of_all_values:
            character.users.remove(user)
    db.commit()
    return


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#

def check_if_finish_time(begin_time, rank, additionnal_time) -> bool:
    if datetime.now() < (begin_time + timedelta(hours=MISSION_RANK_TIME[rank]) + timedelta(minutes=additionnal_time)):
        return False
    return True


def get_finish_time(begin_time, rank, additionnal_time) -> datetime:
    return begin_time + timedelta(hours=MISSION_RANK_TIME[rank]) + timedelta(minutes=additionnal_time)


def get_time_left(finish_time):
    if finish_time < datetime.now():
        return 0
    else:
        return finish_time - datetime.now()


def get_random_mission(db: Session, rank: str, village: str) -> Mission:
    if village == "Nukenin":
        village = "Errant"
    missions = get_missions(db, rank, village)
    size_max = len(missions)
    return missions[randint(0, size_max - 1)]


def get_percent_final(percent_mission, percent_character, percent_choice) -> int:
    percent_cumul = percent_character + percent_mission
    percent = floor((percent_cumul * abs(percent_choice)) // 100)
    if percent_choice < 0:
        stat_final = percent_cumul - percent
    else:
        stat_final = percent_cumul + percent
    if stat_final > 100:
        stat_final = 100
    elif stat_final < 0:
        stat_final = 0
    return floor(stat_final)


def win_or_loose(percent) -> str:
    total_choice = 100
    lst_result_win = ["win"] * percent
    lst_result__loose = ["fail"] * (total_choice - percent)
    result = lst_result_win + lst_result__loose
    shuffle(result)
    return result[randint(0, total_choice - 1)]


def get_result_step(db: Session, mission_playing: MissionPlaying, mission: Mission):
    percent_final = get_percent_final(
        mission.percent_mission, mission_playing.percent_character, mission_playing.percent_choice)
    result = win_or_loose(percent_final)
    return get_finality_from_choice(db, mission_playing.last_choice, result)


def make_response_step(db: Session, mission_playing: MissionPlaying, step: Step, choices: List[Choice]) -> StepResponse:
    choice_lst_responses = []
    if choices:
        for choice in choices:
            choice_lst_responses.append(ChoiceResponse(choice_id=choice.id,
                                                       sentence=choice.sentence))
    step_response = StepResponse(choices=choice_lst_responses,
                                 description=step.description,
                                 mission=make_url_endpoint(
                                     'games/missions', mission_playing.mission_id),
                                 character=make_url_endpoint(
                                     'characters', mission_playing.character_id)
                                 )
    return step_response


def get_choice_value(db: Session, choice: Choice, character: Character):
    character_stat = get_stat_character_from_srpg(character)
    condition_ok = True
    for condition in choice.conditions:
        if condition.type != "Time":
            value_character = character_stat['details'][condition.type]['niveau']
            if value_character < condition.value:
                condition_ok = False
    if not condition_ok:
        return choice.value * -1
    else:
        return choice.value


def get_additional_time(choice: Choice):
    for condition in choice.conditions:
        if condition.type == "Time":
            return condition.value
    return 0
