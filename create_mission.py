import os
import json
import traceback

from sqlalchemy.ext.serializer import loads, dumps
from sqlmodel import Session, SQLModel

from api.core.database import engine
from api.crud import (create_mission, delete_choices_from_mission, delete_conditions_from_mission, delete_mission, delete_steps_from_mission, get_village, edit_mission_village, create_choice, create_step, create_condition,
                      edit_choice, get_choice, get_step, get_condition)
from api.services import MISSION_RANK_PERCENT


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


if __name__ == "__main__":

    SQLModel.metadata.create_all(engine)
    file_name = "test.json"

    file = f"{os.getcwd()}/data/mission_json/{file_name}"

    with open(file) as json_data:
        data = json.load(json_data)

    steps = []
    choices = []
    conditions = []
    relations = []
    villages = []
    with Session(engine) as db:
        try:
            # CREATE MISSION
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
                    step_db = create_step(
                        db, node["properties"]["description"], mission.id)
                    steps.append(
                        {
                            "step_data": node,
                            "step_db": step_db.id
                        }
                    )

            # GET RELATION
            print("STEP 3: Get Relationship")
            for rel in data["relationships"]:
                relations.append(rel)

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

            print("STEP 5: Make relation between Choice and Condition")
            # MAKE RELATION BETWEEN CHOICE AND CONDITION
            for node in conditions:
                for rel in relations:
                    if node['condition_data']['id'] == rel["toId"]:
                        choice = find_choice(rel['fromId'], choices)
                        choice = edit_choice(db, get_choice(db, choice['choice_db']), conditions=[
                            get_condition(db, node['condition_db'])])
            print('Succès: Mission créé')
        except Exception as error:
            db.rollback()

    
            print("Erreur : Mission non créé")
            print(f"Mission ID in DB : {mission.id}")
            traceback.print_exc()

            print(f"Nettoyage des données en cours...")
            delete_conditions_from_mission(db, mission.id)
            delete_choices_from_mission(db, mission.id)
            delete_steps_from_mission(db, mission.id)
            delete_mission(db, mission.id)
            print(f"Nettoyage des données terminé...")
