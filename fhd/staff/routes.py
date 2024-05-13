from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, check_auth
from fhd.local_manager.routes import get_user_full_name
from fhd.utilities import flash_form_errors, check_auth, add_new_product_type, get_product_type_by_name, get_user_full_name
from fhd.utilities import get_product_category, get_all_product_type, get_product_type_by_id, update_product_type
from fhd.utilities import delete_product_type_by_id
from fhd.staff.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm

staff = Blueprint("staff", __name__, template_folder="templates")

# region functions


def check_is_staff():
    return check_auth(3)

# endregion

# region routes


@staff.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)
    return render_template("staff_dashboard.html", name=name)



@staff.route("/staff_add_product_type", methods=["GET", "POST"])
def staff_add_product_type():
    # Check authentication and authorisation
    auth_response = check_is_staff()
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
            return render_template("staff_add_product_type.html", form=form)

        add_new_product_type(image_data, product_name, product_unit, product_description, product_category)
        flash("Product type created successfully", "success")
        return staff_search_product_type()
    
    flash_form_errors(form)
    return render_template("staff_add_product_type.html", form=form)

@staff.route("/staff_search_product_type", methods=["GET","POST"])
def staff_search_product_type():
    # Check authentication and authorisation
    auth_response = check_is_staff()
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
    return render_template("staff_product_type_list.html", form=form, products=products, page=page_num, total_pages=total_pages, categories=categories, product_name=product_name, product_category=product_category)



@staff.route("/staff_edit_product_type/<product_type_id>", methods=["GET", "POST"])
def staff_edit_product_type(product_type_id):
    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
 
    form = EditProductTypeForm()
    product = get_product_type_by_id(product_type_id)
    if not product:
        flash('Product Type not found!', 'danger')
        return redirect(url_for('staff.search_product_type'))
 
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
            return render_template("staff_edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])
 
        else:
            # Update product type in db with the product picture
            update_product_type(product_type_id,image_data, product_name, product_unit, product_description, product_category)
 
        # Return to the product type page after the successful update
        flash("Information updated successfully.", "success")
        return staff_search_product_type()

    form.product_name.data = product[1]
    form.product_unit.data = str(product[4])
    form.product_description.data = product[3]
    form.product_category.data = str(product[5])
 
    flash_form_errors(form)
    return render_template("staff_edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])

@staff.route("/staff_delete_product_type/<product_type_id>", methods=["GET", "POST"])
def staff_delete_product_type(product_type_id):

    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    delete_product_type_by_id(product_type_id)
 
    # Return to the product type page after the successful update
    flash("Product Type deleted successfully.", "success")
    return staff_search_product_type()
# endregion
