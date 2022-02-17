import requests
import unittest
from config import get_settings
from tests.conftest import engine_test
from sqlmodel import SQLModel, Session
from api.services import delete_connexion_with_character, save_characters
from api.crud import get_character, get_user


HOST = 'http://localhost:8000/'


class TestCharacter(unittest.TestCase):

    def setUp(self):
        SQLModel.metadata.create_all(engine_test)
        self.token_srpg = "BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"
        self.url = HOST + 'api/characters'
        self.header = {"Authorization": "Bearer BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"}
        requests.post(url=HOST + 'api/users', json={"token_srpg": self.token_srpg})

    def test_get_characters_success(self):
        with Session(engine_test) as db:
            data_character = get_character(db, name="Narrateur")
        data_correct = {
            "id_srpg": data_character.id_srpg,
            "name": data_character.name,
            "village": data_character.village,
            "level": data_character.level,
            "exp": data_character.exp,
            "cash": data_character.cash,
            "url_avatar": data_character.url_avatar,
        }
        response = requests.get(url=self.url + '/mine', headers=self.header)
        self.assertEqual(response.json()[0], data_correct, msg="expected two dict as equal")

    def test_update_character_success(self):
        with Session(engine_test) as db:
            data_test = {
                "id": 2,
                "name": "Narrateur",
                "village": "Kumo",
                "avatar": "test"
            }
            response = save_characters(db, None, [data_test], True)
        self.assertEqual(response[0].village, "Kumo", msg="excepted village value is Kumo")
        self.assertEqual(response[0].url_avatar, "test", msg="excepted url_village value is test")

    def test_delete_connexion_with_character(self):
        with Session(engine_test) as db:
            data_test = {
                "id": 2,
                "name": "Narrateur",
                "village": "Kumo",
                "avatar": "test"
            }
            user = get_user(db, token_srpg=self.token_srpg)
            delete_connexion_with_character(db, user, [], user.characters)
        response = requests.get(url=self.url + '/mine', headers=self.header)
        self.assertEqual(response.status_code, 404, msg="excepted status code 404")

    def test_update_character_without_change(self):
        response = requests.patch(url=self.url, headers=self.header)
        self.assertEqual(response.status_code, 200, msg="excepted status code 200")

    def test_get_one_character_success(self):
        id_character = 1
        response = requests.get(url=f"{self.url}/{id_character}", headers=self.header)
        self.assertEqual(response.status_code, 200)

    def test_get_one_character_not_exist(self):
        id_character = 2
        response = requests.get(url=f"{self.url}/{id_character}", headers=self.header)
        self.assertEqual(response.json()['detail'], "Character Not Found")

    def tearDown(self) -> None:
        SQLModel.metadata.drop_all(engine_test)


if __name__ == '__main__':
    unittest.main(failfast=True)
