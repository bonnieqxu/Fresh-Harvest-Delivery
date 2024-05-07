from flask import Blueprint, render_template, request
from fhd.utilities import flash_form_errors, get_all_products, get_full_product_info_by_id
from fhd.dbconnection import query_depot_names


main = Blueprint("main", __name__, template_folder="templates")


# region functions
# endregion

# region routes
@main.route("/")
@main.route("/home")
@main.route("/index")
@main.route("/default")
def home():
    depot_names = query_depot_names()
    return render_template("home.html", is_home=True, depot_names=depot_names)

@main.route("/view_products", methods = ['GET'])
def view_products():
    # Get the page number from the query string
    page_num = request.args.get('page', 1, type=int)
    item_num_per_page = 8

    # Get all product infos from db
    products, total = get_all_products(page_num, item_num_per_page)

    # Calculate total pages
    total_pages = (total + item_num_per_page - 1) // item_num_per_page
    return render_template("view_products.html", products=products, page=page_num, total_pages=total_pages)


@main.route("/view_product/<product_id>", methods=['GET'])
def view_product(product_id):
    # Get the specific product from db
    product = get_full_product_info_by_id(product_id)
    return render_template("view_a_product.html", product=product)
# endregion
