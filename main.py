import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from database import *
from dbManager import Checks

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
    return render_template('browse.html')


@app.route('/meals')
def meals():
    return render_template('meal-suggestion.html')


@app.route('/find-store')
def find_store():
    return render_template('find-store.html')


@app.route('/view-item')
def view_item():
    return render_template('view-item.html')


@app.route('/reservation-confirmation')
def rsvp_conf():
    return render_template('RsvpConfirmation.html')


@app.route('/add-item')
def add_item():
    return render_template('add-item.html')


@app.route('/post-confirmation')
def post_conf():
    return render_template('PostConfirmation.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        store = session.query(Store).filter_by(username=request.form["Username"]).first()
        if Checks.valid_login(session, request.form["Username"], request.form["Password"]):
            login_user(store, remember=True)
            return render_template('login.html')
    return render_template('login.html')


@app.route('/store-signup', methods=('GET', 'POST'))
def store_signup():
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
    return redirect(url_for('index'))


app.run(debug=True)
