from config import get_settings
from sqlmodel import SQLModel, create_engine


settings = get_settings()
engine = create_engine(settings.db_url(), echo=settings.db_echo)


def create_database():

    SQLModel.metadata.create_all(engine)
