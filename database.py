import sqlite3
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Identity, MetaData, CheckConstraint, \
    select, DateTime, Float, Boolean, Date
from sqlalchemy.orm import sessionmaker, Query, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from flask_login import UserMixin

# Uses SQLAlchemy to create the database and table objects.

Base = declarative_base()
# engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
# connection = engine.connect()
#
# table_name = 'posts'
#
# query = f'ALTER TABLE {table_name} MODIFY ;'
# connection.execute(query)

# conn = sqlite3.connect('flowershopdatabase.db', check_same_thread=False)
# conn.execute("PRAGMA foreign_keys = 1")
# conn.execute("ALTER TABLE posts DROP CONSTRAINT post_quantity>0")
# conn.execute("ALTER TABLE posts ADD CONSTRAINT post_quantity>=0")
# cursor = conn.cursor()
# conn.commit()

class Store(UserMixin, Base):

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

    def get_id(self):
        return self.store_id

    @staticmethod
    def set_address(session, store_id, street, city, state, country, zip):
        store = session.query(Store).filter_by(store_id=store_id).first()
        store.street = street
        store.city = city
        store.state = state
        store.country = country
        store.zip = zip

    @staticmethod
    def add(session, username, password, store_name, street, city, state, country, zip):
        new_store = Store(username, generate_password_hash(password, method="sha256"), store_name, street, city, state,
                          country, zip)
        session.add(new_store)
        session.commit()

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, username, password, store_name, street, city, state, country, zip):
        self.username = username
        self.password = password
        self.store_name = store_name
        self.street = street
        self.city = city
        self.state = state
        self.country = country
        self.zip = zip
        self.geocode = "standin"

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

    @staticmethod
    def add(session, item_name, item_desc, item_img, ing_id, store_id):
        session.add(Item(item_name, item_desc, item_img, ing_id, store_id))
        session.commit()

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

    def __init__(self, meal_id, ing_id):
        self.meal_id = meal_id
        self.ing_id = ing_id

    def __repr__(self):
        return f"({self.recipe_id}, {self.meal_id}, {self.ing_id})"


class UserPost(Base):
    __tablename__ = "posts"
    post_id = Column("post_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    item_id = Column("item_id", Integer, ForeignKey("items.item_id"), nullable=False)
    post_quantity = Column("post_quantity", Integer, CheckConstraint("post_quantity>=0"), nullable=False)
    price = Column("price", Float, nullable=False)
    exp_date = Column("exp_date", Date, nullable=False)
    post_timestamp = Column("post_timestamp", DateTime, nullable=False)
    active = Column("active", Boolean, nullable=False)

    @staticmethod
    def add_post(session, item_id, post_quantity, price, exp_date):
        active = True
        if post_quantity == 0:
            active = False
        post = UserPost(item_id, post_quantity, datetime.strptime(exp_date, '%Y-%m-%d'), price, datetime.utcnow(),
                        active)
        session.add(post)
        session.commit()

    @staticmethod
    def set_price(session, post_id, price):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.price = price
        session.commit()

    @staticmethod
    def set_active(session, post_id, isActive):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.active = isActive
        session.commit()

    @staticmethod
    def set_quantity(session, post_id, quantity):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.quantity = quantity
        session.commit()

    @staticmethod
    def set_exp(session, post_id, exp_date):
        post = session.query(UserPost).filter_by(post_id=post_id).first()
        post.exp_date = exp_date
        session.commit()

    def __init__(self, item_id, post_quantity, exp_date, price, post_timestamp, active):
        self.item_id = item_id
        self.post_quantity = post_quantity
        self.exp_date = exp_date
        self.price = price
        self.post_timestamp = post_timestamp
        self.active = active

    def __repr__(self):
        return f"({self.post_id}, {self.item_id}, {self.post_quantity}, {self.price}, {self.exp_date}, " \
               f"{self.post_timestamp}, {self.active})"


class Reservation(Base):
    __tablename__ = "reservations"
    rsvp_id = Column("rsvp_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
    rsvp_name = Column("rsvp_name", String, nullable=False)
    post_id = Column("post_id", Integer, ForeignKey("posts.post_id"), nullable=False)
    rsvp_quantity = Column("rsvp_quantity", Integer, CheckConstraint("rsvp_quantity>0"), nullable=False)
    rsvp_timestamp = Column("rsvp_timestamp", DateTime, nullable=False)

    def __init__(self, post_id, rsvp_name, rsvp_quantity):
        self.post_id = post_id
        self.rsvp_name = rsvp_name
        self.rsvp_quantity = rsvp_quantity
        self.rsvp_timestamp = datetime.utcnow()

    def __repr__(self):
        return f"({self.rsvp_id}, {self.rsvp_name}, {self.post_id}, {self.rsvp_quantity}, {self.rsvp_timestamp})"


# engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
# Base.metadata.create_all(bind=engine)
#
# Session = sessionmaker(bind=engine)
# session = Session()

# Reservation.__table__.drop(engine)

# class Res(Base):
#     __tablename__ = "res"
#     rsvp_id = Column("rsvp_id", Integer, Identity(start=0, cycle=True), primary_key=True, nullable=False)
#     post_id = Column("post_id", Integer, ForeignKey("posts.post_id"), nullable=False)
#     rsvp_quantity = Column("rsvp_quantity", Integer, CheckConstraint("rsvp_quantity>0"), nullable=False)
#     rsvp_timestamp = Column("rsvp_timestamp", DateTime, nullable=False)
#
#     def __init__(self, post_id, rsvp_quantity, rsvp_timestamp):
#         self.post_id = post_id
#         self.rsvp_quantity = rsvp_quantity
#         self.rsvp_timestamp = rsvp_timestamp
#
#     def __repr__(self):
#         return f"({self.rsvp_id}, {self.post_id}, {self.rsvp_quantity}, {self.rsvp_timestamp})"


# class Rsvp_Name (Base):
#     __tablename__ = "rsvp_name"
#     rsvp_id = Column("rsvp_id", Integer, primary_key=True, nullable=False)
#     rsvp_name = Column("rsvp_name", String, nullable=False)
#
#     def __init__(self, rsvp_id, rsvp_name):
#         self.rsvp_id = rsvp_id
#         self.rsvp_name = rsvp_name
#
#     def __repr__(self):
#         return f"({self.rsvp_id}, {self.rsvp_name})"
