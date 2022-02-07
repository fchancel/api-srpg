import logging

from click import style
from config import Settings
from api.core.database import create_database

log = logging.getLogger('uvicorn')


def create_start_app_handler(settings: Settings) -> None:
    async def start_app() -> None:
        log.info("Event handler: start application")

        # Database
        log.info(
            f"Loading database settings ... "
            f"[ { style(settings.db_name, fg='cyan') }] on ")
        create_database()
    return start_app