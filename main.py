import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, join
import os
from database import *
from dbManager import Checks
from datetime import date, datetime


# NOTE: Need to split this up to different py files in the future for cleanliness and readability. Also need to clean
#       imports when the project is in a stable place.


# For SQLAlchemy to interact with SQLite
engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

# Login Controls
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(store_id):
    return session.query(Store).filter_by(store_id=store_id).first()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        store = session.query(Store).filter_by(username=request.form["Username"]).first()
        if Checks.valid_login(session, request.form["Username"], request.form["Password"]):
            login_user(store, remember=True)
            # return redirect(url_for('index'))
    return render_template('login.html')


# Webpages
@app.route('/')
def index():
    return render_template('home.html')


# A browse page with a meal_id of 0 shows all posted items. Any number above that displays only ingredients for the
# meal with that meal_id.
@app.route('/browse/<int:meal_id>')
def browse(meal_id):
    if meal_id == 0:
        # Joins "posts", "items", and "recipes" tables while getting the soonest expiration date for an item posted at
        # a given price point.
        posts = session.query(UserPost, Item, Recipe, func.min(UserPost.exp_date)).select_from(UserPost).\
            join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .filter(UserPost.item_id == Item.item_id, Recipe.ing_id == Item.ing_id)\
            .group_by(UserPost.item_id, UserPost.price).all()
    else:
        # Joins "posts", "items", and "recipes" tables while getting the soonest expiration date for an item posted at
        # a given price point, and filters that to ingredients of the chosen meal.
        posts = session.query(UserPost, Item, Recipe, func.min(UserPost.exp_date)).select_from(UserPost)\
            .join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .filter(Recipe.meal_id == meal_id).group_by(UserPost.item_id, UserPost.price).all()
    return render_template('browse.html', posts=posts)


@app.route('/meals')
def meals():
    meals = session.query(Meal).all()
    return render_template('meal-suggestion.html', meals=meals)


@app.route('/find-store')
def find_store():
    return render_template('find-store.html')


@app.route('/view-item')
def view_item():
    return render_template('view-item.html')


@app.route('/reservation-confirmation')
def rsvp_conf():
    return render_template('RsvpConfirmation.html')


@app.route('/add-item', methods=('GET', 'POST'))
@login_required
def add_item():
    ingredients = session.query(Ingredient).all()
    if request.method == 'POST':
        ing_id = session.query(Ingredient).filter(Ingredient.ing_name == request.form["ingredient"]).first()
        if ing_id is not None:
            ing_id = ing_id.ing_id
        Item.add(session, request.form['item_name'], request.form["item_desc"], str(os.urandom(8).hex()), ing_id,
                 current_user.store_id)
        return redirect(url_for('index'))
    return render_template('add-item.html', ingredients=ingredients)


@app.route('/post-new')
@login_required
def post_new():
    return render_template('post-new.html')


@app.route('/post-item', methods=('GET', 'POST'))
@login_required
def post_item():
    items = session.query(Item).filter_by(store_id=current_user.store_id).all()
    if request.method == 'POST':
        UserPost.add_post(session, request.form["item"], request.form["quantity"], request.form["price"],
                          request.form["exp_date"])
        return redirect(url_for('post_conf'))
    return render_template('post-item.html', items=items)


@app.route('/post-confirmation')
def post_conf():
    return render_template('PostConfirmation.html')


@app.route('/store-signup', methods=('GET', 'POST'))
def store_signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form["password"] != request.form["confirm-password"]:
            flash("Passwords do not match.")
            return render_template('/storesignup.html')

        if not Checks.valid_username(session, request.form["username"]):
            flash("Username already exists.")
            return render_template('/storesignup.html')

        if not Checks.valid_address(session,request.form["street-address"], request.form["city"], request.form["state"],
                                    request.form["country"], request.form["zip-code"]):
            flash("An account already exists using this address.")
            return render_template('/storesignup.html')

        if request.form["password"] is not None and request.form["store-name"] is not None:
            Store.add(session, request.form["username"], request.form["password"], request.form["store-name"],
                      request.form["street-address"], request.form["city"], request.form["state"],
                      request.form["country"], request.form["zip-code"])
            return redirect(url_for('login'))
    return render_template('/storesignup.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


app.run(debug=True)
