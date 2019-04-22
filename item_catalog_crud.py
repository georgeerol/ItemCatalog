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

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_category(login_session):
    """
    Create new category
    :param login_session:
    """
    new_category = Category(name=request.form['name'], user_id=login_session['user_id'])
    session.add(new_category)
    session.commit()


def create_category_item(login_session):
    add_new_item = CatalogItem(
        name=request.form['name'],
        description=request.form['description'],
        price=request.form['price'],
        category_id=request.form['category'],
        user_id=login_session['user_id'])
    session.add(add_new_item)
    session.commit()


def read_catalog():
    """
    Read the Catalog page with all categories.
    Public catalog if no user is sign in.
    Private Catalog if a user is sigg in.
    :return:
    """
    categories = session.query(Category).all()
    items = session.query(CatalogItem).order_by(CatalogItem.id.desc())
    quantity = items.count()
    return categories, items, quantity


def read_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return category


def read_category_item(category_item_id):
    item = session.query(CatalogItem).filter_by(id=category_item_id).one()
    return item


def read_categories():
    categories = session.query(Category).all()
    return categories


def read_category_items():
    items = session.query(CatalogItem).order_by(CatalogItem.id.desc())
    return items


def read_category_items_info(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).all()
    creator = get_user_id(category.user_id)
    items = session.query(CatalogItem).filter_by(category_id=category_id).order_by(CatalogItem.id.desc())
    quantity = items.count()
    return creator, category, categories, items, quantity


def read_category_item_info(category_id, catalog_item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(
        CatalogItem).filter_by(id=catalog_item_id).one()
    creator = get_user_id(category.user_id)
    return creator, category, item


def update_category_item(catalog_item_id):
    edited_item = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    if request.form['name']:
        edited_item.name = request.form['name']
    if request.form['description']:
        edited_item.description = request.form['description']
    if request.form['price']:
        edited_item.price = request.form['price']
    session.add(edited_item)
    session.commit()


def delete_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()


def delete_category_item(category_item_id):
    item = session.query(CatalogItem).filter_by(id=category_item_id).one()
    session.delete(item)
    session.commit()


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def create_user(login_session):
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
