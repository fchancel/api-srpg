
from datetime import timedelta, datetime
from http.client import HTTPException
from math import floor
from random import randint, shuffle
from typing import List, Optional
import requests
import json

from sqlmodel import Session
from fastapi import Request
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from passlib.context import CryptContext
from jose import jwt

from config import get_settings, log

from api.schemas import ChoiceResponse, StepResponse, UserCreate, EmailValidation, CharacterCreate
from api.models import Mission, MissionPlaying, User, Character, Choice, Step
from api.crud import create_user, get_choice_from_step, get_finality_from_choice, get_mission, get_missions, get_user, create_character, get_character, edit_character

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

# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_if_user_exist(db: Session, email: EmailStr):
    user = get_user(db, email=email)
    if user:
        return True
    return False


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def save_user(db: Session, user: UserCreate) -> User:
    user.password = get_password_hash(user.password)
    user = create_user(db, user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def check_autorization_authenticate_user(user: User) -> bool:
    if not user.is_active:
        return False
    elif not user.email_verified:
        return False
    return True


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


def send_validation_email(user: User, request: Request):
    settings = get_settings()
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes_mail)
    access_token = create_access_token(data={"id": user.id}, expires_delta=access_token_expires
                                       )
    link = request.url_for("verify_email", **{'token': str(access_token)})
    email_body = f"Salut, Utilise le lien ci-dessous pour valider ton adresse email\n{link}"
    email_subject = 'Valide ton email - SRPG Annexe'

    data = EmailValidation(email_body=email_body,
                           email_subject=email_subject,
                           to_email=[user.email])
    return data

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
        print(f"ID CHARACTER IS {character['id']}")
        if not character_in_db:
            character_db_list.append(create_character(db,
                                                      CharacterCreate(id_srpg=character['id'],
                                                                      name=character['name'],
                                                                      url_avatar=character['avatar'],
                                                                      village=character['village']),
                                                      user))
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
            print(f"remove {character.name}")
            character.users.remove(user)
    db.commit()
    return


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#
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


def check_if_finish_time(begin_time, rank, additionnal_time) -> bool:
    if datetime.now() < (begin_time + timedelta(hours=MISSION_RANK_TIME[rank] + timedelta(minutes=additionnal_time))):
        return False
    return True


def get_finish_time(begin_time, rank, additionnal_time)-> datetime:
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



def get_percent_final(percent_mission, percent_character, percent_choice)-> int:
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
    percent_final = get_percent_final(mission.percent_mission, mission_playing.percent_character, mission_playing.percent_choice)
    result = win_or_loose(percent_final)
    return get_finality_from_choice(db, mission_playing.last_choice, result)


def make_response_step(db: Session, mission_playing: MissionPlaying, choices: List[Choice]) -> StepResponse:
    choice_lst_responses = []
    for choice in choices:
        choice_lst_responses.append(ChoiceResponse(choice_id=choice.id,
                                                   sentence=choice.sentence))
    step_response = StepResponse(mission_id=mission_playing.mission_id,
                                 step_id=mission_playing.step_id,
                                 character=get_character(
                                     db, id=mission_playing.character_id),
                                 choices=choice_lst_responses)
    return step_response
