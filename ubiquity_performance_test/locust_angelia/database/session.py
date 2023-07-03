from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ubiquity_performance_test.settings import DB_CONNECTION_URI, HERMES_DB

connection_string = urlparse(DB_CONNECTION_URI)._replace(path=f"/{HERMES_DB}").geturl()

engine = create_engine(connection_string)
db_session = scoped_session(sessionmaker(bind=engine, future=True))
