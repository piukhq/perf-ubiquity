from sqlalchemy import Table
from sqlalchemy.orm import DeclarativeMeta, declarative_base, relationship
from sqlalchemy.sql.schema import MetaData

from ubiquity_performance_test.locust_angelia.database.session import engine

metadata = MetaData()
Base: DeclarativeMeta = declarative_base(metadata=metadata)


class User(Base):
    __table__ = Table("user", metadata, autoload_with=engine)
    profile = relationship("UserDetail", backref="user", uselist=False)  # uselist = False sets one to one relation
    scheme_account_user_associations = relationship("SchemeAccountUserAssociation", backref="user")


class UserDetail(Base):
    __table__ = Table("user_userdetail", metadata, autoload_with=engine)


class SchemeAccount(Base):
    __table__ = Table("scheme_schemeaccount", metadata, autoload_with=engine)
    scheme_account_user_associations = relationship("SchemeAccountUserAssociation", backref="scheme_account")


class SchemeAccountUserAssociation(Base):
    __table__ = Table("ubiquity_schemeaccountentry", metadata, autoload_with=engine)
