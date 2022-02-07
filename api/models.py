from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, BigInteger, Relationship
from sqlalchemy import Column

from api.schemas import CharacterCreate

# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.Link                             #
#               1.User                             #
#               2.Character                        #
#               3.Village                          #
#               3.Mission                          #
# -------------------------------------------------#


# -------------------------------------------------#
#                                                  #
#               0.Link                             #
#                                                  #
# -------------------------------------------------#

class UserCharacterLink(SQLModel, table=True):
    __tablename__ = "user_character_link"
    id_user: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True)
    id_character: Optional[int] = Field(
        default=None, foreign_key="character.id", primary_key=True)


class MissionPlaying(SQLModel, table=True):
    character_id: Optional[int] = Field(
        default=None, foreign_key="character.id", primary_key=True
    )
    mission_id: Optional[int] = Field(
        default=None, foreign_key="mission.id", primary_key=True
    )

    begin_time: datetime = Field(default=datetime.now())
    percent_character: int = Field()
    percent_choice: int = Field()
    additionnal_time: int = Field(default=0)
    step_id: Optional[int] = Field(default=None, foreign_key="step.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    step: 'Step' = Relationship(back_populates="mission_playing")
    user: 'User' = Relationship(back_populates="mission_playing")


class MissionVillage(SQLModel, table=True):
    village_id: Optional[int] = Field(
        default=None, foreign_key="village.id", primary_key=True
    )
    mission_id: Optional[int] = Field(
        default=None, foreign_key="mission.id", primary_key=True
    )

# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    discord_id: Optional[int] = Field(
        sa_column=Column(BigInteger), default=None, index=True)
    token_srpg: Optional[str] = Field(default=None, index=True)
    email: EmailStr = Field(index=True)
    password: str
    email_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    role: str = Field(default="member")

    characters: "Character" = Relationship(
        back_populates="users", link_model=UserCharacterLink)

    mission_playing: 'MissionPlaying' = Relationship(back_populates="user")

# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


class Character(CharacterCreate, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    users: List["User"] = Relationship(
        back_populates="characters", link_model=UserCharacterLink)

    mission: "Mission" = Relationship(
        back_populates="characters", link_model=MissionPlaying)


# -------------------------------------------------#
#                                                  #
#               3.Village                          #
#                                                  #
# -------------------------------------------------#

class Village(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field()
    missions: List["Mission"] = Relationship(
        back_populates="villages", link_model=MissionVillage)


# -------------------------------------------------#
#                                                  #
#               4.Mission                          #
#                                                  #
# -------------------------------------------------#


class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    rank: str = Field()
    title: str = Field()
    description: str = Field()
    cash: int = Field()
    percent_mission: int = Field()

    villages: List["Village"] = Relationship(
        back_populates="missions", link_model=MissionVillage)

    characters: List["Character"] = Relationship(
        back_populates="mission", link_model=MissionPlaying)


class Step(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    description: str = Field()
    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    mission_playing: 'MissionPlaying' = Relationship(back_populates="step")


class Choice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    sentence: str = Field()
    value: int = Field()

    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    step_to_id: Optional[int] = Field(default=None, foreign_key="step.id")
    step_from_id: Optional[int] = Field(default=None, foreign_key="step.id")

    step_to: 'Step' = Relationship(sa_relationship_kwargs={
                                   "foreign_keys": "Choice.step_to_id"})
    step_from: "Step" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Choice.step_from_id"})

    conditions: List["Condition"] = Relationship(back_populates="choice")


class Condition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    type: str = Field()
    value: int = Field()

    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    choice_id: Optional[int] = Field(default=None, foreign_key="choice.id")
    choice: "Choice" = Relationship(back_populates="conditions")