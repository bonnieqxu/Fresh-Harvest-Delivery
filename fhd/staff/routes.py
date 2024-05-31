from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, check_auth
from fhd.local_manager.routes import get_user_full_name
from fhd.utilities import flash_form_errors, check_auth, add_new_product_type, get_product_type_by_name, get_user_full_name
from fhd.utilities import get_product_category, get_all_product_type, get_product_type_by_id, update_product_type, get_products_by_user_depot, edit_product, update_product, check_low_stock_product_by_depot
from fhd.utilities import delete_product_type_by_id, get_all_messages_by_user_id, delete_message_by_id
from fhd.utilities import get_all_orders, update_order_status_by_depot_orderid, get_status_choices, get_current_user_depot_id
from fhd.utilities import get_order_details, get_customer_info, send_message, get_order_hdr_and_user_id
from fhd.staff.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm, ViewProductForm, UpdateOrderStatusForm, EditProductForm
from markupsafe import Markup


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
    
    # Retrieve depot_id from the session
    depot_id = session.get('user_depot')
    
    # Check for low stock products and set a flash message if any
    if check_low_stock_product_by_depot(depot_id):
        flash(Markup('Warning: Some products are low in stock! <a href="' + url_for('staff.staff_product_list', depot_id=session['user_depot']) + '">Click here to check product inventory</a>'), 'danger')
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)
    return render_template("staff_dashboard.html", name=name, depot_id=depot_id)



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

@staff.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('staff_messages_list.html', messages=messages)

@staff.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")
    return render_template('staff_messages_list.html', messages=messages)

@staff.route('/staff_product_list/<int:depot_id>', methods=["GET", "POST"])
def staff_product_list(depot_id):
    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = ViewProductForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Define the number of items per page
    status_filter = request.args.get('status', '')

    products, total_products = get_products_by_user_depot(depot_id, page, per_page, status_filter)
    
    return render_template('staff_product_list.html', form=form, products=products, depot_id=depot_id, page=page, per_page=per_page, total_products=total_products)

@staff.route('/update_order_status/<int:depot_orderid>', methods=['POST'])
def update_order_status(depot_orderid):
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
    
    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_orderid, status_id)
        order_hdr_id, user_id = get_order_hdr_and_user_id(depot_orderid)

        if status_id == "3" or status_id == 3: #when the order is shipped
            send_message(11, user_id, "Great news! Your order #{} has been successfully shipped and is now on its way to you. Get ready to receive your items soon! Should you have any questions or need further assistance, feel free to reach out. We're here to help. Happy shopping!".format(order_hdr_id), 1)
    
        flash(f"Order {order_hdr_id} status updated successfully.", "success")
        return redirect(url_for('staff.update_order_statuses'))

    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)
    return render_template('staff_update_order_status.html', orders=orders, form=form)



@staff.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)
    return render_template('staff_update_order_status.html', orders=orders, form=form)



@staff.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_order_id, status_id)
        flash(f"Order {depot_order_id} status updated successfully.", "success")
        return redirect(url_for('staff.view_order_details', order_hdr_id=order_hdr_id, depot_order_id=depot_order_id))

    order_details = get_order_details(order_hdr_id)
    customer_info = get_customer_info(order_hdr_id)
    return render_template('staff_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)





@staff.route("/staff_edit_product/<int:product_id>", methods=["GET", "POST"])
def staff_edit_product(product_id):
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = EditProductForm()
    product = edit_product(product_id)

    if request.method == 'POST' and form.validate_on_submit():
        # Update product details based on form data
        new_price = form.product_price.data
        new_quantity = form.product_quantity.data
        # Update other fields as needed

        # Perform database update using the new function
        update_product(product_id, new_price, new_quantity)

        flash('Product updated successfully!', 'success')
        return redirect(url_for('staff.staff_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('staff_edit_product.html', form=form, product=product, product_id=product_id)


