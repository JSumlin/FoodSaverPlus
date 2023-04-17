import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, join
import os
from database import *
from dbManager import Checks
from datetime import date, datetime
from werkzeug.utils import secure_filename
import uuid as uuid


# NOTE: Need to split this up to different py files in the future for cleanliness and readability. Also need to clean
#       imports when the project is in a stable place.


# For SQLAlchemy to interact with SQLite
engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return redirect(url_for('index'))
    return render_template('login.html')


# Calculates the quantity available for "view item" pages.
def calc_quantity(viewed_posts):
    quantity = 0
    for viewed_post, item in viewed_posts:
        quantity = quantity + viewed_post.post_quantity
    return quantity


# When a user is on a "view item" page, that page is for all posts for that item at the stated price point. This returns
# all relevant posts to be used in reservation processes.
def get_viewed_posts(post):
    return session.query(UserPost, Item).select_from(UserPost). \
        join(Item, Item.item_id == UserPost.item_id)\
        .filter(Item.item_id == post.item_id, UserPost.price == post.price, UserPost.active == True)\
        .order_by(UserPost.exp_date).all()

# Webpages
@app.route('/')
def index():
    return render_template('home.html')


# A browse page with a meal_id of 0 shows all posted items. Any number above that displays only ingredients for the
# meal with that meal_id.
@app.route('/browse/<int:meal_id>')
def browse(meal_id):
    current_date = date.today()
    posts = session.query(UserPost).filter(UserPost.active == True).order_by(UserPost.exp_date).all()
    for post in posts:
        if post.exp_date < current_date:
            post.active = False
        elif post.exp_date > current_date:
            break
    session.commit()
    if meal_id == 0:
        # Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
        # posted at a given price point.
        posts = session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost).\
            join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .join(Store, Store.store_id == Item.store_id).filter(UserPost.active == True)\
            .group_by(UserPost.item_id, UserPost.price).all()
    else:
        # Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
        # posted at a given price point, and filters that to ingredients of the chosen meal.
        posts = session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost)\
            .join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .join(Store, Store.store_id == Item.store_id).filter(Recipe.meal_id == meal_id, UserPost.active == True)\
            .group_by(UserPost.item_id, UserPost.price).all()
    return render_template('browse.html', posts=posts, meal_id=meal_id)


@app.route('/meals')
def meals():
    meals = session.query(Meal).all()
    return render_template('meal-suggestion.html', meals=meals)


@app.route('/find-store')
def find_store():
    return render_template('find-store.html')


@app.route('/browse/<int:meal_id>/<int:post_id>', methods=('GET', 'POST'))
def view_item(meal_id, post_id):
    post = session.query(UserPost).filter_by(post_id=post_id).first()
    item = session.query(Item).filter_by(item_id=post.item_id).first()
    viewed_posts = get_viewed_posts(post)
    max_quantity = int(calc_quantity(viewed_posts))

    if request.method == 'POST':
        rsvp_quantity = int(request.form['quantity'])

        if rsvp_quantity > max_quantity or rsvp_quantity < 1:
            flash(f"The quantity requested exceeds the amount available. You may only reserve {max_quantity} at this "
                  f"time.")
            return render_template('view-item.html', post=post, item=item, meal_id=meal_id, max=max_quantity)

        # Atomic transaction subtracting the appropriate quantity from the "posts" table and adding it to the
        # "reservations" table. Also labels posts as inactive if their quantity reaches 0.
        try:
            for viewed_post, viewed_item in viewed_posts:
                if rsvp_quantity >= int(viewed_post.post_quantity):
                    session.add(Reservation(viewed_post.post_id, viewed_post.post_quantity))
                    rsvp_quantity = rsvp_quantity - int(viewed_post.post_quantity)
                    viewed_post.post_quantity = 0
                    viewed_post.active = False
                else:
                    viewed_post.post_quantity = viewed_post.post_quantity - rsvp_quantity
                    session.add(Reservation(viewed_post.post_id, rsvp_quantity))
                    rsvp_quantity = 0
                if rsvp_quantity == 0:
                    break
            session.commit()
            return redirect(url_for('rsvp_conf'))
        except sqlite3.Error():
            flash("An error occurred while placing your reservation. Please Try again.")

    return render_template('view-item.html', post=post, item=item, meal_id=meal_id, max=max_quantity)


@app.route('/reservation-confirmation')
def rsvp_conf():
    return render_template('RsvpConfirmation.html')


@app.route('/add-item', methods=('GET', 'POST'))
@login_required
def add_item():
    ingredients = session.query(Ingredient).all()
    if request.method == 'POST':
        img_name = secure_filename(request.files['image'].filename)
        img_name = 'Images/' + str(uuid.uuid1()) + "_" + img_name
        request.files['image'].save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
        ing_id = session.query(Ingredient).filter(Ingredient.ing_name == request.form["ingredient"]).first()
        if ing_id is not None:
            ing_id = ing_id.ing_id
        Item.add(session, request.form['item_name'], request.form["item_desc"], img_name, ing_id,
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
    inputs = ["", "", "", "", "", "", ""]
    if request.method == 'POST':
        inputs = [request.form["username"], request.form["store-name"],
                  request.form["street-address"], request.form["city"], request.form["state"],
                  request.form["country"], request.form["zip-code"]]
        if request.form["password"] != request.form["confirm-password"]:
            flash("Passwords do not match.")
            return render_template('/storesignup.html', inputs=inputs)

        if not Checks.valid_username(session, request.form["username"]):
            flash("Username already exists.")
            return render_template('/storesignup.html', inputs=inputs)

        if not Checks.valid_address(session,request.form["street-address"], request.form["city"], request.form["state"],
                                    request.form["country"], request.form["zip-code"]):
            flash("An account already exists using this address.")
            return render_template('/storesignup.html', inputs=inputs)

        if request.form["password"] is not None and request.form["store-name"] is not None:
            Store.add(session, request.form["username"], request.form["password"], request.form["store-name"],
                      request.form["street-address"], request.form["city"], request.form["state"],
                      request.form["country"], request.form["zip-code"])
            return redirect(url_for('login'))
    return render_template('/storesignup.html', inputs=inputs)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

# item = session.query(Item).first()
# item.item_img = 'Images/' + item.item_img
# session.commit()
# print(date.today())
app.run(debug=True)
