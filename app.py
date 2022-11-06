from flask import Flask, jsonify
from flask_restful import Api
from resources.sysinfo import *
from resources.user import *
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from blocklist import BLACKLIST
from sql_alchemy import database
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['JWT_SECRET_KEY'] = 'DontTellAnyone'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=2)
database.init_app(app)

api = Api(app)
jwt = JWTManager(app)


api_v1_cors_config = {
    "origins": "*",
    "methods": ["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type", "Origin"],
    "expose_headers": ["Content-Disposition"],
}
CORS(app, resources={r"/api/*": api_v1_cors_config})


def create_admin_user() -> None:
    from models.user import UserModel
    if not UserModel.find_by_login('admin'):
        user = UserModel('admin', 'admin')
        user.save_user()


@app.before_first_request
def create_database() -> None:
    database.create_all()
    create_admin_user()
    # hostname = request.headers.get('Host')
    # print(hostname)


@jwt.token_in_blacklist_loader
def verify_blacklist(token):
    return token['jti'] in BLACKLIST


@jwt.revoked_token_loader
def access_token_invalid():
    return jsonify({'message': 'You have been logged out.'}), 401  # unauthorized


# SYSINFO/api/account/user/<id>
api.add_resource(SysInfo, '/api/sysinfo/<string:id>', methods=['GET', 'DELETE', 'PUT'])
api.add_resource(SysInfos, '/api/sysinfos/', methods=['POST'])  # USED
api.add_resource(SysInfosTable, '/api/sysinfos/', methods=['GET'])
api.add_resource(SysInfosExport, '/api/sysinfos/export/', methods=['POST'])
api.add_resource(SysInfoDeleteMany, '/api/sysinfos/clear/', methods=['DELETE'])

# USER
api.add_resource(User, '/api/account/user/<int:user_id>', methods=['GET', 'DELETE', 'PUT'])
api.add_resource(Users, '/api/account/users/', methods=['GET'])
api.add_resource(UserRegister, '/api/account/register/', methods=['POST'])
api.add_resource(UserLogin, '/api/account/login/', methods=['POST'])
api.add_resource(UserLogout, '/api/account/logout/', methods=['GET'])

# if __name__ == '__main__':
#     from sql_alchemy import database

#     database.init_app(app)
#     api_v1_cors_config = {
#         "origins": "*",
#         "methods": ["OPTIONS", "GET", "POST", "PATCH", "PUT", "DELETE"],
#         "allow_headers": ["Authorization", "Content-Type", "Origin"],
#         "expose_headers": ["Content-Disposition"],
#     }
#     CORS(app, resources={r"/api/*": api_v1_cors_config})
#     app.run(debug=True, host='0.0.0.0', port=8000)
#     # app.run(debug=True, host='127.0.0.1', port=8000)