# Flask
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import session as login_session

# Functools
from functools import wraps

from item_catalog_crud import *
from item_catalog_login import *
from item_catalog_apis import *

app = Flask(__name__)

# ------------------------------------------------------------------
#                       Database Connection
# ------------------------------------------------------------------
# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# ------------------------------------------------------------------
#                       App Configuration
# ------------------------------------------------------------------
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# ------------------------------------------------------------------
#                       Login and Logout Routes
# ------------------------------------------------------------------

@app.route('/login')
def showLogin():
    print("Showing Logging")
    return login()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Google login
    :return: login session output
    """
    return google_connect(CLIENT_ID)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Login decorator
        """
        if 'user_id' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/disconnect')
def disconnect():
    return logout(CLIENT_ID)


# ------------------------------------------------------------------
#                       User Create Routes
# ------------------------------------------------------------------
# CREATE - New category
@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def newCategory():
    """
    Create a new category
    :return:
    """
    print("Creating a new category")
    if request.method == 'POST':
        print login_session
        if 'user_id' not in login_session and 'email' in login_session:
            login_session['user_id'] = get_user_id(login_session['email'])
        create_category(login_session)
        flash("New category created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_category.html')


@app.route('/categories/item/new', methods=['GET', 'POST'])
@login_required
def newCatalogItem():
    """
    Create a new Catalog Item
    :return:
    """
    print("Creating new Category Item")
    print login_session
    """return "This page will be for making a new catalog item" """
    categories = session.query(Category).all()
    if request.method == 'POST':
        create_category_item(login_session)
        flash("New catalog item created!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('new_catalog_item.html', categories=categories)


# ------------------------------------------------------------------
#                       Read Routes
# ------------------------------------------------------------------
@app.route('/')
@app.route('/categories')
def showCatalog():
    """
    Showing the catalog
    :return:
    """
    print("Showing The Catalog")
    categories, items, quantity = read_catalog()
    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               categories=categories,
                               items=items,
                               quantity=quantity)
    else:
        return render_template('catalog.html',
                               categories=categories,
                               items=items,
                               quantity=quantity)


@app.route('/categories/'
           '<int:category_id>/item/<int:catalog_item_id>/')
def showCatalogItem(category_id, catalog_item_id):
    """
    Showing Category Item
    :return category item
    """
    creator, category, item = \
        read_category_item_info(category_id, catalog_item_id)
    return render_template('catalog_menu_item.html',
                           category=category,
                           item=item,
                           creator=creator)


@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategoryItems(category_id):
    """
    Showing Category Items
    :return: items in category
    """
    creator, category, categories, items, quantity = \
        read_category_items_info(category_id)
    return render_template('catalog_menu.html',
                           categories=categories,
                           category=category,
                           items=items,
                           quantity=quantity,
                           creator=creator)


# ------------------------------------------------------------------
#                       User Delete Routes
# ------------------------------------------------------------------

@app.route('/categories/'
           '<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """
    Allows a user to delete an existing category
    """
    category_to_delete = read_category(category_id)
    if category_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized!')}" \
               "</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        delete_category(category_id)
        flash('%s Successfully Deleted' % category_to_delete.name, 'success')
        return redirect(url_for('showCatalog',
                                category_id=category_id))
    else:
        return render_template('delete_category.html',
                               category=category_to_delete)


@app.route('/categories/<int:category_id>/'
           'item/<int:catalog_item_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteCatalogItem(category_id, catalog_item_id):
    """
    Allows a user to delete a category item
    """
    item_to_delete = read_category_item(catalog_item_id)
    if item_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized!')}" \
               "</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        delete_category_item(catalog_item_id)
        flash('Catalog Item Successfully Deleted', 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'delete_catalog_item.html', item=item_to_delete)


# ------------------------------------------------------------------
#                       User Edit Routes
# ------------------------------------------------------------------

@app.route('/categories/'
           '<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """
    Allows a user to edit an existing category
    """
    print("Editing Category")
    edit_category = read_category(category_id)
    if edit_category.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized!')}" \
               "</script><body onload='myFunction()'>"  # noqa
    if request.method == 'POST':
        if request.form['name']:
            edit_category.name = request.form['name']
            flash('Category Successfully Edited %s'
                  % edit_category.name, 'success')
            return redirect(url_for('showCatalog'))
    else:
        return render_template('edit_category.html',
                               category=edit_category)


@app.route('/categories/<int:category_id>'
           '/item/<int:catalog_item_id>/edit', methods=['GET', 'POST'])
@login_required
def editCatalogItem(category_id, catalog_item_id):
    """
    Allows a user to edit category item
    """
    edited_item = read_category_item(catalog_item_id)
    if edited_item.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('You are not authorized!')}</script>" \
               "<body onload='myFunction()'>"
    if request.method == 'POST':
        update_category_item(catalog_item_id)
        flash("Catalog item updated!", 'success')
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).all()
        return render_template('edit_catalog_item.html',
                               categories=categories, item=edited_item)


# ------------------------------------------------------------------
#                       Catalog JSON APIs
# ------------------------------------------------------------------
@app.route('/api/v1/categories/JSON')
def showCategoriesJSON():
    """
    Show Catalog Categories as JSON
    :return: Categories JSON
    """
    return show_catalog_categories()


@app.route('/api/v1/items/JSON')
def showItemsJSON():
    """
    Show Catalog Items as JSON
    :return: Items JSON
    """
    return show_catalog_items()


@app.route('/api/v1/categories/'
           '<int:category_id>/item/<int:catalog_item_id>/JSON')
def showCatalogItemJSON(category_id, catalog_item_id):
    """
    Show Catalog Item
    :return:  Item JSON
    """
    return show_select_item(catalog_item_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
