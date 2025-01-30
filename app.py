from flask import request


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask import Flask, jsonify
from extension import db
from models import Planet, People, User, Favorite

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///starwars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/people', methods=['GET'])
def get_all_people():
    all_people = People.query.all()
    return jsonify([{"id": people.id, "name": people.name} for people in all_people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify({
            "id": person.id,
            "name": person.name,
            "height": person.height,
            "mass": person.mass,
            "hair_color": person.hair_color,
            "skin_color": person.skin_color,
            "eye_color": person.eye_color,
            "birth_year": person.birth_year,
            "gender": person.gender
        }), 200
    else:
        return jsonify({"error": "Character not found"}), 404


@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    
    return jsonify([{"id": planet.id, "name": planet.name} for planet in all_planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify({
            "id": planet.id,
            "name": planet.name,
            "climate": planet.climate,
            "terrain": planet.terrain,
            "population": planet.population
        }), 200
    else:
        return jsonify({"error": "Planet not fond"}), 404


@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()

    return jsonify([{"id": user.id, "username": user.username} for user in all_users]), 200

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)


    if not username:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    current_user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    favorite_list = []
    for fav in favorites:
        if fav.planet_id:
            planet = Planet.query.get(fav.planet_id)
            favorite_list.append({"type": "planet", "id": planet.id, "name": planet.name})
        elif fav.people_id:
            person = People.query.get(fav.people_id)
            favorite_list.append({"type": "people", "id": person.id, "name": person.name})

    return jsonify(favorite_list), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()
    favorite = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Planet added to favorites"}),201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
@jwt_required()
def add_favorite_people(people_id):
    current_user_id = get_jwt_identity() 
    favorite = Favorite(user_id=current_user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({"message": "Person added to favorites"}),201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()  
    favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites"}), 200
    else:
        return jsonify({"error": "Favorite not found"}), 404


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_people(people_id):
    current_user_id = get_jwt_identity() 
    favorite = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": " Person removed from favorites"}), 200
    else:
        return jsonify({"error": "Favorite not found"}),404
