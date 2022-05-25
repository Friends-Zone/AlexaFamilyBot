import threading

from sqlalchemy import Column, UnicodeText, Integer, String, Boolean

from haruka.modules.sql import BASE, SESSION
from haruka import SUDO_USERS

class SudoUsers(BASE):
    __tablename__ = "sudos"
    user_id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    reason = Column(UnicodeText)

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return f"<Sudo User {self.name} ({self.user_id})>"

    def to_dict(self):
        return {"user_id": self.user_id,
                "name": self.name}

SudoUsers.__table__.create(checkfirst=True)

SUDO_USERS_LOCK = threading.RLock()
SUDO_SETTING_LOCK = threading.RLock()
SUDO_LIST = set()
SUDOSTAT_LIST = set()

def gpromote_user(user_id, name):
    with SUDO_USERS_LOCK:
        user = SESSION.query(SudoUsers).get(user_id)
        if not user:
            user = SudoUsers(user_id, name)
        else:
            user.name = name

        SESSION.merge(user)
        SESSION.commit()
        __load_sudo_userid_list()

def ungpromote_user(user_id):
    with SUDO_USERS_LOCK:
        if user := SESSION.query(SudoUsers).get(user_id):
            SESSION.delete(user)

        SESSION.commit()
        __load_sudo_userid_list()

def get_sudo_list():
    try:
        return [x.to_dict() for x in SESSION.query(SudoUsers).all()]
    finally:
        SESSION.close()

def __load_sudo_userid_list():
    global SUDO_LIST
    try:
        SUDO_LIST = {x.user_id for x in SESSION.query(SudoUsers).all()}
    finally:
        SESSION.close()
