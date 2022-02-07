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


