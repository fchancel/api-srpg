import logging

from click import style
from fastapi import FastAPI
import uvicorn

from config import Settings, get_settings
from api.core.events import create_start_app_handler
from api.routes.user_routes import router as user_routes
from api.routes.character_routes import router as character_routes
from api.routes.mission_routes import router as mission_routes


log = logging.getLogger("uvicorn")


def create_application(settings: Settings) -> FastAPI:
    # Logging
    log.info('\n')
    log.info(
        f"Loading settings from the environment... "
        f"[{ style(settings.environment, fg='cyan') }] ")

    # FastAPI application
    log.info("Creating application ...")
    api = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        docs_url=settings.documentation_url,
        debug=settings.environment == "dev"
    )

    # Routes
    log.info("  ... add routes ...")
    api.include_router(user_routes, prefix="/api")
    api.include_router(character_routes, prefix="/api")
    api.include_router(mission_routes, prefix="/api")
    # if settings.is_dev():
    # these routes are only for testing, they will not be present in prod
    # api.include_router(tests_routes, prefix="/api")

    # Event handlers registration
    log.info("  ... add events handlers ...")
    api.add_event_handler("startup", create_start_app_handler(settings))
    return api


api = create_application(get_settings())

if __name__ == "__main__":
    uvicorn.run("main:api", host="0.0.0.0", port=8000, reload=True)
