from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Identity, MetaData, CheckConstraint, \
    select, DateTime, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query
from flask import Flask

# Uses SQLAlchemy to create the database and table objects for database management.

Base = declarative_base()


class Store(Base):
    __tablename__ = "stores"
    store_id = Column("store_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    username = Column("username", String, unique=True, nullable=False)
    password = Column("password", String, nullable=False)
    store_name = Column("store_name", String, nullable=False)
    street = Column("street", String, nullable=False)
    city = Column("city", String, nullable=False)
    state = Column("state", String, nullable=False)
    country = Column("country", String, nullable=False)
    zip = Column("zip", Integer, nullable=False)
    geocode = Column("geocode", String, nullable=False)

    @staticmethod
    def set_address(store_id, street, city, state, country, zip):
        store = session.query(Store).filter_by(store_id=store_id).first()
        store.street = street
        store.city = city
        store.state = state
        store.country = country
        store.zip = zip
        session.commit()

    def __init__(self, username, password, store_name, street, city, state, country, zip):
        self.username = username
        self.password = password
        self.store_name = store_name
        self.street = street
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip
        self.geocode="standin"

    def __repr__(self):
        return f"({self.store_id}, {self.username}, {self.password}, {self.store_name}, {self.street}, {self.city}, " \
               f"{self.state}, {self.country}, {self.zip}, {self.geocode})"


class Item(Base):
    __tablename__ = "items"
    item_id = Column("item_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    item_name = Column("item_name", String, nullable=False)
    item_desc = Column("item_desc", String)
    item_img = Column("item_img", String, unique=True)
    ing_id = Column("ing_id", Integer, ForeignKey("ingredients.ing_id"))
    store_id = Column("store_id", Integer, ForeignKey("stores.store_id"), nullable=False)

    def __init__(self, item_name, item_desc, item_img, ing_id, store_id):
        self.item_name = item_name
        self.item_desc = item_desc
        self.item_img = item_img
        self.ing_id = ing_id
        self.store_id = store_id

    def __repr__(self):
        return f"({self.item_id}, {self.item_name}, {self.item_desc}, {self.item_img}, {self.ing_id}, {self.store_id})"


class Ingredient(Base):
    __tablename__ = "ingredients"
    ing_id = Column("ing_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    ing_name = Column("ing_name", String, nullable=False, unique=True)

    def __init__(self, ing_name):
        self.ing_name = ing_name

    def __repr__(self):
        return f"({self.ing_id}, {self.ing_name})"


class Meal(Base):
    __tablename__ = "meals"
    meal_id = Column("meal_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    meal_name = Column("meal_name", String, nullable=False)
    meal_img = Column("meal_img", String, nullable=False)

    def __init__(self, meal_name, meal_img):
        self.meal_name = meal_name
        self.meal_img = meal_img

    def __repr__(self):
        return f"({self.meal_id}, {self.meal_name}, {self.meal_img})"


class Recipe(Base):
    __tablename__ = "recipes"
    recipe_id = Column("recipe_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    meal_id = Column("meal_id", Integer, ForeignKey("meals.meal_id"), nullable=False)
    ing_id = Column("ing_id", Integer, ForeignKey("ingredients.ing_id"), nullable=False)

    def __int__(self, meal_id, ing_id):
        self.meal_id = meal_id
        self.ing_id = ing_id

    def __repr__(self):
        return f"({self.recipe_id}, {self.meal_id}, {self.ing_id})"


class UserPost(Base):
    __tablename__ = "posts"
    post_id = Column("post_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    item_id = Column("item_id", Integer, ForeignKey("items.item_id"), nullable=False)
    post_quantity = Column("post_quantity", Integer, CheckConstraint("post_quantity>0"), nullable=False)
    price = Column("price", Float, nullable=False)
    exp_date = Column("exp_date", Date, nullable=False)
    post_timestamp = Column("post_timestamp", DateTime, nullable=False)
    active = Column("active", Boolean, nullable=False)

    @staticmethod
    def set_price(post_id, price):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.price = price
        session.commit()

    @staticmethod
    def set_active(post_id, isActive):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.active = isActive
        session.commit()

    @staticmethod
    def set_quantity(post_id, quantity):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.quantity = quantity
        session.commit()

    @staticmethod
    def set_exp(post_id, exp_date):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.exp_date = exp_date
        session.commit()

    def __int__(self, item_id, post_quantity, exp_date, post_timestamp, status):
        self.item_id = item_id
        self.post_quantity = post_quantity
        self. exp_date = exp_date
        self.post_timestamp = post_timestamp
        self.status = status

    def __repr__(self):
        return f"({self.post_id}, {self.item_id}, {self.post_quantity}, {self.exp_date}, {self.post_timestamp}, " \
               f"{self.status})"


class Reservation(Base):
    __tablename__ = "reservations"
    rsvp_id = Column("rsvp_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    post_id = Column("post_id", Integer, ForeignKey("posts.post_id"), nullable=False)
    rsvp_quantity = Column("rsvp_quantity", Integer, CheckConstraint("rsvp_quantity>0"), nullable=False)
    rsvp_timestamp = Column("rsvp_timestamp", DateTime, nullable=False)

    def __int__(self, post_id, rsvp_quantity, rsvp_timestamp):
        self.post_id = post_id
        self.rsvp_quantity = rsvp_quantity
        self.rsvp_timestamp = rsvp_timestamp

    def __repr__(self):
        return f"({self.rsvp_id}, {self.post_id}, {self.rsvp_quantity}, {self.rsvp_timestamp})"


engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# store1 = Store("username1", "password1", "kroger", "185 brown rd", "stockbridge", "ga", "united states", 30281)
# store2 = Store("username2", "password2", "kroger2", "186 brown rd", "stockbridge", "ga", "united states", 30281)
#
# ing1 = Ingredient("spaghetti")
#
# item1 = Item("spaghetti", "it's spaghetti", "../static/Images/spaghetti.png", 1, 2)


# session.add(store1)
# session.add(store2)
# session.add(ing1)
# session.add(item1)
# session.commit()

# results = session.query(Store).all()
# print(results)
# results = session.query(Ingredient).all()
# print(results)
# results = session.query(Item).all()
# print(results)