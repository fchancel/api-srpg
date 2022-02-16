import os
import logging
from dotenv import load_dotenv

from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings
from functools import lru_cache

import db_config

log = logging.getLogger('uvicorn')
load_dotenv(dotenv_path="config")

class Settings(BaseSettings):

    # ENVIRONMENT
    environment: str = 'dev'
    test: bool = False
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_url = 'http://localhost:8000/'


    def is_dev(self):
        return self.environment == 'dev'

    def is_test(self):
        return self.test

    # FASTAPI
    app_title: str = "SRPG API"
    app_description: str = "An Crazy API for SRPG"
    documentation_url: str = "/docs"


    # TOKEN
    secret_key: str = '2e816a6e37893d60b91cc8e4c6a4ce3805a875cd20407827972545c7af98fea7'
    secret_key_bot: str = '2e816a6e37893d60b91cc8e4c6a4ce3805a875cd20407827972545c7af98fea7'
    secret_key_bot: str = 'jg2roh8ne723sn3r8023fH8ha139dopze9ç912E32kjufzh8de23n892n743410d'
    
    algorithm_hash: str = 'HS256'
    access_token_expire_minutes_mail: int = 60 * 24
    access_token_expire_minutes_login: int = 60

    # DATABASE
    db_user: str = db_config.db_user
    db_password: str = db_config.db_password
    db_host: str = db_config.db_host
    db_port: str = db_config.db_port
    db_name: str = db_config.db_name
    db_echo: bool = False


    # SRPG 
    TOKEN_API_SRPG = os.getenv("TOKEN_API_SRPG")
    SRPG_URL_BASE = "https://shinobi-rpg.ovh"
    SRPG_URL_BASE_PROFILE = SRPG_URL_BASE + "/profil-"
    SRPG_URL_API_LAST_USER = f"{SRPG_URL_BASE}/api.php?function=getDerniers&tokenAPI={TOKEN_API_SRPG}"
    SRPG_URL_API_NINDO = f"{SRPG_URL_BASE}/api.php?function=getCitations&tokenAPI={TOKEN_API_SRPG}"
    SRPG_URL_CHARACTERS_TOKEN = f"{SRPG_URL_BASE}/api.php?function=getAccount&tokenAPI={TOKEN_API_SRPG}&crypt="
    SRPG_URL_MISSION_PERCENT = f"{SRPG_URL_BASE}/api.php?function=getPower&tokenAPI={TOKEN_API_SRPG}&id="

    def db_url(self):
        return f"mysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@ lru_cache()
def get_settings() -> Settings:
    settings = None
    try:
        settings = Settings()
    except ValueError as err:
        log.critical(err)
        exit(0)

    return settings
