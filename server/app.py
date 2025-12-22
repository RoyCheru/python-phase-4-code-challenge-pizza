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
    response = [restaurant.to_dict() for restaurant in restaurants]
    return make_response(response, 200)

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        return make_response(restaurant.to_dict(), 200)
    except:
        return make_response({"error": "Restaurant not found"}, 404)

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = [pizza.to_dict() for pizza in pizzas]
    return make_response(response, 200)

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data["price"],
            restaurant_id=data["restaurant_id"],
            pizza_id=data["pizza_id"]
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return make_response(new_restaurant_pizza.to_dict(), 201)
    except ValueError as e:
        return make_response({"errors": [str(e)]}, 400)

@app.route("/restaurant_pizzas/<int:id>", methods=["PATCH"])
def update_restaurant_pizza(id):
    data = request.get_json()
    restaurant_pizza = RestaurantPizza.query.get(id)
    if "price" in data:
        restaurant_pizza.price = data["price"]
    db.session.commit()
    return make_response(restaurant_pizza.to_dict(), 200)

@app.route("/restaurant_pizzas/<int:id>", methods=["DELETE"])
def delete_restaurant_pizza(id):
    try:
        restaurant_pizza = RestaurantPizza.query.get(id)
        db.session.delete(restaurant_pizza)
        db.session.commit()
        return make_response({}, 204)
    except:
        return make_response({"error": "RestaurantPizza not found"}, 404)




if __name__ == "__main__":
    app.run(port=5555, debug=True)
