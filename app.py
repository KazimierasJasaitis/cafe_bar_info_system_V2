from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class CafeBar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    open_hours = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    seats = db.Column(db.Integer, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    data.populate_initial_data(db.session, CafeBar)

@app.route("/cafes_and_bars", methods=["GET", "POST"])
def cafes_and_bars():
    if request.method == "GET":
        cafes_and_bars = CafeBar.query.all()
        return jsonify([cb.as_dict() for cb in cafes_and_bars])

    if request.method == "POST":
        new_cafe_bar = CafeBar(**request.json)
        db.session.add(new_cafe_bar)
        db.session.commit()
        return jsonify(new_cafe_bar.as_dict()), 201

@app.route("/cafes_and_bars/<int:id>", methods=["GET", "PUT", "DELETE"])
def cafe_bar(id):
    cafe_bar = CafeBar.query.get(id)

    if cafe_bar is None:
        return jsonify({"error": "Cafe/Bar not found"}), 404

    if request.method == "GET":
        return jsonify(cafe_bar.as_dict())

    if request.method == "PUT":
        for key, value in request.json.items():
            setattr(cafe_bar, key, value)
        db.session.commit()
        return jsonify(cafe_bar.as_dict())

    if request.method == "DELETE":
        db.session.delete(cafe_bar)
        db.session.commit()
        return jsonify({"message": "Cafe/Bar deleted"}), 200

CafeBar.as_dict = lambda self: {
    "id": self.id,
    "name": self.name,
    "location": self.location,
    "open_hours": self.open_hours,
    "type": self.type,
    "seats": self.seats,
}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
