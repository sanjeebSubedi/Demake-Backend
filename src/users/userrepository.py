from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

# Repository class
class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id):
        try:
            user = self.session.query(user).filter(user.id == user_id).one_or_none()
            return user
        except NoResultFound:
            return None

    def find_by_email(self, email):
        try:
            user = self.session.query(user).filter(user.email == email).one_or_none()
            return user
        except NoResultFound:
            return None
