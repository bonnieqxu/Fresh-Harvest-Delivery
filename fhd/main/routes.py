
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, get_all_products, get_full_product_info_by_id, get_product_category, get_box_size
from fhd.utilities import query_depot_names, get_box_contents_by_product_id



main = Blueprint("main", __name__, template_folder="templates")


# region functions
def get_category_id_by_name(category_name, categories):
    # This function returns the category ID corresponding to the given category name.
    # It iterates through a list of categories, which are tuples containing category IDs and names.
    # If the category name matches the provided name, it returns the corresponding category ID.
    # If no match is found, it returns None.
    for category_id, name in categories:
        if name == category_name:
            return category_id
    return None  # Return None or appropriate value if not found

# endregion



# region routes
@main.route("/")
@main.route("/home")
@main.route("/index")
@main.route("/default")
def home():
    # This function handles requests to the root URL ("/") and several other routes ("/home", "/index", "/default").
    # It retrieves a list of depot names by calling the query_depot_names function.
    # It then renders the "home.html" template, passing the depot names and a flag (is_home=True) to indicate that this is the home page.
    
    depot_names = query_depot_names()
    return render_template("home.html", is_home=True, depot_names=depot_names)




@main.route("/view_products/<depot_name>/")
@main.route("/view_products/<depot_name>/", defaults={'category_name': 'All', 'size': None})
@main.route("/view_products/<depot_name>/<category_name>/", defaults={'size': None})
@main.route("/view_products/<depot_name>/<category_name>/<size>/")
def view_products(depot_name, category_name='All', size=None):
    # This function handles requests to view products in a specified depot, with optional category and size filters.
    # It supports multiple route patterns with default values for category_name and size.

    if depot_name == None:
        # If no depot name is provided, flash a message to the user and redirect to the home page.
        flash("You have to choose a depot!", "danger")
        return redirect(url_for('main.home'))

    # Get the page number from the query string
    page_num = request.args.get('page', 1, type=int)
    item_num_per_page = 8

    # Replace '-' back to ''
    category_name = str(category_name).replace('-', ' ')

    # Get product categories and category_id
    categories = get_product_category()
    category_id = get_category_id_by_name(category_name, categories)

    # Retrieve box sizes only when the box category is the current category
    box_sizes = get_box_size() if category_name == "Premade Box" else None

    # Get all product infos
    products, total = get_all_products(page_num, item_num_per_page, depot_name, category_id, size, category_name)

    # Calculate total pages
    total_pages = (total + item_num_per_page - 1) // item_num_per_page

    # Render the "view_products.html" template with the retrieved data.
    return render_template("view_products.html", products=products, page=page_num, total_pages=total_pages, 
                           categories=categories, current_category=category_name, box_sizes=box_sizes, current_size=size, depot_name=depot_name)



@main.route("/view_product/<product_id>", methods=['GET'])
def view_product(product_id):
    # This function handles GET requests to view a specific product by its product ID.

    # Get the specific product from db
    product = get_full_product_info_by_id(product_id)
    
    # Check if the product is a Premade Box
    box_contents = None

    # Check if the product is categorized as a "Premade Box".
    # If it is, retrieve the contents of the box.
    if product[7] == 'Premade Box':
        box_contents = get_box_contents_by_product_id(product_id)
    
    return render_template("view_a_product.html", product=product, product_id=product_id, box_contents=box_contents)



# endregion

