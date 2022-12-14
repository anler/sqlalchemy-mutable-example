import pickle

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import Mutable, MutableDict
from sqlalchemy.types import JSON

Base = declarative_base()
Session = sessionmaker()


class Account(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True)
    settings = sa.Column(MutableDict.as_mutable(JSON))


def main():
    engine = sa.create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    session = Session()

    session.add(Account(id=1, settings={"email_notifications": False}))
    session.commit()

    account = session.query(Account).get(1)
    cached_detached_account = pickle.loads(pickle.dumps(account))
    cached_persistent_account = session.merge(cached_detached_account, load=False)

    cached_persistent_account.settings["email_notifications"] = True

    # Both of these assertions fail
    assert sa.inspect(cached_persistent_account).modified, "instance not modified"
    assert (
        cached_persistent_account in cached_detached_account.settings._parents
    ), "instance not being tracked"
