from item_catalog_crud import read_category_items
from item_catalog_crud import read_category_item
from item_catalog_crud import read_categories
from flask import jsonify
import json


# ------------------------------------------------------------------
#                       Catalog JSON APIs
# ------------------------------------------------------------------

def show_catalog_items():
    items = read_category_items()
    return jsonify(CatalogItems=[i.serialize for i in items])


def show_catalog_categories():
    categories = read_categories()
    return jsonify(Catalories=[i.serialize for i in categories])


def show_select_item(category_item_id):
    item = read_category_item(category_item_id)
    return jsonify(Catalog_Item=item.serialize)
