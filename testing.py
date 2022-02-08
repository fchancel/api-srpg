# from characters.models.character_models import get_characters
# from characters.services.character_services import delete_connexion_with_character
# from sqlmodel import Session
# from core.database import engine
# from users.models.user_models import get_user

# data = [{"id": "1482", "name": "Chikara Takehiko", "village": "Konoha", "avatar": "\/image\/avatars\/Chikara_Takehiko_miniAva1.jpg?avatar=470802"},
#         {"id": "843", "name": "Hattori Raika", "village": "Kumo",
#             "avatar": "\/image\/avatars\/Hattori_Raika_miniAva9.jpg?avatar=369148"},
#         {"id": "842", "name": "Hattori Reika", "village": "Kumo",
#             "avatar": "\/image\/avatars\/Hattori_Reika_miniAva6.jpg?avatar=370566"},
#         {"id": "1346", "name": "Hattori Satoko", "village": "Kumo",
#         "avatar": "\/image\/avatars\/Hattori_Satoko_miniAva1.jpg?avatar=343491"},
#         {"id": "1544", "name": "Kirishitan Ayana", "village": "Konoha",
#         "avatar": "\/image\/avatars\/Kirishitan_Ayana_miniAva1.jpg?avatar=464756"},
#         {"id": "1469", "name": "Minashigo Kodoku", "village": "Errant",
#         "avatar": "\/image\/avatars\/Minashigo_Kodoku_miniAva3.png?avatar=931290"},
#         {"id": "305", "name": "Miwaku Genichi", "village": "Kumo",
#         "avatar": "\/image\/avatars_v1\/68692816ec62877599.jpg"},
#         ]

# with Session(engine) as db:
#     user = get_user(db, email="user@example.com")
#     characters_user = get_characters(db, user.id)
#     # print(characters_user)
#     delete_connexion_with_character(db, user,data, characters_user)

from datetime import datetime, timedelta

def check_if_finish_time(begin_time, rank, additionnal_time):
    if datetime.now() < (begin_time + timedelta(hours=3) + timedelta(minutes=additionnal_time)):
        return False
    return True

def get_finish_time(begin_time, rank, additionnal_time):
    return begin_time + timedelta(hours=3) + timedelta(minutes=additionnal_time)


def get_time_left(finish_time):
    if finish_time < datetime.now():
        return 0
    else:
        return finish_time - datetime.now()


print(f"datetime now: {datetime.now()}")
begin_time = datetime.now() - timedelta(hours=3, minutes=51)
print(f"begin time : {begin_time}")
finish_time = get_finish_time(begin_time, 3, 60)
print(f"finish time : {finish_time}")
time_left = get_time_left(finish_time)
print(f"left time : {time_left}")