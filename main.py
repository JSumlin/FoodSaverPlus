import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, func, desc, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, join
import os
from database import *
from dbManager import Checks
from datetime import date, datetime
from werkzeug.utils import secure_filename
import uuid as uuid
from browse import browse
from database import session


# NOTE: Need to split this up to different py files in the future for cleanliness and readability. Also need to clean
#       imports when the project is in a stable place.

app = Flask(__name__)
app.register_blueprint(browse, url_prefix='/browse')
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# User authentication controls
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


# Webpages
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/meals')
def meals():
    meals = session.query(Meal).all()
    return render_template('meal-suggestion.html', meals=meals)


# Needs implementation
# @app.route('/find-store')
# def find_store():
#     return render_template('find-store.html')


@app.route('/reservation-confirmation/<int:store_id>')
def rsvp_conf(store_id):
    store = session.query(Store).filter_by(store_id=store_id).first()
    return render_template('RsvpConfirmation.html', store=store)


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


# Needs implementation
# @app.route('/post-new')
# @login_required
# def post_new():
#     return render_template('post-new.html')


@app.route('/post-item', methods=('GET', 'POST'))
@login_required
def post_item():
    items = session.query(Item).filter_by(store_id=current_user.store_id).all()
    if request.method == 'POST':
        dateinput = datetime.strptime(request.form["exp_date"], '%Y-%m-%d')
        if dateinput.date() < date.today():
            return render_template('post-item.html', items=items)
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


@app.route('/reservations')
@login_required
def reservations():
    reservations = session.query(Reservation, UserPost, Item).select_from(Reservation)\
        .join(UserPost, UserPost.post_id == Reservation.post_id).join(Item, Item.item_id == UserPost.item_id)\
        .filter(Item.store_id == current_user.store_id).all()
    return render_template('reservations.html', reservations=reservations)


app.run(debug=True)
