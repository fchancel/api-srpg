from typing import List, Optional
from datetime import datetime
from enum import Enum
import re

from pydantic import BaseModel, EmailStr, validator
from sqlmodel import SQLModel, Field
# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.General                          #
#               1.Validator                        #
#               2.Token                            #
#               3.User                             #
#               4.Character                        #
#               5.Mission                          #
#               6.Stats                            #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               0.General                          #
#                                                  #
# -------------------------------------------------#


class EmailValidation(BaseModel):
    email_body: str
    to_email: List[EmailStr]
    email_subject: str


class Response204(BaseModel):
    detail: str


class Response400(BaseModel):
    detail: str


class Response401(BaseModel):
    detail: str


class Response403(BaseModel):
    detail: str


class Response404(BaseModel):
    detail: str


class Response409(BaseModel):
    detail: str


class Response500(BaseModel):
    detail: str


# -------------------------------------------------#
#                                                  #
#               1.Validator                        #
#                                                  #
# -------------------------------------------------#


def password_validator(password):
    # REGEX PASSWORD : minimum 8 characters, 1 lowercase, 1 uppercase,
    # 1 digits and can contain @$!%*?.&()[]{}
    regex_password = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$&+=-_!%*?.()\[\]{}]{8,}"
    pattern_password = re.compile(regex_password)

    if not pattern_password.match(password):
        raise ValueError(
            """value is not a valid password""")
    return password


def passwords_match(password2, values, **kwargs):
    if 'password' in values and password2 != values['password']:
        raise ValueError('passwords do not match')
    return password2


# -------------------------------------------------#
#                                                  #
#               2.Token                            #
#                                                  #
# -------------------------------------------------#


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None


# -------------------------------------------------#
#                                                  #
#               3.User                             #
#                                                  #
# -------------------------------------------------#


class UserCreate(SQLModel):
    email: EmailStr
    password: str
    password2: str

    # Validators
    _password_validator_password = validator(
        'password', allow_reuse=True)(password_validator)
    _password_validator_match_password = validator(
        'password', 'password2', allow_reuse=True)(passwords_match)


class UserResponse(SQLModel):
    id: Optional[int]
    discord_id: Optional[int]
    token_srpg: Optional[str]
    email: EmailStr


# -------------------------------------------------#
#                                                  #
#               4.Character                        #
#                                                  #
# -------------------------------------------------#


class CharacterBase(SQLModel):
    id_srpg: int
    name: str
    village: str
    level: int = Field(default=0)
    exp: int = Field(default=0)
    cash: int = Field(default=0)
    url_avatar: str


class CharacterCreate(CharacterBase):
    pass


# -------------------------------------------------#
#                                                  #
#               5.Mission                          #
#                                                  #
# -------------------------------------------------#


class EnumRank(str, Enum):
    C = 'C'
    B = 'B'
    A = 'A'
    S = 'S'


class MissionResponse(SQLModel):
    title: str
    rank: str
    village: str
    description: str
    finish_choice: bool = False
    begin_time: datetime
    end_time: datetime
    character: CharacterBase


class MissionPlayingCreate(SQLModel):
    mission_id: int
    character_id: int
    begin_time: datetime
    percent_character: int
    percent_choice: int = 0
    additionnal_time: int = 0
    step_id: int
    user_id: int


class ChoiceResponse(SQLModel):
    choice_id: int
    sentence: str


class StepResponse(SQLModel):
    mission_id: int
    step_id: int
    description: str
    character: CharacterBase
    choices: List[ChoiceResponse]


class FinalResult(SQLModel):
    mission_id: int
    description: str
    value: str


class TimeLeft(SQLModel):
    time: datetime


# -------------------------------------------------#
#                                                  #
#               6.Stats                            #
#                                                  #
# -------------------------------------------------#

class RankStatBase(SQLModel):
    rank: str
    win: int = Field(default=0)
    fail: int = Field(default=0)
