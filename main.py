import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(24).hex())

conn = sqlite3.connect('foodsaverplus.db', check_same_thread=False)
conn.execute("PRAGMA foreign_keys = 1")
cursor = conn.cursor()
conn.commit()


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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/store-signup')
def store_signup():
    return render_template('/storesignup.html')


app.run(debug=True)
