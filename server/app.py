#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()

    response = [
        restaurant.to_dict(only=("id", "name", "address"))
        for restaurant in restaurants
    ]

    return make_response(response, 200)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    response = restaurant.to_dict(
        only=("id", "name", "address"),
        include={
            "restaurant_pizzas": {
                "only": ("id", "price", "pizza_id", "restaurant_id"),
                "include": {
                    "pizza": {
                        "only": ("id", "name", "ingredients")
                    }
                }
            }
        }
    )

    return make_response(response, 200)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    db.session.delete(restaurant)
    db.session.commit()

    return make_response("", 204)


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()

    response = [
        pizza.to_dict(only=("id", "name", "ingredients"))
        for pizza in pizzas
    ]

    return make_response(response, 200)


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        response = restaurant_pizza.to_dict(
            only=("id", "price", "pizza_id", "restaurant_id"),
            include={
                "pizza": {
                    "only": ("id", "name", "ingredients")
                },
                "restaurant": {
                    "only": ("id", "name", "address")
                }
            }
        )

        return make_response(response, 201)

    except Exception:
        db.session.rollback()
        return make_response(
            {"errors": ["validation errors"]},
            400
        )



if __name__ == "__main__":
    app.run(port=5555, debug=True)
