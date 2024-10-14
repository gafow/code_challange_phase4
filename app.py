#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants')
def get_restaurants():
    restaurants = [restaurant.to_dict(only=('address', 'id', 'name')) for restaurant in Restaurant.query.all()]
    return make_response(restaurants, 200)

@app.route('/restaurants/<int:id>', methods = ['GET', 'DELETE'])
def getting_restaurants_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id==id).first()
    if not restaurant:
        error_response = {"error": "Restaurant not found"}
        return make_response(error_response, 404)
    
    if request.method == "GET":
        return make_response(restaurant.to_dict(only=('address','id','name','restaurant_pizzas')), 200)
    
    elif request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

@app.route('/pizzas')
def get_pizzas():
    pizzas = [pizza.to_dict(only= ('id', 'ingredients', 'name')) for pizza in Pizza.query.all()]
    return make_response(pizzas, 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    data = request.get_json()
    try:
        new_post = RestaurantPizza(
        price=data['price'],
        pizza_id=data['pizza_id'],
        restaurant_id=data['restaurant_id'],
        )
        db.session.add(new_post)
        db.session.commit()
        return make_response(new_post.to_dict(), 201)
    except ValueError:
            return make_response({'errors': ["validation errors"]}, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)