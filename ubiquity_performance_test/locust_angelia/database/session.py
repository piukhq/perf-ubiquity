from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ubiquity_performance_test.config import settings

connection_string = urlparse(settings.DB_CONNECTION_URI)._replace(path=f"/{settings.HERMES_DB}").geturl()

engine = create_engine(connection_string)
db_session = scoped_session(sessionmaker(bind=engine, future=True))
