from sqlmodel import Session
from config import get_settings
from sqlmodel import SQLModel, create_engine
from api.crud import get_village, create_village

settings = get_settings()
engine = create_engine(settings.db_url(), echo=settings.db_echo)


def create_database():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        village = get_village(db, 'Konoha')
        if not village:
            create_village(db, "Kumo")
            create_village(db, "Konoha")
            create_village(db, "Errant")
