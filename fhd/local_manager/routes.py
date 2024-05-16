from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, check_auth, add_new_product_type, get_product_type_by_name, get_user_full_name
from fhd.utilities import get_product_category, get_all_product_type, get_product_type_by_id, update_product_type
from fhd.utilities import delete_product_type_by_id, delete_message_by_id, get_all_messages_by_user_id
from fhd.local_manager.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm

local_manager = Blueprint("local_manager", __name__, template_folder="templates")

# region functions
def check_is_local_manager():
    return check_auth(4)


def get_category_id_by_name(category_name, categories):
    for category_id, name in categories:
        if name == category_name:
            return category_id
    return None  # Return None or appropriate value if not found



# endregion

# region routes

@local_manager.route("/add_product_type", methods=["GET", "POST"])
def add_product_type():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = AddProductTypeForm()

    if form.validate_on_submit():
        images = request.files.getlist('product_image')
        #if len(images) == 0 or (len(images) == 1 and images[0].filename == ''):
        #    flash("Product type image is required!", "danger")
        #    return render_template("add_product_type.html", form=form)
        
        image_data = images[0].read()
        product_name = form.product_name.data
        product_unit = form.product_unit.data
        product_description = form.product_description.data
        product_category = form.product_category.data

        if get_product_type_by_name(product_name):
            flash("Product type name already exist", "danger")
            return render_template("add_product_type.html", form=form)

        add_new_product_type(image_data, product_name, product_unit, product_description, product_category)
        flash("Product type created successfully", "success")
        return search_product_type()
    
    flash_form_errors(form)
    return render_template("add_product_type.html", form=form)

@local_manager.route("/search_product_type", methods=["GET","POST"])
def search_product_type():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = SearchProductTypeForm()
    
    # Initialize variables
    product_name = None
    product_category = None
    page_num = request.args.get('page', 1, type=int)

    if request.method == 'POST' and form.validate_on_submit():
        product_name = form.product_name.data
        product_category = form.product_category.data

    if request.method == 'GET':
        product_name = request.args.get('product_name')
        if product_name == '':
            product_name = None  # Set to None if empty string

        product_category = request.args.get('product_category')
        if product_category == '':
            product_category = None  # Set to None if empty string

    item_num_per_page = 20

    # Get product categories
    categories = get_product_category()

    # Get all product infos from db
    products, total = get_all_product_type(page_num, item_num_per_page, product_category, product_name)

    # Calculate total pages
    total_pages = (total + item_num_per_page - 1) // item_num_per_page
    return render_template("product_type_list.html", form=form, products=products, page=page_num, total_pages=total_pages, categories=categories, product_name=product_name, product_category=product_category)



@local_manager.route("/edit_product_type/<product_type_id>", methods=["GET", "POST"])
def edit_product_type(product_type_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
 
    form = EditProductTypeForm()
    product = get_product_type_by_id(product_type_id)
    if not product:
        flash('Product Type not found!', 'danger')
        return redirect(url_for('local_manager.search_product_type'))
 
    # When user clicks on submit button
    if form.validate_on_submit():

        images = request.files.getlist('product_image')
        #if len(images) == 0 or (len(images) == 1 and images[0].filename == ''):
        #    flash("Product type image is required!", "danger")
        #    return render_template("add_product_type.html", form=form)
        
        image_data = images[0].read()
        product_name = form.product_name.data
        product_unit = form.product_unit.data
        product_description = form.product_description.data
        product_category = form.product_category.data

        # No image is uploaded
        if len(images) == 0 or (len(images) == 1 and images[0].filename == ''):
            # Update product_type in db with no product picture
            update_product_type(product_type_id,None, product_name, product_unit, product_description, product_category)
 
        # More than 1 images are uploaded
        elif len(images) > 1:
            flash("Only 1 profile image is allowed!", "danger")
            return render_template("edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])
 
        else:
            # Update product type in db with the product picture
            update_product_type(product_type_id,image_data, product_name, product_unit, product_description, product_category)
 
        # Return to the product type page after the successful update
        flash("Information updated successfully.", "success")
        return search_product_type()

    form.product_name.data = product[1]
    form.product_unit.data = str(product[4])
    form.product_description.data = product[3]
    form.product_category.data = str(product[5])
 
    flash_form_errors(form)
    return render_template("edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])

@local_manager.route("/delete_product_type/<product_type_id>", methods=["GET", "POST"])
def delete_product_type(product_type_id):

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    delete_product_type_by_id(product_type_id)
 
    # Return to the product type page after the successful update
    flash("Product Type deleted successfully.", "success")
    return search_product_type()

@local_manager.route("/dashboard")
def dashboard():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)
    return render_template("local_manager_dashboard.html", name=name)

@local_manager.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('account_holder_messages_list.html', messages=messages)

@local_manager.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")
    return render_template('account_holder_messages_list.html', messages=messages)