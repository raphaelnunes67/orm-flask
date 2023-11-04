from sql_alchemy import database
from datetime import datetime


class UserModel(database.Model):
    __tablename__ = 'users'

    user_id = database.Column(database.Integer, primary_key=True)
    login = database.Column(database.String(40))
    password = database.Column(database.String(40))
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    modified_at = database.Column(database.DateTime, default=datetime.utcnow)

    def __init__(self, login, password) -> None:
        self.login = login
        self.password = password
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()

    def json(self) -> dict:
        return {
            'user_id': self.user_id,
            'login': self.login
        }

    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        if user:
            return user
        return None

    @classmethod
    def query_all(cls):
        users = cls.query.all()

        return users

    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None

    def save_user(self) -> None:
        database.session.add(self)
        database.session.commit()

    def delete_user(self) -> None:
        database.session.delete(self)
        database.session.commit()
