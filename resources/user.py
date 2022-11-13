from flask_restful import Resource, reqparse
from flask import session
from models.user import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blocklist import BLACKLIST

attributes = reqparse.RequestParser()
attributes.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank.")
attributes.add_argument('password', type=str, required=True, help="The field 'password' cannot be left blank.")


class User(Resource):
    # /users/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message': 'User not found'}, 404

    # @jwt_required
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            if user.login == 'admin':
                return {'message': 'admin can\'t be deleted.'}, 405
            else:
                user.delete_user()
                return {'message': 'User deleted'}, 200
        return {'message': 'User not found'}, 404

    def put(self, user_id):
        data = attributes.parse_args()

        if UserModel.find_by_login(data['login']):
            return {"message": "The login '{}' already exists.".format(data['login'])}

        user = UserModel.find_user(user_id)

        if user:
            user.save_user()
            return {'message': 'User updated successfully!'}, 200

        user = UserModel(**data)
        user.save_user()

        return {'message': 'User created successfully!'}, 201


class Users(Resource):

    @jwt_required
    def get(self):
        if session.get('login') == 'admin':
            users = UserModel.query_all()
            values = []
            for entry in users:
                values.append(entry.login)
            return {"users": values}, 200
        return {"message": "Unauthorized method"}, 401


class UserRegister(Resource):
    # /register
    def post(self):
        data = attributes.parse_args()

        if UserModel.find_by_login(data['login']):
            return {"message": "The login '{}' already exists.".format(data['login'])}

        user = UserModel(**data)
        user.save_user()

        return {'message': 'User created successfully!'}, 201


class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = attributes.parse_args()
        user = UserModel.find_by_login(data['login'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.user_id)
            session['login'] = data['login']
            return {'token': access_token, 'user_id': user.user_id}, 200
        return {'message': 'The username or password is incorrect.'}, 401  # Unauthorized


class UserLogout(Resource):

    @jwt_required
    def get(self):
        jwt_id = get_raw_jwt()['jti']  # JWT Token Identifier
        BLACKLIST.add(jwt_id)
        session['login'] = None
        return {'message': 'Logged out successfully!'}, 200
