# Flask
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import session as login_session
from flask import make_response

# Sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, CatalogItem, Category, User

# Oath2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import json
import requests
import random
import string
import httplib2

# Functools
from functools import wraps

from item_catalog_crud import read_catalog
from item_catalog_crud import read_category_items
from item_catalog_crud import read_category_item_info
from item_catalog_crud import read_category_item
from item_catalog_login import login
from item_catalog_login import google_connect
from item_catalog_crud import create
from item_catalog_crud import get_user_id
from item_catalog_crud import create_user
from item_catalog_crud import read_category
from item_catalog_crud import read_category_item_info
from item_catalog_crud import delete_category
from item_catalog_crud import delete_category_item

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    print("Showing Logging")
    return login()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)

    return decorated_function


# CONNECT - Google login get token
@app.route('/gconnect', methods=['POST'])
def gconnect():
    return google_connect(CLIENT_ID)


# CRUD
# Read - home page
@app.route('/')
@app.route('/categories')
def showCatalog():
    print("Showing The Catalog")
    categories, items, quantity = read_catalog()
    if 'username' not in login_session:
        return render_template('public_catalog.html', categories=categories, items=items, quantity=quantity)
    else:
        return render_template('catalog.html', categories=categories, items=items, quantity=quantity)


# CREATE - New category
@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    print("Creating new category")
    if request.method == 'POST':
        print login_session
        if 'user_id' not in login_session and 'email' in login_session:
            login_session['user_id'] = get_user_id(login_session['email'])
        create(login_session)
        flash("New category created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_category.html')


# --------------------------------------
# CRUD for category items
# --------------------------------------
# READ - show category items
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategoryItems(category_id):
    """returns items in category"""
    creator, category, categories, items, quantity = read_category_items(category_id)
    return render_template('catalog_menu.html', categories=categories, category=category, items=items,
                           quantity=quantity, creator=creator)


# READ ITEM - selecting specific item show specific information about that item
@app.route('/categories/<int:category_id>/item/<int:catalog_item_id>/')
def showCatalogItem(category_id, catalog_item_id):
    """returns category item"""
    creator, category, item = read_category_item_info(category_id, catalog_item_id)
    return render_template('catalog_menu_item.html', category=category, item=item, creator=creator)


# DELETE a category
@app.route('/categories/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """Allows user to delete an existing category"""
    category_to_delete = read_category(category_id)
    if category_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        delete_category(category_id)
        flash('%s Successfully Deleted' % category_to_delete.name, 'success')
        return redirect(url_for('showCatalog', category_id=category_id))
    else:
        return render_template('delete_category.html', category=category_to_delete)


# DELETE ITEM
@app.route('/categories/<int:category_id>/item/<int:catalog_item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(catalog_item_id):
    """return "This page will be for deleting a catalog item" """
    item_to_delete = read_category_item(catalog_item_id)
    if item_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        delete_category_item(catalog_item_id)
        flash('Catalog Item Successfully Deleted', 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'delete_catalog_item.html', item=item_to_delete)


# EDIT a category
@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """Allows user to edit an existing category"""
    print("Editing Category")
    edit_category = read_category(category_id)
    if edit_category.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            edit_category.name = request.form['name']
            flash('Category Successfully Edited %s' % edit_category.name, 'success')
            return redirect(url_for('showCatalog'))
    else:
        return render_template('edit_category.html', category=edit_category)


# UPDATE ITEM
@app.route('/categories/<int:category_id>/item/<int:catalog_item_id>/edit', methods=['GET', 'POST'])
@login_required
def editCatalogItem(category_id, catalog_item_id):
    """return "This page will be for making a updating catalog item" """
    editedItem = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized!')}</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash("Catalog item updated!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template('edit_catalog_item.html',categories=categories,item=editedItem)


@app.route('/categories/item/new', methods=['GET', 'POST'])
@login_required
def newCatalogItem():
    print("Creating new Cate")
    """return "This page will be for making a new catalog item" """
    categories = session.query(Category).all()
    if request.method == 'POST':
        addNewItem = CatalogItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(addNewItem)
        session.commit()
        flash("New catalog item created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_catalog_item.html', categories=categories)


@app.route('/gdisconnect')
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        # token given is invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# disconnect FB login
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # noqa
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print login_session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", 'danger')
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
