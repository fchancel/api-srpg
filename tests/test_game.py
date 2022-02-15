import json
import requests
import unittest
from config import get_settings
from tests.conftest import engine_test
from sqlmodel import SQLModel, Session
from api.models import *
from api.services import delete_connexion_with_character, save_characters
from api.crud import get_character, get_user, create_village
from create_mission import generate_mission_script


HOST = 'http://localhost:8000/'


class TestGame(unittest.TestCase):

    def setUp(self):
        SQLModel.metadata.create_all(engine_test)
        with Session(engine_test) as db:
            create_village(db, 'Konoha')
            create_village(db, 'Kumo')
            create_village(db, 'Errant')
        generate_mission_script(test=True, echo=False)
        self.token_srpg = "BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"
        self.url = HOST + 'api/games'
        self.header = {
            "Authorization": "Bearer BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"}
        requests.post(url=HOST+'api/users',
                      json={"token_srpg": self.token_srpg})

    # def test_create_game_bad_rank(self):
    #     data = {"rank":"P", "character_name":"Narrateur"}
    #     response = requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     self.assertEqual(response.status_code, 422, msg='excepted status code 422')

    # def test_create_game_success_and_create_game_already_exist(self):
    #     data = {"rank":"C", "character_name":"Narrateur"}
    #     response = requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     self.assertEqual(response.status_code, 201, msg="excepted status code 201")
    #     self.assertEqual(response.json()["mission"], f"{get_settings().app_url}api/games/missions/2", msg="excepted same url")
    #     response = requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     self.assertEqual(response.status_code, 409, msg="excepted status code 409 | Mission already exist")

    # def test_get_game_without_mission(self):
    #     response = requests.get(url=self.url+"/in-progress", headers=self.header)
    #     self.assertEqual(response.status_code, 404, msg='excpeted status code 404')

    # def test_get_game_success(self):
    #     data = {"rank":"C", "character_name":"Narrateur"}
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     response = requests.get(url=self.url+"/in-progress", headers=self.header)
    #     self.assertEqual(response.status_code, 200, msg='excepted status code 200')
    #     self.assertEqual(response.json()["mission"], f"{get_settings().app_url}api/games/missions/2", msg="excepted same url")

    # def test_get_game_time_left(self):
    #     data = {"rank":"C", "character_name":"Narrateur"}
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     response = requests.get(url=self.url+"/in-progress/time-left", headers=self.header)
    #     self.assertGreaterEqual(response.json()['time'], 10790, msg='expected time greather than 1790 seconds')
    #     self.assertLessEqual(response.json()['time'], 10810, msg='expected time less than 1790 seconds')

    # def test_get_game_time_left_after_adding_time(self):
    #     data = {"rank": "C", "character_name": "Narrateur"}
    #     id_choice = 1
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     requests.patch(url=self.url+"/in-progress/step?id_choice=" +
    #                    str(id_choice), headers=self.header)
    #     requests.get(
    #         url=self.url+"/step/in-progress", headers=self.header)
    #     response = requests.get(url=self.url+"/in-progress/time-left", headers=self.header)
    #     self.assertGreaterEqual(response.json()['time'], 14390, msg='expected time greather than 1790 seconds')
    #     self.assertLessEqual(response.json()['time'], 14410, msg='expected time less than 1790 seconds')


    # def test_get_first_step(self):
    #     data = {"rank":"C", "character_name":"Narrateur"}
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     response = requests.get(url=self.url+"/step/in-progress", headers=self.header)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['description'], "Test")
    #     self.assertEqual(response.json()["choices"][0]['choice_id'], 1)

    # def test_edit_position_succes(self):
    #     data = {"rank": "C", "character_name": "Narrateur"}
    #     id_choice = 2
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     requests.patch(url=self.url+"/in-progress/step?id_choice=" +
    #                    str(id_choice), headers=self.header)
    #     response = requests.get(
    #         url=self.url+"/step/in-progress", headers=self.header)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['description'], 'step 1')

    # def test_edit_position_end_of_way(self):
    #     data = {"rank": "C", "character_name": "Narrateur"}
    #     id_choice = 1
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     requests.patch(url=self.url+"/in-progress/step?id_choice="+str(id_choice), headers=self.header)
    #     response = requests.get(url=self.url+"/step/in-progress", headers=self.header)
    #     self.assertEqual(response.status_code, 204)
        
    # def test_get_game_result_not_take_all_choice(self):
    #     data = {"rank":"C", "character_name":"Narrateur"}
    #     requests.post(url=self.url+'/start', headers=self.header, json=data)
    #     response = requests.get(url=self.url+"/in-progress/result", headers=self.header)
    #     self.assertEqual(response.status_code, 403, msg="expected status code 403")



    def tearDown(self) -> None:
        SQLModel.metadata.drop_all(engine_test)

if __name__ == '__main__':
    unittest.main(failfast=True)
