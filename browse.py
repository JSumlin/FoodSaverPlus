from sqlalchemy import func
from datetime import date
from database import session
from database import *
from flask import Flask, render_template, request, url_for, flash, redirect, Blueprint

browse = Blueprint("browse", __name__, static_folder='static', template_folder='templates')


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


# Used in browse page
# Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
# posted at a given price point.
def get_all_posts():
    return session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost).\
            join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .join(Store, Store.store_id == Item.store_id).filter(UserPost.active == True)\
            .group_by(UserPost.item_id, UserPost.price).order_by(UserPost.exp_date).all()


# Used in browse page
# Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
# posted at a given price point, and filters that to ingredients of the chosen meal.
def filter_by_meal(meal_id):
    return session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost)\
            .join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id)\
            .join(Store, Store.store_id == Item.store_id).filter(Recipe.meal_id == meal_id, UserPost.active == True)\
            .group_by(UserPost.item_id, UserPost.price).order_by(UserPost.exp_date).all()


# Used in browse page
# Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
# posted at a given price point, and filters that to items posted by a chosen store.
def filter_by_store(store_id):
    return session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost). \
            join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id) \
            .join(Store, Store.store_id == Item.store_id).filter(UserPost.active == True, Item.store_id == store_id) \
            .group_by(UserPost.item_id, UserPost.price).order_by(UserPost.exp_date).all()


# Used in browse page
# Joins "posts", "items", "recipes", and "stores" tables while getting the soonest expiration date for an item
# posted at a given price point, and filters that to ingredients of a chosen meal posted by a chosen store.
def filter_by_both(store_id, meal_id):
    return session.query(UserPost, Item, Recipe, Store, func.min(UserPost.exp_date)).select_from(UserPost) \
            .join(Item, Item.item_id == UserPost.item_id).join(Recipe, Recipe.ing_id == Item.ing_id) \
            .join(Store, Store.store_id == Item.store_id)\
            .filter(Recipe.meal_id == meal_id, UserPost.active == True, Item.store_id == store_id)\
            .group_by(UserPost.item_id, UserPost.price).order_by(UserPost.exp_date).all()


# Sets posts which pass their sell-by date as inactive
def clear_old_posts():
    current_date = date.today()
    posts = session.query(UserPost).filter(UserPost.active == True).order_by(UserPost.exp_date).all()
    for post in posts:
        if post.exp_date < current_date:
            post.active = False
        elif post.exp_date > current_date:
            break
    session.commit()


# Used in view_items
# Atomic transaction subtracting the appropriate quantity from the "posts" table and adding it to the
# "reservations" table. Also labels posts as inactive if their quantity reaches 0. Returns True for successful, False
# for failure.
def make_reservation(viewed_posts, rsvp_quantity):
    try:
        for viewed_post, viewed_item in viewed_posts:
            if rsvp_quantity >= int(viewed_post.post_quantity):
                session.add(Reservation(viewed_post.post_id, request.form['name'], viewed_post.post_quantity))
                rsvp_quantity = rsvp_quantity - int(viewed_post.post_quantity)
                viewed_post.post_quantity = 0
                viewed_post.active = False
            else:
                viewed_post.post_quantity = viewed_post.post_quantity - rsvp_quantity
                session.add(Reservation(viewed_post.post_id, request.form['name'], rsvp_quantity))
                rsvp_quantity = 0
            if rsvp_quantity == 0:
                break
        session.commit()
        return True
    except sqlite3.Error():
        return False


# A browse page with a meal_id of 0 shows all posted items. Any number above that displays only ingredients for the
# meal with that meal_id.
@browse.route('/<int:meal_id>/<int:store_id>', methods=['GET', 'POST'])
def browse_posts(meal_id, store_id):
    clear_old_posts()
    if meal_id == 0 and store_id == 0:
        posts = get_all_posts()
    elif store_id == 0:
        posts = filter_by_meal(meal_id)
    elif meal_id == 0:
        posts = filter_by_store(store_id)
    else:
        posts = filter_by_both(store_id, meal_id)

    stores = session.query(Store).all()  # for store filter

    if request.method == 'POST':
        chosen_store = session.query(Store).filter_by(store_id=request.form['store_filter']).first()
        if chosen_store is None:
            return redirect(url_for('browse.browse_posts', meal_id=meal_id, store_id=0))
        else:
            return redirect(url_for('browse.browse_posts', meal_id=meal_id, store_id=chosen_store.store_id))
    return render_template('browse.html', posts=posts, store_id=store_id, meal_id=meal_id, stores=stores)


# Allows users to view/reserve items posted at a given price point.
@browse.route('/<int:meal_id>/<int:store_id>/<int:post_id>', methods=('GET', 'POST'))
def view_item(meal_id, store_id, post_id):
    post = session.query(UserPost).filter_by(post_id=post_id).first()
    item = session.query(Item).filter_by(item_id=post.item_id).first()
    viewed_store_id = item.store_id
    viewed_posts = get_viewed_posts(post)
    max_quantity = int(calc_quantity(viewed_posts))

    # Reservation request
    if request.method == 'POST':
        rsvp_quantity = int(request.form['quantity'])
        if rsvp_quantity > max_quantity or rsvp_quantity < 1:
            flash(f"The quantity requested exceeds the amount available. You may only reserve {max_quantity} at this "
                  f"time.")
            return render_template('view-item.html', post=post, item=item, meal_id=meal_id, max=max_quantity)
        if make_reservation(viewed_posts, rsvp_quantity):
            return redirect(url_for('rsvp_conf', store_id=viewed_store_id))
        else:
            flash("An error occurred while placing your reservation. Please try again.")

    return render_template('view-item.html', post=post, item=item, meal_id=meal_id, max=max_quantity, store_id=store_id)
