import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Profile
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

load_dotenv()

project_root = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, instance_path=os.path.join(project_root, 'instance'), instance_relative_config=False)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

@app.route('/')
def main():
    return jsonify({"status", "Server running successfully"}), 200


@app.route('/api/sign-up', methods=['POST'])
def register():
    
    name = request.json.get('name', '')
    username = request.json.get('username')
    password = request.json.get('password')
    active = request.json.get('active', True)

    if not username:
        return jsonify({ "msg": "Username is required!"}), 400
    
    if not password:
        return jsonify({ "msg": "Password is required!"}), 400
    
    found = User.query.filter_by(username=username).first()
    if found:
        return jsonify({ "msg": "Username is already in use"}), 400

    user = User()
    user.name = name
    user.username = username
    user.password = generate_password_hash(password)
    user.active = active

    # Crear el perfil al momento de registrarno
    profile = Profile()
    user.profile = profile # vincular el perfil al usuario
    user.save()
    #db.session.add(user)
    #db.session.commit()

    if user:
        return jsonify({
            "status": "success",
            "message": "Register successfully, please sign in"
        })

    return jsonify({
        "status": "fail",
        "message": "Please try again later, or contact to administrator"
    })


@app.route('/api/sign-in', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username:
        return jsonify({ "msg": "Username is required!"}), 400
    
    if not password:
        return jsonify({ "msg": "Password is required!"}), 400
    
    user = User.query.filter_by(username=username, active=True).first()

    if not user:
        return jsonify({ "msg": "Credentials not match, please try again"}), 401
    
    if not check_password_hash(user.password, password):
        return jsonify({ "msg": "Credentials not match, please try again"}), 401
    
    expire_at = timedelta(days=1)
    access_token = create_access_token(identity=user.id, expires_delta=expire_at)

    return jsonify({
        "status": "success",
        "message": "Login successfully",
        "access_token": access_token,
        "currentUser": user.serialize()
    }), 200


@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    
    id = get_jwt_identity()

    user = User.query.filter_by(id=id).first()

    if not user.profile:
        #return jsonify({ "msg": "User has not profile"}), 200
        profile = Profile()
        user.profile = profile
        user.update()
        
        return jsonify(user.profile.serialize_full_info()), 200

    
    return jsonify(user.profile.serialize_full_info()), 200


@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    
    id = get_jwt_identity()
    user = User.query.filter_by(id=id).first()

    name = request.json.get('name', user.name)
    biography = request.json.get('biography', user.profile.biography)
    github = request.json.get('github', user.profile.github)
    linkedin = request.json.get('linkedin', user.profile.linkedin)

    user.name = name
    user.profile.biography = biography
    user.profile.github = github
    user.profile.linkedin = linkedin
    user.update()
        
    return jsonify({
        "status": "success", 
        "message": "Profile updated successfully!", 
        "profile": user.profile.serialize_full_info()
    }), 200


if __name__ == '__main__':
    app.run()