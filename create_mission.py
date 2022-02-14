import os
import json
import traceback

from sqlalchemy.ext.serializer import loads, dumps
from sqlmodel import Session, SQLModel

from api.core.database import engine
from api.crud import (create_finality, create_mission, delete_choices_from_mission, delete_conditions_from_mission, delete_finality_from_mission, delete_mission, delete_steps_from_mission, get_finality, get_village, edit_mission_village, create_choice, create_step, create_condition,
                      edit_choice, get_choice, get_step, get_condition)
from api.services import MISSION_RANK_PERCENT
from tests.conftest import engine_test


def find_choice(id: str, choice: list):
    for node in choice:
        if node['choice_data']['id'] == id:
            return node


def find_step(id: str, step: list):
    for node in step:
        if node['step_data']['id'] == id:
            return node


def find_condition(id: str, condition: list):
    for node in condition:
        if node['condition_data']['id'] == id:
            return node


def generate_mission_script(test: bool = False, recursive=True, echo=True):
    if test:
        #! NOT CHANGE HERE
        if recursive:
            generate_mission_script(True, False, echo)
            file_name = "test_konoha.json"
            file = f"{os.getcwd()}/data/mission_json/{file_name}"
            engine = engine_test
        else:
            file_name = "test_kumo.json"
            file = f"{os.getcwd()}/data/mission_json/{file_name}"
            engine = engine_test
        #! NOT CHANGE HERE
    else:
        # EDIT HERE FOR CHANGE MISSION IN SCRIPT
        file_name = "test.json"
        file = f"{os.getcwd()}/data/mission_json/{file_name}"

    with open(file) as json_data:
        data = json.load(json_data)

    steps = []
    choices = []
    conditions = []
    relations = []
    finality = []
    villages = []
    with Session(engine) as db:
        try:
            # CREATE MISSION
            if echo:
                print("STEP 1: Create Mission")
            for node in data['nodes']:
                if "Mission" in node['labels']:
                    mission = create_mission(db, node["properties"]["rank"].upper(),
                                             node["properties"]["title"],
                                             node["properties"]["description"],
                                             node["properties"]["cash"],
                                             MISSION_RANK_PERCENT[node["properties"]["rank"].upper()])
                for property in node["labels"]:
                    if property != "Mission":
                        villages.append(get_village(db, property.capitalize()))
                if len(villages) == 0:
                    raise
                mission = edit_mission_village(db, mission, villages)

            # CREATE CHOICE, STEP AND CONDITION
            if echo:
                print("STEP 2: Create Choice, Step and Condition")
            for node in data['nodes']:
                if node['caption'] == "Choice":
                    choice_db = create_choice(
                        db, node["properties"]["sentence"], node["properties"]["value"], mission.id)
                    choices.append(
                        {
                            "choice_data": node,
                            "choice_db": choice_db.id
                        }
                    )
                elif node["caption"] == "Condition":
                    condition_db = create_condition(
                        db, node["properties"]["type"].capitalize(), node["properties"]["value"], mission.id)
                    conditions.append(
                        {
                            "condition_data": node,
                            "condition_db": condition_db.id
                        }
                    )
                elif node['caption'] == "Step":
                    if "Mission" in node['labels']:
                        first_step = True
                    else:
                        first_step = False
                    step_db = create_step(
                        db, node["properties"]["description"], mission.id, first_step)
                    steps.append(
                        {
                            "step_data": node,
                            "step_db": step_db.id
                        }
                    )
                elif node['caption'] == "Finality":
                    if 'cash' in node['properties']:
                        cash = node['properties']['cash']
                    else:
                        cash = 0
                    finality_db = create_finality(
                        db, node["properties"]["description"], mission.id, node["properties"]["value"], cash)
                    finality.append(
                        {
                            "finality_data": node,
                            "finality_db": finality_db.id
                        }
                    )

            # GET RELATION
            if echo:
                print("STEP 3: Get Relationship")
            for rel in data["relationships"]:
                relations.append(rel)

            if echo:
                print("STEP 4: Make relation between Choice and Step")
            # MAKE RELATION BETWEEN CHOICE AND STEP
            for node in steps:
                for rel in relations:
                    if node['step_data']['id'] == rel["fromId"]:
                        choice = find_choice(rel['toId'], choices)
                        choice = edit_choice(db,
                                             get_choice(
                                                 db, choice['choice_db']),
                                             step_from=get_step(db, node['step_db']))
                    if node['step_data']['id'] == rel["toId"]:
                        choice = find_choice(rel['fromId'], choices)
                        choice = edit_choice(db,
                                             get_choice(
                                                 db, choice['choice_db']),
                                             step_to=get_step(db, node['step_db']))
            if echo:
                print("STEP 5: Make relation between Choice and Condition")
            # MAKE RELATION BETWEEN CHOICE AND CONDITION
            for node in conditions:
                for rel in relations:
                    if node['condition_data']['id'] == rel["toId"]:
                        choice = find_choice(rel['fromId'], choices)
                        choice = edit_choice(db, get_choice(db, choice['choice_db']), conditions=[
                            get_condition(db, node['condition_db'])])
            if echo:
                print("STEP 6: Make relation between Choice and Finality")
            # MAKE RELATION BETWEEN CHOICE AND FINALITY
            for node in finality:
                for rel in relations:
                    if node['finality_data']['id'] == rel["toId"]:
                        choice = find_choice(rel['fromId'], choices)
                        choice = edit_choice(db, get_choice(db, choice['choice_db']), finalities=[
                            get_finality(db, node['finality_db'])])
            if echo:
                print('Succès: Mission créé')
        except Exception as error:
            db.rollback()

            print("Erreur : Mission non créé")
            print(f"Mission ID in DB : {mission.id}")
            traceback.print_exc()

            print(f"Nettoyage des données en cours...")
            delete_conditions_from_mission(db, mission.id)
            delete_finality_from_mission(db, mission.id)
            delete_choices_from_mission(db, mission.id)
            delete_steps_from_mission(db, mission.id)
            delete_mission(db, mission.id)
            print(f"Nettoyage des données terminé...")


if __name__ == "__main__":

    generate_mission_script()
