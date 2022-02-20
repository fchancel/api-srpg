from typing import Optional, List
from pydantic import EmailStr

from sqlmodel import Session, select, BigInteger, text

from api.models import (Finality, MissionPlaying, MissionVillage, RankStat, Village, User, Character, Mission, Step,
                        Choice, Condition, UserCharacterLink, StatAdminMission)
from api.schemas import StatAdminMissionBase, CharacterCreate, EnumRank, MissionPlayingCreate

# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.Village                          #
#               1.User                             #
#               2.Character                        #
#               3.Mission                          #
#                   3.1.Mission                    #
#                   3.2.Step                       #
#                   3.3.Choice                     #
#                   3.4.Condition                  #
#                   3.5.Finality                   #
#                   3.6.Mission Playing            #
#               4.Stats                            #
#                   4.1.Rank Stats                 #
#                   4.2.Mission Admin Stats        #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               0.Village                          #
#                                                  #
# -------------------------------------------------#


def create_village(db: Session, name: str):
    village = Village(name=name)
    db.add(village)
    db.commit()
    db.refresh(village)
    return village


def get_village(db: Session, name: str):
    return db.exec(select(Village).where(Village.name == name)).first()


# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


def create_user_db(db: Session, token_srpg: str, discord_id: Optional[int]):
    db_user = User(token_srpg=token_srpg)
    if discord_id:
        db_user.discord_id = discord_id
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(
        db: Session, id: Optional[int] = None, discord_id: Optional[BigInteger] = None,
        token_srpg: Optional[str] = None,
        email: Optional[EmailStr] = None) -> Optional[User]:
    user = None
    if id:
        user = db.exec(select(User).where(User.id == id)).first()
    elif discord_id:
        user = db.exec(select(User).where(
            User.discord_id == discord_id)).first()
    elif token_srpg:
        user = db.exec(select(User).where(
            User.token_srpg == token_srpg)).first()
    elif email:
        user = db.exec(select(User).where(User.email == email)).first()
    return user


def add_connexion_discord(
        db: Session, user: User, token_srpg: Optional[str] = None, discord_id: Optional[int] = None) -> User:
    if discord_id:
        discord_id = discord_id
    db.commit()
    db.refresh()
    return user


# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


def create_character(
        db: Session, character: CharacterCreate, user: Optional['User'],
        rank_stat: Optional[List['RankStat']]):
    db_character: Character = Character.parse_obj(character)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    if user:
        db_character.users.append(user)
    if rank_stat:
        for rank in rank_stat:
            db_character.mission_rank.append(rank)
    db.commit()
    return character


def edit_character(
        db: Session, character: Character, village: Optional[str] = None, url_avatar: Optional[str] = None,
        user: Optional['User'] = None, cash: Optional[int] = None):
    if village:
        character.village = village
    if url_avatar:
        character.url_avatar = url_avatar
    if user:
        character.users.append(user)
    if cash is not None:
        character.cash = cash
    db.commit()
    db.refresh(character)
    return character


def get_character(db: Session, id: Optional[int] = None, id_srpg: Optional[int] = None, name: Optional[str] = None):
    if id:
        character = db.exec(select(Character).where(
            Character.id == id)).first()
    elif id_srpg:
        character = db.exec(select(Character).where(
            Character.id_srpg == id_srpg)).first()
    elif name:
        character = db.exec(select(Character).where(
            Character.name == name)).first()
    return character


def get_characters_db(db: Session, id_user: int):
    characters = db.exec(select(Character).join(UserCharacterLink).where(
        UserCharacterLink.id_user == id_user)).all()
    return characters


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#


# -------------------------------------------------#
#               3.1.Mission                        #
# -------------------------------------------------#


def create_mission(db: Session, rank: EnumRank, title: str, description: str, cash: int, percent_mission: int):
    mission = Mission(rank=rank, title=title, description=description,
                      cash=cash, percent_mission=percent_mission)
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


def edit_mission_village(db: Session, mission: Mission, villages: List['Village']):
    for village in villages:
        mission.villages.append(village)
    db.commit()
    db.refresh(mission)
    return mission


def get_mission(db: Session, id: int):
    return db.get(Mission, id)


def get_missions(db: Session, rank: Optional[str] = None, village: Optional[str] = None):
    if rank and village:
        missions = db.exec(select(Mission).where(Mission.rank == rank).join(MissionVillage).join(
            Village).where(Village.name == village)).all()

    elif rank:
        missions = db.exec(select(Mission).where(Mission.rank == rank)).all()
    elif village:
        missions = db.exec(select(Mission).join(MissionVillage).join(
            Village).where(Village.name == village)).all()
    return missions


def delete_mission(db: Session, id: int):
    mission = get_mission(db, id)
    db.delete(mission)
    db.commit()
    return

# -------------------------------------------------#
#               3.2.Step                           #
# -------------------------------------------------#


def create_step(db: Session, description: str, mission_id: int, first_step: bool):
    step = Step(description=description,
                mission_id=mission_id, first_step=first_step)
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def get_step(db: Session, id: int):
    return db.get(Step, id)


def get_first_step(db: Session):
    return db.exec(select(Step).where(Step.first_step == True)).first()


def get_steps_from_mission(db: Session, mission_id: int):
    return db.exec(select(Step).where(Step.mission_id == mission_id)).all()


def delete_steps_from_mission(db: Session, mission_id: int):
    steps = get_steps_from_mission(db, mission_id)
    for step in steps:
        db.delete(step)
    db.commit()
    return

    # -------------------------------------------------#
    #               3.3.Choice                         #
    # -------------------------------------------------#


def create_choice(db: Session, sentence: str, value: int, mission_id: int):
    choice = Choice(sentence=sentence, value=value, mission_id=mission_id)
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice


def get_choice(db: Session, id: int):
    return db.get(Choice, id)


def get_choice_from_step(db: Session, step_from: Optional[Step] = None, step_to: Optional[Step] = None):
    choices = []
    if step_from and step_to:
        choices: Choice = db.exec(select(Choice).where(
            Choice.step_to_id == step_to.id, Choice.step_from_id == step_from.id)).all()
    elif step_from:
        choices: Choice = db.exec(select(Choice).where(
            Choice.step_from_id == step_from.id)).all()
    elif step_to:
        choices: Choice = db.exec(select(Choice).where(
            Choice.step_to_id == step_to.id)).all()
    if len(choices) == 0:
        return None
    return choices


def edit_choice(
        db: Session, choice: Choice, step_from: Optional[Step] = None, step_to: Optional[Step] = None,
        conditions: Optional[list] = None, finalities: Optional[list] = None):
    if step_from:
        choice.step_from_id = step_from.id
    if step_to:
        choice.step_to_id = step_to.id
    if conditions:
        for condition in conditions:
            choice.conditions.append(condition)
    if finalities:
        for finality in finalities:
            choice.finalities.append(finality)
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice


def get_choices_from_mission(db: Session, mission_id: int):
    return db.exec(select(Choice).where(Choice.mission_id == mission_id)).all()


def delete_choices_from_mission(db: Session, mission_id: int):
    choices = get_choices_from_mission(db, mission_id)
    for choice in choices:
        db.delete(choice)
    db.commit()
    return

# -------------------------------------------------#
#               3.4.Condition                      #
# -------------------------------------------------#


def create_condition(db: Session, type: str, value: int, mission_id: int):
    condition = Condition(type=type, value=value, mission_id=mission_id)
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition


def get_condition(db: Session, id: int):
    return db.get(Condition, id)


def get_conditions_from_mission(db: Session, mission_id: int):
    return db.exec(select(Condition).where(Condition.mission_id == mission_id)).all()


def delete_conditions_from_mission(db: Session, mission_id: int):
    conditions = get_conditions_from_mission(db, mission_id)
    for condition in conditions:
        db.delete(condition)
    db.commit()
    return

# -------------------------------------------------#
#               3.5.Finality                       #
# -------------------------------------------------#


def create_finality(db: Session, description: str, mission_id: int, value: str, cash: int):
    finality = Finality(description=description,
                        mission_id=mission_id,
                        value=value,
                        cash=cash)
    db.add(finality)
    db.commit()
    db.refresh(finality)
    return finality


def get_finality(db: Session, id: int):
    return db.get(Finality, id)


def get_finality_from_choice(db: Session, choice: Choice, value: str):
    return db.exec(select(Finality).where(Finality.choice_id == choice.id, Finality.value == value)).first()


def get_finality_from_mission(db: Session, mission_id: int):
    return db.exec(select(Finality).where(Finality.mission_id == mission_id)).all()


def delete_finality_from_mission(db: Session, mission_id: int):
    finalities = get_finality_from_mission(db, mission_id)
    for finality in finalities:
        db.delete(finality)
    db.commit()
    return


# -------------------------------------------------#
#               3.6.Mission Playing                #
# -------------------------------------------------#


def create_mission_playing(db: Session, mission_data: MissionPlayingCreate):
    mission = MissionPlaying.parse_obj(mission_data)
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


def get_mission_playing(db: Session, user: Optional[User] = None, character: Optional['Character'] = None) -> Mission:
    if user:
        mission = db.exec(select(MissionPlaying).where(
            MissionPlaying.user == user)).first()
    elif character:
        mission = db.exec(select(MissionPlaying).where(
            Mission.character == character)).first()
    return mission


def update_mission_playing(
        db: Session, mission_playing: MissionPlaying, percent_choice: Optional[int] = None,
        step: Optional['Step'] = None,
        additional_time: Optional[int] = None, last_choice: Optional['Choice'] = None) -> Mission:
    mission_playing.step = step
    if percent_choice:
        mission_playing.percent_choice = percent_choice
    if additional_time:
        mission_playing.additionnal_time += additional_time
    if last_choice:
        mission_playing.last_choice_id = last_choice.id
    db.commit()
    db.refresh(mission_playing)
    return mission_playing


def delete_mission_playing_db(db: Session, mission_playing: MissionPlaying) -> None:
    db.delete(mission_playing)
    db.commit()
    return


# def get_missions(db: Session, offset: int, limit: int, desc: bool, user: Optional[User] = None):
#     if user:
#         missions = db.exec(select(Mission).where(Mission.user == user).order_by(
#             text(f"begin_time {desc}")).offset(offset).limit(limit)).all()
#         # missions = db.exec(select(Mission).where(Mission.user == user).order_by(Mission.begin_time.desc()).offset(offset).limit(limit)).all()
#     else:
#         missions = db.exec(select(Mission).order_by(
#             text(f"begin_time {desc}")).offset(offset).limit(limit)).all()
#         # missions = db.exec(select(Mission).order_by(Mission.begin_time.desc()).offset(offset).limit(limit)).all()
#     return missions


# -------------------------------------------------#
#                                                  #
#               4.Stats                            #
#                                                  #
# -------------------------------------------------#

# -------------------------------------------------#
#               4.1.Rank Stats                     #
# -------------------------------------------------#

def create_rank_stat(db: Session, rank: str) -> RankStat:
    rank_stat: RankStat = RankStat(rank=rank, win=0, fail=0)
    db.add(rank_stat)
    db.commit()
    db.refresh(rank_stat)
    return rank_stat


def get_rank_stat(db: Session, character: Character, rank: str):
    return db.exec(select(RankStat).where(Character.id == character.id, RankStat.rank == rank)).first()


def update_rank_stat(
        db: Session, character: Character, rank: str, win: Optional[int] = None, fail: Optional[int] = None):
    rank_db = get_rank_stat(db, character, rank)
    if win is not None:
        rank_db.win += 1
    if fail is not None:
        rank_db.fail += 1
    db.commit()
    db.refresh(rank_db)
    return rank_db


# -------------------------------------------------#
#               4.2.Mission Admin Stats            #
# -------------------------------------------------#

def create_stat_admin_mission(db: Session, data: StatAdminMissionBase):
    stat = StatAdminMission.parse_obj(data)
    db.add(stat)
    db.commit()
    return stat
