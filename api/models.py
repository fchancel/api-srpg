from typing import Optional, List
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, BigInteger, Relationship
from sqlalchemy import Column, table

from api.schemas import CharacterCreate, RankStatBase, StatAdminMission

# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.Link                             #
#               1.User                             #
#               2.Character                        #
#               3.Village                          #
#               4.Mission                          #
#               5.Stats                            #
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
    last_choice_id: Optional[int] = Field(
        default=None, foreign_key='choice.id')
    step_id: Optional[int] = Field(default=None, foreign_key="step.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    last_choice: 'Choice' = Relationship(back_populates="mission_playing")
    step: 'Step' = Relationship(back_populates="mission_playing")
    user: 'User' = Relationship(back_populates="mission_playing")


class MissionVillage(SQLModel, table=True):
    village_id: Optional[int] = Field(
        default=None, foreign_key="village.id", primary_key=True
    )
    mission_id: Optional[int] = Field(
        default=None, foreign_key="mission.id", primary_key=True
    )


class CharacterMissionStat(SQLModel, table=True):
    mission_rank_id: Optional[int] = Field(
        default=None, foreign_key="rank_stat.id", primary_key=True)

    character_id: Optional[int] = Field(
        default=None, foreign_key="character.id", primary_key=True)

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

    mission_rank: List["RankStat"] = Relationship(
        back_populates="character", link_model=CharacterMissionStat)


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
    first_step: bool = Field(default=False)
    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    mission_playing: 'MissionPlaying' = Relationship(back_populates="step")


class Choice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    sentence: str = Field()
    value: int = Field()

    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    step_to_id: Optional[int] = Field(default=None, foreign_key="step.id")
    step_from_id: Optional[int] = Field(default=None, foreign_key="step.id")

    mission_playing: 'MissionPlaying' = Relationship(
        back_populates="last_choice")
    step_to: 'Step' = Relationship(sa_relationship_kwargs={
                                   "foreign_keys": "Choice.step_to_id"})
    step_from: "Step" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Choice.step_from_id"})

    conditions: List["Condition"] = Relationship(back_populates="choice")

    finalities: Optional[List["Finality"]] = Relationship(
        back_populates="choice")


class Condition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    type: str = Field()
    value: int = Field()

    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    choice_id: Optional[int] = Field(default=None, foreign_key="choice.id")
    choice: "Choice" = Relationship(back_populates="conditions")


class Finality(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    mission_id: Optional[int] = Field(default=None, foreign_key="mission.id")

    description: str = Field()
    value: str = Field()  # win or fail
    cash: int = Field()

    choice_id: Optional[int] = Field(default=None, foreign_key="choice.id")
    choice: "Choice" = Relationship(back_populates="finalities")


# -------------------------------------------------#
#                                                  #
#               5.Stats                            #
#                                                  #
# -------------------------------------------------#


class RankStat(RankStatBase, table=True):
    __tablename__ = "rank_stat"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    character: "Character" = Relationship(
        back_populates="mission_rank", link_model=CharacterMissionStat)


class StatAdminMission(StatAdminMission):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)


class StatAdminMission(SQLModel):
    mission_name: str
    mission_rank: str
    mission_village: str

    character_name: str

    percent_mission: int
    percent_character: int
    percent_choice: int

    result: str
