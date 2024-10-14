from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )
    pizzas = association_proxy(
        "restaurant_pizzas",
        "pizza",
        creator=lambda pizza_obj: RestaurantPizza(pizza=pizza_obj),
    )

    # add serialization rules
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza")
    restaurants = association_proxy(
        "restaurant_pizzas",
        "restaurant",
        creator=lambda restaurant_obj: RestaurantPizza(restaurant=restaurant_obj),
    )

    # add serialization rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # add relationships
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # add serialization rules
    serialize_rules = (
        "-restaurant.restaurant_pizzas",
        "-pizza.restaurant_pizzas",
    )

    # add validation
    @validates("price")
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    @validates("restaurant_id")
    def validate_restaurant_id(self, key, restaurant_id):
        if restaurant_id is None:
            raise ValueError("Restaurant ID is required")
        return restaurant_id

    @validates("pizza_id")
    def validate_pizza_id(self, key, pizza_id):
        if pizza_id is None:
            raise ValueError("Pizza ID is required")
        return pizza_id

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"