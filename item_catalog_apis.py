from item_catalog_crud import read_category_items
from item_catalog_crud import read_category_item
from item_catalog_crud import read_categories
from flask import jsonify


# ------------------------------------------------------------------
#                       Catalog JSON APIs
# ------------------------------------------------------------------

def show_catalog_items():
    """
    Show the catalog items
    :return: items JSON
    """
    items = read_category_items()
    return jsonify(CatalogItems=[i.serialize for i in items])


def show_catalog_categories():
    """
    Show the catalog categories
    :return: categories Json
    """
    categories = read_categories()
    return jsonify(Catalories=[i.serialize for i in categories])


def show_select_item(category_item_id):
    """
    Show a select item from the catalog
    :param category_item_id: id of the item
    :return: item JSON
    """
    item = read_category_item(category_item_id)
    return jsonify(Catalog_Item=item.serialize)
