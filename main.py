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

# For SQLAlchemy to interact with SQLite
engine = create_engine("sqlite:///foodsaverplus.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# main = Blueprint("main", __name__)
app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(store_id):
    return session.query(Store).filter_by(store_id=store_id).first()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/browse')
def browse():
    posts = session.query(UserPost, Item, func.min(UserPost.exp_date)).join(Item).filter(UserPost.item_id == Item.item_id)\
    .group_by(UserPost.item_id, UserPost.price).all()
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
    if request.method == 'POST':
        Item.add(session, request.form['item_name'], request.form["item_desc"], str(os.urandom(8).hex()), None,
                 current_user.store_id)
        return redirect(url_for('index'))
    return render_template('add-item.html')


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
            # flash("Sign up successful.")
            # redirect("/")
    return render_template('/storesignup.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


app.run(debug=True)
