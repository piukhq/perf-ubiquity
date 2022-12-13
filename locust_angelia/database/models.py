from sqlalchemy import Table
from sqlalchemy.orm import relationship

from locust_angelia.database.db import DB

# These Reflect each database table we need to use, using metadata. Some redundant models that we aren't using at the
# moment (for the 'add_join database job'), but will leave these in, in case they are needed.


class User(DB().Base):
    __table__ = Table("user", DB().metadata, autoload_with=DB().engine)
    profile = relationship("UserDetail", backref="user", uselist=False)  # uselist = False sets one to one relation
    scheme_account_user_associations = relationship("SchemeAccountUserAssociation", backref="user")


class UserDetail(DB().Base):
    __table__ = Table("user_userdetail", DB().metadata, autoload_with=DB().engine)


class SchemeAccount(DB().Base):
    __table__ = Table("scheme_schemeaccount", DB().metadata, autoload_with=DB().engine)
    scheme_account_user_associations = relationship("SchemeAccountUserAssociation", backref="scheme_account")


class SchemeAccountUserAssociation(DB().Base):
    __table__ = Table("ubiquity_schemeaccountentry", DB().metadata, autoload_with=DB().engine)
