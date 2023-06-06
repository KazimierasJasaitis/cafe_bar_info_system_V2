from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import data
import requests

from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.exc import IntegrityError
from flask import url_for

#####################SWAGGER
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafe_bar_info_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

SWAGGER_URL = '/api/docs' 
API_YAML_URL = '/static/swagger.yaml' 

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_YAML_URL,
    config={
        'app_name': "BAR_CAFE_IS"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
######################SWAGGER

menu_service_url = "http://menu_service:5000"

class User(db.Model):
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    managed_cafe_id = db.Column(db.Integer, db.ForeignKey("bar_cafe.id"))
    reputation_index = db.Column(db.Float, nullable=False, default=0)

    def __init__(self, username, password, email, role, managed_cafe_id, reputation_index):
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.managed_cafe_id = managed_cafe_id
        self.reputation_index = reputation_index


class UserSchema(ma.Schema):
    class Meta:
        fields = ("username", "password", "email", "role", "managed_cafe_id", "reputation_index")

bar_cafe_menu = Table(
    "bar_cafe_menu",
    db.Model.metadata,
    Column("bar_cafe_id", Integer, ForeignKey("bar_cafe.id"), primary_key=True),
    Column("dish_id", Integer, primary_key=True),
)



class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    __table_args__ = {'extend_existing': True}


class BarCafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    open_hours = db.Column(db.String(15), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey("user.username"), nullable=False)

    def __init__(self, name, location, open_hours, type, seats, user_id):
        self.name = name
        self.location = location
        self.open_hours = open_hours
        self.type = type
        self.seats = seats
        self.user_id = user_id


class BarCafeSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "location", "open_hours", "type", "seats", "user_id")


class SeatStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_cafe_id = db.Column(db.Integer, db.ForeignKey("bar_cafe.id"), nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey("user.username"), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)

    def __init__(self, bar_cafe_id, user_id, status, timestamp):
        self.bar_cafe_id = bar_cafe_id
        self.user_id = user_id
        self.status = status
        self.timestamp = timestamp


class SeatStatusSchema(ma.Schema):
    class Meta:
        fields = ("id", "bar_cafe_id", "user_id", "status", "timestamp")


class KarmaLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("user.username"), nullable=False)
    karma_points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, karma_points, timestamp):
        self.user_id = user_id
        self.karma_points = karma_points
        self.timestamp = timestamp

class KarmaLogSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "karma_points", "timestamp")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
bar_cafe_schema = BarCafeSchema()
bar_cafes_schema = BarCafeSchema(many=True)
seat_status_schema = SeatStatusSchema()
seat_statuses_schema = SeatStatusSchema(many=True)
karma_log_schema = KarmaLogSchema()
karma_logs_schema = KarmaLogSchema(many=True)

@app.route("/dishes", methods=["GET"])
def get_dishes():
    try:
        response = requests.get(f"{menu_service_url}/dishes")
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while fetching dishes from the menu-service."}), 500

def create_dish(dish_data):
    try:
        response = requests.post(f"{menu_service_url}/dishes", json=dish_data)
        response.raise_for_status()
        return response.json()["id"]
    except requests.exceptions.RequestException as e:
        return None

def update_dish(dish_id, dish_data):
    try:
        response = requests.put(f"{menu_service_url}/dishes/{dish_id}", json=dish_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return False
    return True

@app.route("/bar_cafe/<id>/menu", methods=['GET'])
def get_menu_for_cafe(id):
    cafe = BarCafe.query.get_or_404(id)

    try:
        response = requests.get(f"{menu_service_url}/dishes")
        response.raise_for_status()
        all_dishes = response.json()

        related_dishes = db.session.query(bar_cafe_menu).filter_by(bar_cafe_id=id).all()

        related_dish_ids = [dish.dish_id for dish in related_dishes]

        cafe_dishes = [dish for dish in all_dishes if dish['id'] in related_dish_ids]

        return jsonify(cafe_dishes), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "An error occurred while fetching dishes from the menu-service."}), 500


@app.route('/bar_cafe/<int:id>/menu', methods=['POST'])
def add_dish(id):
    cafe = BarCafe.query.get_or_404(id)
    dish_id = create_dish(request.json)
    if dish_id:
        relation = bar_cafe_menu.insert().values(bar_cafe_id=id, dish_id=dish_id)
        db.session.execute(relation)
        db.session.commit()
        return jsonify({"message": "Dish added to the cafe's menu", "cafe_id": id, "dish_id": dish_id}), 201
    else:
        return jsonify({"error": "An error occurred while adding the dish to the cafe's menu"}), 500


@app.before_first_request
def setup_initial_data():
    db.create_all()
    data.populate_initial_data(db.session, User, BarCafe, SeatStatus, KarmaLog)

@app.route("/bar_cafe", methods=["POST"])
def add_bar_cafe():
    name = request.json.get("name", None)
    location = request.json.get("location", None)
    open_hours = request.json.get("open_hours", None)
    type = request.json.get("type", None)
    seats = request.json.get("seats", None)
    user_id = request.json.get("user_id", None)
    if not name or name.strip() == "":
        return jsonify({"error": "Name cannot be empty or null."}), 400
    if not location or location.strip() == "":
        return jsonify({"error": "Location cannot be empty or null."}), 400
    if not open_hours:
        return jsonify({"error": "Open hours cannot be null."}), 400
    if not type or type.strip() == "":
        return jsonify({"error": "Type cannot be empty or null."}), 400
    if not seats:
        return jsonify({"error": "Seats cannot be null."}), 400
    if not user_id:
        return jsonify({"error": "User ID cannot be null."}), 400

    new_bar_cafe = BarCafe(name=name, location=location, open_hours=open_hours, type=type, seats=seats, user_id=user_id)
    try:
        db.session.add(new_bar_cafe)
        db.session.commit()
        response = jsonify(bar_cafe_schema.dump(new_bar_cafe))
        response.status_code = 201
        response.headers['Location'] = url_for('get_bar_cafe', id=new_bar_cafe.id, _external=True)
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the item."}), 500

@app.route("/bar_cafe", methods=["GET"])
def get_all_bar_cafes():
    try:
        all_bar_cafes = BarCafe.query.all()
        result = bar_cafes_schema.dump(all_bar_cafes)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching all items."}), 500

@app.route("/bar_cafe/<id>", methods=["GET"])
def get_bar_cafe(id):
    bar_cafe = BarCafe.query.get(id)
    if not bar_cafe:
        return jsonify({"error": "Item not found"}), 404

    try:
        # Get the list of dish ids for this cafe
        dish_relations = db.session.query(bar_cafe_menu).filter_by(bar_cafe_id=id).all()
        dish_ids = [relation.dish_id for relation in dish_relations]
        
        # Get dish data for those ids from the menu-service
        cafe_menu = []
        for dish_id in dish_ids:
            response = requests.get(f"{menu_service_url}/dishes/{dish_id}")
            response.raise_for_status()
            cafe_menu.append(response.json())
        
    except requests.exceptions.RequestException as e:
        cafe_menu = []
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the item."}), 500

    # Add the menu to the bar_cafe data
    bar_cafe_data = bar_cafe_schema.dump(bar_cafe)
    bar_cafe_data['menu'] = cafe_menu

    return jsonify(bar_cafe_data)




@app.route("/bar_cafe/<id>", methods=["PUT"])
def update_bar_cafe(id):
    bar_cafe = BarCafe.query.get(id)
    if not bar_cafe:
        return jsonify({"error": "item not found"}), 404

    name = request.json.get("name", None)
    location = request.json.get("location", None)
    open_hours = request.json.get("open_hours", None)
    type = request.json.get("type", None)
    seats = request.json.get("seats", None)
    user_id = request.json.get("user_id", None)

    if name is None or name.strip() == "":
        return jsonify({"error": "Name cannot be empty or null."}), 400

    if location is None or location.strip() == "":
        return jsonify({"error": "Location cannot be empty or null."}), 400

    if open_hours is None:
        return jsonify({"error": "Open hours cannot be null."}), 400

    if type is None or type.strip() == "":
        return jsonify({"error": "Type cannot be empty or null."}), 400

    if seats is None:
        return jsonify({"error": "Seats cannot be null."}), 400

    if user_id is None:
        return jsonify({"error": "User ID cannot be null."}), 400

    bar_cafe.name = name
    bar_cafe.location = location
    bar_cafe.open_hours = open_hours
    bar_cafe.type = type
    bar_cafe.seats = seats
    bar_cafe.user_id = user_id

    try:
        db.session.commit()
        response = bar_cafe_schema.jsonify(bar_cafe)
        response.headers['Location'] = url_for('get_bar_cafe', id=bar_cafe.id, _external=True)
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the item."}), 500
    

@app.route("/bar_cafe/<id>", methods=["DELETE"])
def delete_bar_cafe(id):
    try:
        bar_cafe = BarCafe.query.get(id)
        if not bar_cafe:
            return jsonify({"error": "Item not found"}), 404
        db.session.delete(bar_cafe)
        db.session.commit()
        return bar_cafe_schema.jsonify(bar_cafe)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the item."}), 500


@app.route("/user", methods=["POST"])
def add_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    email = request.json.get("email", None)
    role = request.json.get("role","user")
    managed_cafe_id = request.json.get("managed_cafe_id", None)
    reputation_index = request.json.get("reputation_index", 0)

    if not username or username.strip() == "":
        return jsonify({"error": "Username cannot be empty or null."}), 400
    
    if not email or email.strip() == "":
        return jsonify({"error": "e-mail cannot be empty or null."}), 400
    
    if role not in ["user", "admin"]:
        return jsonify({"error": "Role must be either 'user' or 'admin'."}), 400

    new_user = User(username=username, password=password, email=email, role=role, managed_cafe_id=managed_cafe_id, reputation_index=reputation_index)

    try:
        db.session.add(new_user)
        db.session.commit()
        response = jsonify(user_schema.dump(new_user))
        response.status_code = 201
        response.headers['Location'] = url_for('get_user', username=new_user.username, _external=True)
        return response
    except IntegrityError as e:
        db.session.rollback()
        error_detail = str(e.orig)
        
        if "user.email" in error_detail:
            error_message = "A user with this email already exists."
        elif "user.username" in error_detail:
            error_message = "A user with this username already exists."
        else:
            error_message = "An error occurred while adding the user."
        
        return jsonify({"error": error_message}), 409

@app.route("/user", methods=["GET"])
def get_all_users():
    try:
        all_users = User.query.all()
        result = users_schema.dump(all_users)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching users."}), 500

@app.route("/user/<username>", methods=["GET"])
def get_user(username):
    try:
        user = User.query.get(username)
        if user is not None:
            return user_schema.jsonify(user)
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the user."}), 500

@app.route("/user/<username>", methods=["PUT"])
def update_user(username):
    user = User.query.get(username)
    if user is None:
        return jsonify({"error": "User not found."}), 404

    password = request.json.get("password", None)
    email = request.json.get("email", None)
    role = request.json.get("role", "user")
    managed_cafe_id = request.json.get("managed_cafe_id", None)
    reputation_index = request.json.get("reputation_index", 0)

    if password is None or password.strip() == "":
        return jsonify({"error": "Password cannot be empty or null."}), 400

    if email is None or email.strip() == "":
        return jsonify({"error": "Email cannot be empty or null."}), 400

    if role is None or role.strip() == "" or role not in ["user", "admin"]:
        return jsonify({"error": "Role must be either 'user' or 'admin'."}), 400

    user.password = password
    user.email = email
    user.role = role
    user.managed_cafe_id = managed_cafe_id
    user.reputation_index = reputation_index

    try:
        db.session.commit()
        response = user_schema.jsonify(user)
        response.headers['Location'] = url_for('get_user', username=user.username , _external=True)
        return response
    except IntegrityError as e:
        db.session.rollback()
        error_detail = str(e.orig)

        if "user.email" in error_detail:
            error_message = "A user with this email already exists."
        else:
            error_message = "An error occurred while updating the user."

        return jsonify({"error": error_message}), 409

@app.route("/user/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        user = User.query.get(username)
        if user is not None:
            db.session.delete(user)
            db.session.commit()
            return user_schema.jsonify(user)
        else:
            return jsonify({"error": "User not found."}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the user."}), 500


@app.route("/seat_status", methods=["POST"])
def add_seat_status():
    bar_cafe_id = request.json.get("bar_cafe_id", None)
    user_id = request.json.get("user_id", None)
    status = request.json.get("status", None)
    timestamp = request.json.get("timestamp", None)

    if not bar_cafe_id or bar_cafe_id.strip() == "":
        return jsonify({"error": "bar_cafe_id is a required field."}), 400

    if not user_id or user_id.strip() == "":
        return jsonify({"error": "user_id is a required field."}), 400

    if not status or status.strip() == "":
        return jsonify({"error": "status is a required field."}), 400

    if not timestamp or timestamp.strip() == "":
        return jsonify({"error": "timestamp is a required field."}), 400

    new_seat_status = SeatStatus(bar_cafe_id=bar_cafe_id, user_id=user_id, status=status, timestamp=timestamp)
    try:
        db.session.add(new_seat_status)
        db.session.commit()
        response = jsonify(seat_status_schema.dump(new_seat_status))
        response.status_code = 201
        response.headers['Location'] = url_for('get_seat_status', id=new_seat_status.id, _external=True)
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the seat status."}), 500


@app.route("/seat_status", methods=["GET"])
def get_all_seat_statuses():
    try:
        all_seat_statuses = SeatStatus.query.all()
        result = seat_statuses_schema.dump(all_seat_statuses)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching seat statuses."}), 500
    
@app.route("/seat_status/<id>", methods=["GET"])
def get_seat_status(id):
    try:
        seat_status = SeatStatus.query.get(id)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the seat status."}), 500

    if not seat_status:
        return jsonify({"error": "Seat status not found"}), 404
    return seat_status_schema.jsonify(seat_status)


@app.route("/seat_status/<id>", methods=["PUT"])
def update_seat_status(id):
    try:
        seat_status = SeatStatus.query.get(id)
        if not seat_status:
            return jsonify({"error": "Seat status not found"}), 404

        bar_cafe_id = request.json.get("bar_cafe_id", None)
        user_id = request.json.get("user_id", None)
        status = request.json.get("status", None)
        timestamp = request.json.get("timestamp", None)

        if not bar_cafe_id or bar_cafe_id.strip() == "":
            return jsonify({"error": "bar_cafe_id is a required field."}), 400

        if not user_id or user_id.strip() == "":
            return jsonify({"error": "user_id is a required field."}), 400

        if not status or status.strip() == "":
            return jsonify({"error": "status is a required field."}), 400

        if not timestamp or timestamp.strip() == "":
            return jsonify({"error": "timestamp is a required field."}), 400

        seat_status.bar_cafe_id = bar_cafe_id
        seat_status.user_id = user_id
        seat_status.status = status
        seat_status.timestamp = timestamp

        db.session.commit()
        response = seat_status_schema.jsonify(seat_status)
        response.headers['Location'] = url_for('get_seat_status', id=seat_status.id, _external=True)
        return response
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the seat status."}), 500



@app.route("/seat_status/<id>", methods=["DELETE"])
def delete_seat_status(id):
    try:
        seat_status = SeatStatus.query.get(id)
        if not seat_status:
            return jsonify({"error": "Seat status not found"}), 404
        db.session.delete(seat_status)
        db.session.commit()

        return seat_status_schema.jsonify(seat_status)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the seat status."}), 500

@app.route("/karma_log", methods=["POST"])
def add_karma_log():
    user_id = request.json.get("user_id", None)
    karma_points = request.json.get("karma_points", None)
    timestamp = request.json.get("timestamp", None)

    if not user_id or user_id.strip() == "":
        return jsonify({"error": "user_id is a required field."}), 400

    if not karma_points or karma_points.strip() == "":
        return jsonify({"error": "karma_points is a required field."}), 400

    if not timestamp or timestamp.strip() == "":
        return jsonify({"error": "timestamp is a required field."}), 400

    new_karma_log = KarmaLog(user_id=user_id, karma_points=karma_points, timestamp=timestamp)
    
    try:
        db.session.add(new_karma_log)
        db.session.commit()
        response = jsonify(bar_cafe_schema.dump(new_karma_log))
        response.status_code = 201
        response.headers['Location'] = url_for('get_karma_log', id=new_karma_log.id, _external=True)
        return response
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the karma log."}), 409

@app.route("/karma_log", methods=["GET"])
def get_all_karma_logs():
    try:
        all_karma_logs = KarmaLog.query.all()
        result = karma_logs_schema.dump(all_karma_logs)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching all karma logs."}), 500


@app.route("/karma_log/<id>", methods=["GET"])
def get_karma_log(id):
    try:
        karma_log = KarmaLog.query.get(id)
        if not karma_log:
            return jsonify({"error": "Karma log not found"}), 404
        return karma_log_schema.jsonify(karma_log)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching the karma log."}), 500


@app.route("/karma_log/<id>", methods=["PUT"])
def update_karma_log(id):
    karma_log = KarmaLog.query.get(id)
    if not karma_log:
        return jsonify({"error": "Karma log not found"}), 404

    user_id = request.json.get("user_id", None)
    karma_points = request.json.get("karma_points", None)
    timestamp = request.json.get("timestamp", None)

    if not user_id or user_id.strip() == "":
        return jsonify({"error": "user_id is a required field."}), 400

    if not karma_points or karma_points.strip() == "":
        return jsonify({"error": "karma_points is a required field."}), 400

    if not timestamp or timestamp.strip() == "":
        return jsonify({"error": "timestamp is a required field."}), 400

    karma_log.user_id = user_id
    karma_log.karma_points = karma_points
    karma_log.timestamp = timestamp

    try:
        db.session.commit()
        response = karma_log_schema.jsonify(karma_log)
        response.headers['Location'] = url_for('get_karma_log', id=karma_log.id, _external=True)
        return response
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the karma log."}), 409

@app.route("/karma_log/<id>", methods=["DELETE"])
def delete_karma_log(id):
    try:
        karma_log = KarmaLog.query.get(id)
        if not karma_log:
            return jsonify({"error": "Karma log not found"}), 404
        db.session.delete(karma_log)
        db.session.commit()
        return karma_log_schema.jsonify(karma_log)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the karma log."}), 500
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
