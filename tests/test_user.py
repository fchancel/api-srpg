import requests
import unittest
from tests.conftest import engine_test
from sqlmodel import SQLModel


HOST = 'http://localhost:8000/'


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        SQLModel.metadata.create_all(engine_test)

    def setUp(self):
        self.url = HOST + 'api/users'

    def test_create_user_with_invalid_token(self):
        data = {"token_srpg": "Invalid Token"}
        response = requests.post(url=self.url, json=data)
        self.assertEqual(response.json()['detail'], 'Invalid Token', msg="expected status code 401")

    def test_create_user_with_empty_token(self):
        data = {"token_srpg": ""}
        response = requests.post(url=self.url, json=data)
        self.assertEqual(response.json()['detail'], 'Invalid Token', msg="expected status code 401")

    def test_create_user_with_no_token_key(self):
        data = {}
        response = requests.post(url=self.url, json=data)
        self.assertEqual(response.status_code, 422, msg="expected status code 422")

    def test_create_correct_user(self):
        data = {"token_srpg": "BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"}
        response = requests.post(url=self.url, json=data)
        self.assertEqual(response.status_code, 201, msg="excpected status code 201")
        self.assertEqual(response.json()['token_srpg'], data['token_srpg'],
                         msg='excepted same token_srpg between response and data')

    def test_create_user_with_same_token(self):
        data = {"token_srpg": "BG%2FznOInEBpENjj%2B0Df9Lw%3D%3D"}
        response = requests.post(url=self.url, json=data)
        self.assertEqual(response.status_code, 422, msg="excpected status code 422 / value is not unique")

    @classmethod
    def tearDownClass(cls) -> None:
        SQLModel.metadata.drop_all(engine_test)


if __name__ == '__main__':
    unittest.main(failfast=True)
