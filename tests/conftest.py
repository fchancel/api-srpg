from sqlmodel import create_engine
import db_config

db_user: str = db_config.db_user_test
db_password: str = db_config.db_password_test
db_host: str = db_config.db_host_test
db_port: str = db_config.db_port_test
db_name: str = db_config.db_name_test


def db_url_test():
    return f"mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine_test = create_engine(db_url_test(), echo=False)
