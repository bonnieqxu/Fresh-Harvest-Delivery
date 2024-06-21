from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from fhd.utilities import flash_form_errors, check_auth, delete_message_by_id, get_product_category
from fhd.utilities import get_user_full_name, get_product_weight, get_all_messages_by_user_id, get_all_product_type
from fhd.utilities import add_product_weight_by_id, delete_product_weight_by_id, get_product_type_by_id
from fhd.utilities import update_product_weight, unit_exists_check, update_product_type, get_product_type_by_name
from fhd.utilities import get_all_category_List, category_exists_check, delete_product_type_by_id, add_new_product_type
from fhd.utilities import insert_product_category, get_product_category_by_id, update_product_category, delete_product_category
from fhd.utilities import get_all_shipping_option_list, insert_shipping_option, get_shipping_option_name_by_id, update_shipping_option
from fhd.utilities import delete_shipping_option_by_id, get_all_depots, get_products_by_depot_and_status
from fhd.utilities import get_all_pending_requests, get_request_details, get_user_id_from_account_holder,reject_request, send_message
from fhd.utilities import get_credit_limit, update_account_holder, update_user_role, get_status_choices, update_order_status_by_depot_orderid
from fhd.utilities import get_order_hdr_and_user_id, get_all_orders, get_current_user_depot_id, get_order_details, get_customer_info
from fhd.utilities import get_filtered_orders, update_credit_limit_after_processing_request, get_all_account_holders, get_account_holders_by_depot
from fhd.utilities import get_all_staff_members, get_staff_by_id, get_all_roles, update_staff, get_staff_by_depot
from fhd.utilities import delete_staff_member, add_new_staff, update_credit_limit, update_message_by_id, get_message_by_id
from fhd.national_manager.forms import AddProductWeightForm, EditProductWeightForm, AddCategoryForm, EditCategoryForm, AddShippingOptionForm
from fhd.national_manager.forms import EditShippingOptionForm, UpdateOrderStatusForm, SearchProductTypeForm
from fhd.utilities import insert_product_category, get_product_category_by_id, update_product_category, delete_product_category, update_product, edit_product, check_low_stock_product_by_all
from fhd.national_manager.forms import ViewProductForm, EditProductForm, EditProductTypeForm, AddProductTypeForm, ReplyMessageForm
from fhd.utilities import get_credit_limit_increase_requests, get_credit_limit_increase_request_info, get_user_id_from_credit_limit_request
from fhd.utilities import approve_credit_limit_request, get_credit_account_id, reject_credit_limit_request, user_exists_with_email
from fhd.utilities import get_depot_name_by_id, get_all_active_subscription_display, get_gst_rate, get_all_active_subscription, get_full_product_info_by_id
from fhd.utilities import get_products_by_depot_status_search
from fhd.local_manager.routes import create_box_func, add_box_content_func, add_to_box_func, review_box_func, confirm_box_func, review_box_func
from fhd.local_manager.routes import delete_box_item_func, clear_box_func, view_boxes_func, view_box_func, delete_box_func, delete_box_detail_func
from fhd.local_manager.routes import add_to_existing_box_func, generate_invoice, is_order_due, create_order
from markupsafe import Markup
import re, datetime
from fhd import my_hashing
from datetime import datetime
from fhd.utilities import get_customer_shipping_fee, insert_payment, update_subscription_quantity

national_manager = Blueprint("national_manager", __name__, template_folder="templates")

# region functions

def check_is_national_manager():
    # This function checks if the current user has the role of a national manager
    return check_auth(5)

# endregion


# region routes


# Displays the dashboard for the national manager.
@national_manager.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    # Check for low stock products and set a flash message if any
    low_stock_depots = check_low_stock_product_by_all()
    if low_stock_depots:
        if len(low_stock_depots) == 1:
            depots_str = low_stock_depots[0]
        else:
            depots_str = ', '.join(low_stock_depots[:-1]) + ' and ' + low_stock_depots[-1]
        
        # Construct the message with Markup
        flash(Markup(
            f'Warning: Products are low in stock or unavailable at the following depots: {depots_str}. '
            f'<a href="{url_for("national_manager.national_manager_product_list")}">Click here to check product inventory</a>'
        ), 'danger')
        
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)
    return render_template("national_manager_dashboard.html", name=name)




@national_manager.route("/add_product_weight", methods=["GET", "POST"])
def add_product_weight():
    # This route validates the form data submitted for adding product weight, and adds the new product weight to the database.

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddProductWeightForm()

    if form.validate_on_submit():
        # Extract data from the form
        weight_str = form.weight.data

    # Check if the weight is a positive number or zero
        if weight_str:
            try:
                weight = float(weight_str)

                if weight == 0:
                    weight = None

    # If the weight is not a number, display an error message
            except ValueError:
                flash("Weight must be a positive number or zero.", "danger")
                return render_template('national_manager_add_product_weight.html', form=form)

        else:
            weight = None
        
        unit = form.unit.data

        # Check if the new unit already exists
        unit_exists = unit_exists_check(weight, unit)


        # If the unit already exists, display an error message
        if unit_exists:
            flash("Product Unit already exists", "danger")

            return render_template('national_manager_add_product_weight.html', form=form)

        # Add new product weight to the database
        add_product_weight_by_id(weight, unit)

        flash("New product unit added successfully.", "success")

        return redirect(url_for('national_manager.view_product_weight'))

    return render_template('national_manager_add_product_weight.html', form=form)



@national_manager.route("/view_product_weight", methods=["GET", "POST"])
def view_product_weight():
    # Displays the product weights for the national manager.

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    product_weight = get_product_weight()

    return render_template("national_manager_view_product_weight.html", product_weight=product_weight)



@national_manager.route("/delete_product_weight/<int:product_weight_id>", methods=["GET", "POST"])
def delete_product_weight(product_weight_id):
    # This route deletes the specified product weight from the database and displays a flash message upon success.
    
    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    delete_product_weight_by_id (product_weight_id)

    # Return to the product unit page after the successful update
    flash("Product Unit deleted successfully.", "success")

    return view_product_weight()



@national_manager.route('/edit_product_weight/<int:product_weight_id>', methods=["GET", "POST"])
def edit_product_weight(product_weight_id):
    #  Allows national managers to edit product weight.
    # Handles form submission for editing product weight, updates data in the database, and redirects to view_product_weight upon success.

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = EditProductWeightForm()

    product_weight = get_product_weight(product_weight_id)

    # When user clicks on submit button
    if form.validate_on_submit():
        weight_str = form.weight.data

        if weight_str:
            try:
                weight = float(weight_str)
                if weight == 0:
                    weight = None

            except ValueError:
                flash("Weight must be a positive number or zero.", "danger")
                return render_template('national_manager_edit_product_weight.html', form=form, product_weight_id=product_weight_id)
       
        else:
            weight = None
        
        unit = form.unit.data
        
        # Check if the new unit already exists
        unit_exists = unit_exists_check(weight, unit)
        
        if unit_exists:
            flash("Product Unit already exists", "danger")
            return render_template('national_manager_edit_product_weight.html', form=form, product_weight_id=product_weight_id)

        # Update product weight and unit in db
        update_product_weight(product_weight_id, weight, unit)

        flash("Information updated successfully.", "success")
        return redirect(url_for('national_manager.view_product_weight', product_weight_id=product_weight_id))

    # Prepopulate form with current product weight data
    if product_weight:
        form.weight.data = str(product_weight[0][1]) if product_weight[0][1] is not None else ''
        form.unit.data = product_weight[0][2]

    return render_template('national_manager_edit_product_weight.html', form=form, product_weight_id=product_weight_id)




@national_manager.route('/nm_getMessages')
def nm_getMessages():
    # Fetches all messages associated with the current user and renders them in the national_manager_messages_list.html template.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('national_manager_messages_list.html', messages=messages)




@national_manager.route('/nm_delete_message/<int:message_id>')
def nm_delete_message(message_id):   
    # Deletes the specified message from the database and displays a flash message upon successful deletion.
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")

    return render_template('national_manager_list.html', messages=messages)




@national_manager.route('/getCategoryList')
def getCategoryList():
    # Retrieves category list for national managers and renders them in the national_manager_category_list.html template.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    categories = get_all_category_List()
    
    return render_template('national_manager_category_list.html', categories=categories)




@national_manager.route('/add_category', methods=["GET", "POST"])
def add_category():
    # Handles form submission for adding a new category,
    # inserts the new category into the database, and displays a flash message upon success.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddCategoryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            category_name = form.categoryname.data
            status = form.status.data

            # Check if the category already exists
            category_exists = category_exists_check(category_name)

            if category_exists:
                flash("Product Category already exists", "danger")
                return render_template('national_manager_add_category.html',form=form)

            # Insert the new category into the database
            insert_product_category(category_name, status)

            flash("Product Category created successfully", "success")
            categories = get_all_category_List()
    
            return render_template('national_manager_category_list.html', categories=categories)

    return render_template('national_manager_add_category.html', form=form)




@national_manager.route('/edit_category/<int:category_id>', methods=["GET", "POST"])
def edit_category(category_id):
    # Handles form submission for editing a category,
    # updates the category in the database, and displays a flash message upon success.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = EditCategoryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            category_name = form.categoryname.data
            status = form.status.data

            # Update the category in the database
            update_product_category(category_id, category_name, status)

            flash("Product Category updated successfully", "success")
            categories = get_all_category_List()
    
            return render_template('national_manager_category_list.html', categories=categories)
    
    # Prepopulate the form with current category data
    category = get_product_category_by_id(category_id)
    form.categoryname.data = category[1]
    form.status.data = category[2]

    return render_template('national_manager_edit_category.html', form=form, category_id=category_id)




@national_manager.route('/delete_category/<int:category_id>', methods=["GET", "POST"])
def delete_category(category_id):
    # Deletes the specified category from the database and displays a flash message upon successful deletion.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    delete_product_category(category_id)

    flash("Product Category deleted successfully", "success")
    categories = get_all_category_List()

    return render_template('national_manager_category_list.html', categories=categories)




@national_manager.route('/national_manager_product_list', methods=["GET", "POST"])
def national_manager_product_list():
    # Displays a list of products for national managers.
    # Allows filtering by depot and status, and paginates the product list.

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = ViewProductForm()

    # Populate depot choices
    depots = get_all_depots()
    form.depot.choices = [(0, 'All Depots')] + [(int(d['id']), d['name']) for d in depots]

    selected_depot = None
    selected_status = 'All'
    search_query = '' 

    # Get selected depot and status
    if request.method == 'POST':
        selected_depot = int(request.form.get('depot'))
        selected_status = request.form.get('status')
        search_query = request.form.get('search')
    else:
        selected_depot = request.args.get('depot', 0, type=int)  # Get from query parameters if GET
        selected_status = request.args.get('status', 'All')  # Get status from query parameters if GET
        search_query = request.args.get('search', '')  # search product name 

    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    # Pagination
    products, total = get_products_by_depot_status_search(selected_depot, selected_status, search_query, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template('national_manager_product_list.html', form=form, products=products, depots=depots, selected_depot=selected_depot, selected_status=selected_status, page=page, total_pages=total_pages)




@national_manager.route('/getShippingOptionList')
def getShippingOptionList():
    # Fetches all shipping options and renders them in the national_manager_shipping_option_list.html template.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
      
    shipping_option = get_all_shipping_option_list()
    
    return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)




@national_manager.route('/addShippingOption', methods=["GET", "POST"])
def addShippingOption():
    # Handles form submission for adding a new shipping option,
    # inserts the new option into the database, and displays a flash message upon success.
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddShippingOptionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            shipping_option_name = form.shippingOption.data
            shipping_price = form.price.data

            # Check if the shipping option already exists
            shipping_option_exists = category_exists_check(shipping_option_name)

            if shipping_option_exists:
                flash("Shipping option already exists", "danger")
                return render_template('national_manager_add_shipping_option.html',form=form)

            insert_shipping_option(shipping_option_name, shipping_price)

            flash("Shipping option created successfully", "success")
            shipping_option = get_all_shipping_option_list()
    
            return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)

    return render_template('national_manager_add_shipping_option.html', form=form)




@national_manager.route('/edit_shipping_option/<int:shipping_option_id>', methods=["GET", "POST"])
def edit_shipping_option(shipping_option_id):
    # Handles form submission for editing a shipping option,
    # updates the option in the database, and displays a flash message upon success.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    form = EditShippingOptionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            shipping_option_name = form.shippingOption.data
            shipping_price = form.price.data

            # Update the shipping option in the database
            update_shipping_option(shipping_option_id, shipping_option_name, shipping_price)

            flash("Shipping option updated successfully", "success")
            shipping_option = get_all_shipping_option_list()
    
            return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)
        
    # Prepopulate form with current shipping option data
    shipping_option = get_shipping_option_name_by_id(shipping_option_id)
    form.shippingOption.data = shipping_option[1]
    form.price.data = shipping_option[2]

    return render_template('national_manager_edit_shipping_option.html', form=form, shipping_option_id=shipping_option_id)




@national_manager.route("/national_manager_edit_product/<int:product_id>", methods=["GET", "POST"])
def national_manager_edit_product(product_id): 
    # Handles form submission for editing a product,
    # updates the product details in the database, and displays a flash message upon success.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    form = EditProductForm()

    product = edit_product(product_id)

    if request.method == 'POST' and form.validate_on_submit():
        # Update product details based on form data
        new_price = form.product_price.data
        new_quantity = form.product_quantity.data

        # Check if the 'Discontinued' checkbox was checked
        is_discontinued = 'discontinued' in request.form

        # Perform database update using the new function
        update_product(product_id, new_price, new_quantity, is_discontinued)

        flash('Product updated successfully!', 'success')
        return redirect(url_for('national_manager.national_manager_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('national_manager_edit_product.html', form=form, product=product, product_id=product_id)




@national_manager.route('/delete_shipping_option/<int:shipping_option_id>', methods=["GET", "POST"])
def delete_shipping_option(shipping_option_id):   
    # Deletes the specified shipping option from the database
    # and displays a flash message upon successful deletion.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    delete_shipping_option_by_id(shipping_option_id)

    flash("Shipping Option deleted successfully", "success")
    shipping_option = get_all_shipping_option_list()

    return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)




@national_manager.route('/view_requests', methods=["GET"])
def view_requests():
    # Fetches all pending requests
    # and renders them in the national_manager_view_requests.html template.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Get all pending requests
    requests = get_all_pending_requests()

    return render_template('national_manager_view_requests.html',requests=requests)




@national_manager.route('/view_request_details/<int:request_id>', methods=['GET'])
def view_request_details(request_id):
    # Fetches details of the specified request
    # and renders them in the national_manager_view_request_details.html template.
    
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    request = get_request_details(request_id)
    
    # Check if request is found
    if request is None:
        flash("Request not found.", "danger")
        return redirect(url_for('national_manager.view_requests'))
    
    return render_template('national_manager_view_request_details.html', request=request)




@national_manager.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):
    # Processes the approval or rejection of a request,
    # updates the database accordingly, sends a message to the user, and redirects to the request view page.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    action = request.form['action']
    message_content = request.form['message']
    
    # get user_id from account_holder
    user_id = get_user_id_from_account_holder(request_id)
    
    if user_id is None:
        flash("Error fetching user ID.", "danger")
        return redirect(url_for('national_manager.view_request_details', request_id=request_id))
    
    # Approve or reject request
    if action == 'approve':
        credit_limit = request.form['credit_limit']
        
        # Validate that the credit limit is a positive number
        try:
            credit_limit = float(credit_limit)
            if credit_limit <= 0:
                raise ValueError("Credit limit must be a positive amount.")
            
        except ValueError as e:
            flash(f"Invalid credit limit: {str(e)}", "danger")
            return redirect(url_for('national_manager.view_request_details', request_id=request_id))
        
        # Get credit account ID
        credit_account_id = get_credit_limit(credit_limit)
        
        if credit_account_id is None:
            flash("Error creating credit account.", "danger")
            return redirect(url_for('national_manager.view_request_details', request_id=request_id))
        
        # Update account_holder with credit account ID
        update_account_holder(request_id, credit_account_id)
        
        # Update role ID to "Credit Account Holder" (role_id = 2)
        update_user_role(user_id, 2)
        
        # Get user name
        user_name = get_user_full_name(user_id)
        if user_name is None:
            flash("Error fetching user name.", "danger")
            return redirect(url_for('national_manager.view_request_details', request_id=request_id))
        
        flash(f"{user_name}'s account holder application has been approved.", "success")
    
    # Reject request
    elif action == 'reject':
        user_name = reject_request(request_id)
        
        if user_name is None:
            flash("Error fetching user name.", "danger")
            return redirect(url_for('national_manager.view_request_details', request_id=request_id))
        
        flash(f"{user_name}'s account holder application has been rejected.", "danger")
    
    # Send message
    send_message(11, user_id, message_content, 1)
    
    return redirect(url_for('national_manager.view_requests'))




@national_manager.route('/update_order_status/<int:depot_orderid>', methods=['POST'])
def update_order_status(depot_orderid):
    # Processes the update of an order's status,
    # sends a message to the customer if the status is changed to 'Shipped',
    # and redirects to the update_order_statuses endpoint.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    # Check if the form is submitted and valid
    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data

        update_order_status_by_depot_orderid(depot_orderid, status_id)

        order_hdr_id, user_id = get_order_hdr_and_user_id(depot_orderid)

        # Send a message to the customer based on the new status
        if status_id == "3" or status_id == 3: #when the order is shipped
            send_message(11, user_id, "Great news! Your order #{} has been successfully shipped and is now on its way to you. Get ready to receive your items soon! Should you have any questions or need further assistance, feel free to reach out. We're here to help. Happy shopping!".format(order_hdr_id), 1)
    
        flash(f"Order {order_hdr_id} status updated successfully.", "success")
        return redirect(url_for('national_manager.update_order_statuses'))

    # Fetch orders for the current depot
    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)

    return render_template('national_manager_update_order_status.html', orders=orders, form=form)




@national_manager.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    # Fetches orders and renders them along with a form to update their statuses in the national_manager_update_order_status.html template.

    # Check authentication and authorisation    
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    # Get all orders
    selected_depot = request.args.get('depot_id')

    # Check if a depot is selected
    if selected_depot and selected_depot != 'all':
        orders = get_all_orders(selected_depot)
    
    else:
        orders = get_all_orders() 

    depots = get_all_depots()  

    return render_template('national_manager_update_order_status.html', orders=orders, form=form, depots=depots, selected_depot=selected_depot)




@national_manager.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    # Fetches the order details and customer information 
    # based on the given order header ID and depot order ID.
    #  Allows national managers to updatethe order status using a form.

    # Check authentication and authorisation    
    auth_response = check_is_national_manager()  
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    # Check if the form is submitted and valid
    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_order_id, status_id)

        flash(f"Order {depot_order_id} status updated successfully.", "success")

        return redirect(url_for('national_manager.update_order_statuses')) 

    # Get order details and customer info
    order_details = get_order_details(order_hdr_id)
    customer_info = get_customer_info(order_hdr_id)

    return render_template('national_manager_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)




@national_manager.route('/view_daily_orders', methods=['GET'])
def view_daily_orders():
    # Fetches orders based on optional filters such as depot, order date, status, and customer name.
    #  Validates the customer name to ensure it contains only letters.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Get orders based on filters
    depot_id = request.args.get('depot_id')
    order_date = request.args.get('order_date')
    status = request.args.get('status')
    customer_name = request.args.get('customer_name')

    # Validate customer_name to ensure it only contains letters
    if customer_name and not customer_name.isalpha():
        flash("Customer name can only contain letters.", "danger")
        return redirect(url_for('national_manager.view_daily_orders'))

    # Get orders based on filters
    orders = get_filtered_orders(depot_id, order_date, status, customer_name)
    status_choices = get_status_choices()
    depots = get_all_depots()

    return render_template('national_manager_view_daily_orders.html', orders=orders, status_choices=status_choices, depots=depots)




@national_manager.route('/manage_credit_limits', methods=['GET', 'POST'])
def manage_credit_limits():
    # Allows national managers to manage credit limits for account holders.
    # Retrieves depots and selected depot. If the form is submitted, updates the credit limit for the selected account holder.
    # Displays account holders based on the selected depot, or all account holders if no depot is selected.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Get depots and select depot
    depots = get_all_depots()  
    if not depots:
        depots = []

    selected_depot = request.args.get('depot_id')

    # Check if the form is submitted
    if request.method == 'POST':
        account_holder_id = request.form.get('account_holder_id')
        new_credit_limit = request.form.get('new_credit_limit')
        account_holder_id, business_name = update_credit_limit(account_holder_id, new_credit_limit)
        
        flash(f"Credit limit updated successfully for {business_name}.", "success")
        return redirect(url_for('national_manager.manage_credit_limits', depot_id=selected_depot))

    # Get account holders based on selected depot
    if selected_depot and selected_depot != 'all':
        account_holders = get_account_holders_by_depot(selected_depot)
    
    else:
        account_holders = get_all_account_holders()

    if not account_holders:
        account_holders = []

    return render_template('national_manager_manage_credit_limits.html', account_holders=account_holders, depots=depots, selected_depot=selected_depot)




@national_manager.route('/manage_staff', methods=['GET'])
def manage_staff():
    # Retrieves staff members based on the selected depot. 
    # If no depot is selected, retrieves all staff members. Renders the 'national_manager_manage_staff.html' template with staff members and depot information.

    # Check authentication and authorisation    
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Get staff members based on selected depot
    selected_depot = request.args.get('depot_id', default='all', type=str)
    
    if selected_depot == 'all':
        staff_members = get_all_staff_members()
    
    else:
        staff_members = get_staff_by_depot(selected_depot)
    
    depots = get_all_depots()

    return render_template('national_manager_manage_staff.html', staff_members=staff_members, selected_depot=selected_depot, depots=depots)




@national_manager.route('/edit_staff/<int:staff_id>', methods=['GET', 'POST'])
def edit_staff(staff_id):
    # Retrieves staff details by ID. On form submission, validates and updates the staff member's details in the database. 
    # Renders the 'national_manager_edit_staff.html'template with staff details, roles, and depots for selection.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Check if the form is submitted
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']
        role_id = request.form['role_id']
        depot_id = request.form['depot_id']
        password = request.form.get('password', None)

        # Validate email
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('national_manager.edit_staff', staff_id=staff_id))


        # Validate names
        if not first_name.isalpha() or not last_name.isalpha():
            flash('Name must contain only letters', 'danger')
            return redirect(url_for('national_manager.edit_staff', staff_id=staff_id))

        # Validate phone number
        if not phone_number.isdigit():
            flash('Phone number must contain only number', 'danger')
            return redirect(url_for('national_manager.edit_staff', staff_id=staff_id))

        # Validate age (date_of_birth should be a valid date and user should be 18+)
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            flash('Staff member must be at least 18 years old', 'danger')
            return redirect(url_for('national_manager.edit_staff', staff_id=staff_id))
        
        # Validate password if provided
        if password:
            password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$'
            if not re.match(password_pattern, password):
                flash('Password must be at least 8 characters long and include a mix of character types.', 'danger')
                return redirect(url_for('national_manager.edit_staff', staff_id=staff_id))

        # Hash password if provided
        hashed_password = my_hashing.hash_value(password, salt='myhashsalt') if password else None

        # Update staff member details
        try:
            update_staff(staff_id, email, first_name, last_name, address, phone_number, date_of_birth, role_id, depot_id, hashed_password)
            flash('Staff member details updated successfully!', 'success')
        
        # Handle exceptions
        except Exception as e:
            flash(f'Failed to update staff member details. Error: {str(e)}', 'danger')
        
        return redirect(url_for('national_manager.manage_staff'))

    # Retrieve staff details, roles, and depots
    staff_member = get_staff_by_id(staff_id)
    roles = get_all_roles()
    depots = get_all_depots()

    return render_template('national_manager_edit_staff.html', staff=staff_member, roles=roles, depots=depots)




@national_manager.route('/delete_staff/<int:staff_id>', methods=['POST'])
def delete_staff(staff_id):
    # Retrieves the staff member by ID and attempts to delete it from the database.
    # If successful, a success flash message is displayed; otherwise, an error flash message is displayed.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Delete staff member
    try:
        delete_staff_member(staff_id)
        flash('Staff member deleted successfully!', 'success')

    # Handle exceptions    
    except Exception as e:
        flash('Failed to delete staff member. Error: ' + str(e), 'danger')
    
    return redirect(url_for('national_manager.manage_staff'))




@national_manager.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    # Adds a new staff member.
    # Validates the form data submitted by the user to ensure it meets the required criteria.
    # If the data is valid, a new staff member is added to the database.
    # Displays success or error flash messages accordingly.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    # Check if the form is submitted
    if request.method == 'POST':
        # Retrieve form data
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']
        role_id = request.form['role_id']
        depot_id = request.form['depot_id']
        password = request.form['password']

        # Validate email
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('national_manager.add_staff'))
        
        # Check if email already exists
        if user_exists_with_email(email):
            flash('Email address already in use', 'danger')
            return redirect(url_for('national_manager.add_staff'))

        # Validate names
        if not first_name.isalpha() or not last_name.isalpha():
            flash('Name must contain only letters', 'danger')
            return redirect(url_for('national_manager.add_staff'))

        # Validate phone number
        if not phone_number.isdigit():
            flash('Phone number must contain only number', 'danger')
            return redirect(url_for('national_manager.add_staff'))

        # Validate age (date_of_birth should be a valid date and user should be 18+)
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            flash('User must be 18 years or older', 'danger')
            return redirect(url_for('national_manager.add_staff'))

        # Validate password
        if password:
            password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$'
            if not re.match(password_pattern, password):
                flash('Password must be at least 8 characters long and include a mix of character types.', 'danger')
                return redirect(url_for('national_manager.add_staff'))

        # Hash password
        hashed_password = my_hashing.hash_value(password, salt='myhashsalt')

        # Add new staff member
        try:
            add_new_staff(email, first_name, last_name, address, phone_number, date_of_birth, role_id, depot_id, hashed_password)
            flash('Staff member added successfully!', 'success')
        
        # Handle exceptions
        except Exception as e:
            flash(f'Failed to add staff member. Error: {str(e)}', 'danger')
            
        return redirect(url_for('national_manager.manage_staff'))

    # Retrieve roles and depots for the form
    roles = get_all_roles()
    depots = get_all_depots()

    return render_template('national_manager_add_staff.html', roles=roles, depots=depots)




@national_manager.route('/create_box', methods=['GET', 'POST'])
def create_box():
    # Handles the creation of a new box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the create_box_func() function.
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return create_box_func()




@national_manager.route('/add_box_content/')
@national_manager.route('/add_box_content/', defaults={'category_name': 'All'})
@national_manager.route('/add_box_content/<category_name>/')
def add_box_content(category_name="All"):
    # Handles adding content to a box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the add_box_content_func() function with the specified category_name.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return add_box_content_func(category_name)




@national_manager.route("/add_to_box/<product_id>", methods=["GET"])
def add_to_box(product_id):
    # Handles adding a product to a box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the add_to_box_func() function with the specified product_id.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return add_to_box_func(product_id)




@national_manager.route('/review_box')
def review_box():
    # Displays the review box page for the national manager.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the review_box_func() function to handle displaying the review box page.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return review_box_func()




@national_manager.route('/confirm_box', methods=['GET', 'POST'])
def confirm_box():
    # Handles the confirmation of the box contents by the national manager.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the confirm_box_func() function to handle the confirmation process.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return confirm_box_func()



@national_manager.route('/clear_box')
def clear_box():
    # Clears the contents of the box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the clear_box_func() function to clear the box contents.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return clear_box_func()



@national_manager.route('/delete_box_item/<int:item_id>')
def delete_box_item(item_id):
    # Deletes an item from the box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the delete_box_item_func() function to delete the specified item from the box.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return delete_box_item_func(item_id)




@national_manager.route('/view_boxes')
def view_boxes():
    #  Displays the list of boxes.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the view_boxes_func() function to retrieve and display the list of boxes.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return view_boxes_func()




@national_manager.route('/view_box/<int:box_id>')
def view_box(box_id):
    # Displays the details of a specific box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the view_box_func() function to retrieve and display the details of the specified box.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return view_box_func(box_id)
 



@national_manager.route('/delete_box/<int:box_id>')
def delete_box(box_id):
    # Deletes a specific box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the delete_box_func() function to delete the specified box.
    
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return delete_box_func(box_id)




@national_manager.route('/delete_box_detail/<int:item_product_id>')
def delete_box_detail(item_product_id):
    # Deletes a specific item from a box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the delete_box_detail_func() function to delete the specified item from the box.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return delete_box_detail_func(item_product_id)



@national_manager.route("/add_to_existing_box/<product_id>", methods=["GET"])
def add_to_existing_box(product_id):
    # Adds a product to an existing box.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, calls the add_to_existing_box_func() function to add the product to the existing box.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    return add_to_existing_box_func(product_id)



@national_manager.route('/view_credit_limit_increase_requests', methods=['GET', 'POST'])
def view_credit_limit_increase_requests():
    # Displays credit limit increase requests.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, retrieves credit limit increase requests based on the selected depot (if any) or all depots.
    # Handles form submission for filtering by depot.
    # Renders the 'nm_credit_limit_increase_list.html' template with the list of requests and depot filter dropdown.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    depot_id = None
    depot_name = "All"

    # Handle the form submission for filtering
    if request.method == 'POST':
        depot_id = request.form.get('depot_id')
        if depot_id:
            requests = get_credit_limit_increase_requests(depot_id=depot_id)
            depot_name = get_depot_name_by_id(depot_id)
        else:
            requests = get_credit_limit_increase_requests()
    else:
        requests = get_credit_limit_increase_requests()

    # Get list of depots for the filter dropdown
    depots = get_all_depots()

    return render_template('nm_credit_limit_increase_list.html', requests=requests, depots=depots, selected_depot_name=depot_name)



@national_manager.route('/view_credit_limit_increase_request/<int:request_id>', methods=['GET'])
def view_credit_limit_increase_request(request_id):
    # Displays details of a specific credit limit increase request.
    # Checks if the user is authenticated and authorized as a national manager.
    # If authenticated, retrieves information about the specified credit limit increase request.
    # Renders the 'nm_credit_limit_increase_details.html' template with the request information.

    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    request_info = get_credit_limit_increase_request_info(request_id)

    return render_template('nm_credit_limit_increase_details.html', request_info=request_info)
    


@national_manager.route('/handle_credit_limit_request/<int:request_id>', methods=['POST'])
def handle_credit_limit_request(request_id):
    # Handles the approval or rejection of a credit limit increase request.
    # Checks if the user is authenticated and authorized as a national manager.
    # Retrieves the action, message content, and requested credit limit from the form.
    # Based on the action, updates the credit limit and processes the request accordingly.
    # Sends a message to the user regarding the decision.
    # Redirects to the view_credit_limit_increase_requests route.
    
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    action = request.form['action']
    message_content = request.form['message']
    credit_limit = request.form.get('credit_limit', type=int)
    requested_limit = request.form['requested_limit']

    # get user_id and credit_account_id and user name
    user_id = get_user_id_from_credit_limit_request(request_id)

    credit_account_id = get_credit_account_id(user_id)

    user_name = get_user_full_name(user_id)
    
    # if approving the requested amount
    if action == 'approve_same':
        new_limit = requested_limit

        update_credit_limit_after_processing_request(new_limit, credit_account_id)

        approve_credit_limit_request(new_limit, request_id)

        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been approved,<br><br>"
                            f'The new credit limit is ${new_limit}.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'success')

    # if approving a different amount
    elif action == 'approve_diff' and credit_limit is not None:
        new_limit = credit_limit

        update_credit_limit_after_processing_request(new_limit, credit_account_id)

        approve_credit_limit_request(new_limit, request_id)

        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been approved,<br><br>"
                            f'The new credit limit is ${new_limit}.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'success')

    # if declining the request and keeping the current credit limit
    elif action == 'reject':

        reject_credit_limit_request(request_id)

        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been declined,<br><br>"
                            f'The credit limit remains the same as before.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'warning')
    
    # Send message
    send_message(11, user_id, message_content, 1)
    
    return redirect(url_for('national_manager.view_credit_limit_increase_requests'))




@national_manager.route('/view_trigger_list', methods=['GET'])
def view_trigger_list():
    # Displays the trigger list for national managers.
    # Checks if the user is authenticated and authorized as a national manager.
    # Retrieves all active subscriptions and filters out subscriptions with orders due.
    # Renders the national_manager_trigger_list.html template with the due subscriptions.
    
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    subscriptions = get_all_active_subscription_display()

    due_subscriptions = [subscription for subscription in subscriptions if is_order_due(subscription[-1], subscription[-2])]

    return render_template('national_manager_trigger_list.html', subscriptions=due_subscriptions)




@national_manager.route('/create_subcription_orders', methods=["POST"])
def create_subcription_orders():
    # Creates subscription orders for active subscriptions.
    # Checks if the user is authenticated and authorized as a national manager.
    # Retrieves the GST rate and current date.
    # Retrieves all active subscriptions.
    # Iterates over active subscriptions and creates orders for subscriptions with due orders.
    # Updates subscription quantities after creating orders.
    # Flashes a success message and redirects to the trigger list view.
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    gst_rate = get_gst_rate() / 100
    
    payment_date = datetime.now().strftime('%Y-%m-%d')

    subscriptions = get_all_active_subscription()

    # Iterate over active subscriptions
    for subscription in subscriptions:
        checkout_cart_items = {}
        subtotal = 0

        # Check if there are orders due for the subscription
        if int(subscription[5]) > 0 and is_order_due(subscription[8], subscription[2]): #quantity of order to be placed
            user_id = subscription[0]
            line_total = float(subscription[7]) * 1 #price * 1 (assumming subscription purchase is always on 1 box)
            subtotal += line_total

            # Create a new dictionary for the item with additional information
            product_info = get_full_product_info_by_id(subscription[6])

            item_for_checkout_info = {
                'product_id': subscription[6],
                'name': product_info[0],
                'quantity': 1,
                'price': subscription[7],
                'unit': str(product_info[5]) + product_info[6]
            }
            
            # Add the item dictionary
            checkout_cart_items[subscription[6]] = {
                'item_info': item_for_checkout_info,
                'line_total': line_total
            }

            shipping_fee = get_customer_shipping_fee(subscription[0])
            subtotal += float(shipping_fee)
            tax = ("%.2f" % (gst_rate * float(subtotal)))
            grandtotal = "%.2f" % float(subtotal)

            order_hdr_id = create_order(grandtotal, checkout_cart_items, user_id, "subscription_order")

            payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date,user_id)

            invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

            update_subscription_quantity(subscription[1])


    flash('Subscription orders triggered successfully!', 'success')

    return redirect(url_for('national_manager.view_trigger_list'))




@national_manager.route("/nm_add_product_type", methods=["GET", "POST"])
def nm_add_product_type():
    # Renders the form to add a new product type and handles the submission of the form.
    # On form submission, validates the form data, processes the image, and adds a new product type.
    # Flashes success or error messages accordingly.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddProductTypeForm()

    if form.validate_on_submit():
        images = request.files.getlist('product_image')

        # Get the image data
        image_data = images[0].read()

        # Get form data
        product_name = form.product_name.data
        product_unit = form.product_unit.data
        product_description = form.product_description.data
        product_category = form.product_category.data

        # Check if the product type name already exists
        if get_product_type_by_name(product_name):
            flash("Product type name already exist", "danger")
            return render_template("nm_add_product_type.html", form=form)

        # Add the new product type
        add_new_product_type(image_data, product_name, product_unit, product_description, product_category)

        flash("Product type created successfully", "success")
        
        return nm_search_product_type()
    
    flash_form_errors(form)
    
    return render_template("nm_add_product_type.html", form=form)




@national_manager.route("/nm_search_product_type", methods=["GET","POST"])
def nm_search_product_type():
    # Renders the search form for product types and displays the product types based on search criteria.
    # On GET request, retrieves search criteria from the request parameters and displays matching product types.
    # On POST request, validates the form data, retrieves search criteria, and displays matching product types.
    # Also, retrieves product categories for the form.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
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
        # Retrieve search criteria from request parameters
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
    
    return render_template("nm_product_type_list.html", form=form, products=products, page=page_num, total_pages=total_pages, categories=categories, product_name=product_name, product_category=product_category)




@national_manager.route("/nm_edit_product_type/<product_type_id>", methods=["GET", "POST"])
def nm_edit_product_type(product_type_id):
    # Renders the form to edit product type information and handles the update of product type details.

    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
 
    form = EditProductTypeForm()
    product = get_product_type_by_id(product_type_id)

    if not product:
        flash('Product Type not found!', 'danger')
        return redirect(url_for('national_manager.nm_search_product_type'))
 
    # When user clicks on submit button
    if form.validate_on_submit():

        images = request.files.getlist('product_image')

        # Read image data if provided
        image_data = images[0].read()

        # Retrieve form data
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
            return render_template("nm_edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])
 
        else:
            # Update product type in db with the product picture
            update_product_type(product_type_id,image_data, product_name, product_unit, product_description, product_category)
 
        # Return to the product type page after the successful update
        flash("Information updated successfully.", "success")
        return nm_search_product_type()

    # Pre-fill form fields with existing product type data
    form.product_name.data = product[1]
    form.product_unit.data = str(product[4])
    form.product_description.data = product[3]
    form.product_category.data = str(product[5])
 
    flash_form_errors(form)

    return render_template("nm_edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])




# Deletes a product type by its ID.
@national_manager.route("/nm_delete_product_type/<product_type_id>", methods=["GET", "POST"])
def nm_delete_product_type(product_type_id):
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    delete_product_type_by_id(product_type_id)
 
    flash("Product Type deleted successfully.", "success")
    return nm_search_product_type()




#  Allows the national manager to reply to a message.
@national_manager.route('/reply_message/<int:message_id>', methods=["GET", "POST"])
def nm_reply_message(message_id):
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = ReplyMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            message_content = form.message_content.data

            # Get additional message details from the form
            message_category = request.form.get('message_category')
            original_message = request.form.get('original_message')
            sender_id = request.form.get('sender_id')

            message_content = f"{message_content}\n=====\n{original_message}\n=====\n"

            send_message(session['user_id'], sender_id, message_content, message_category, session['user_depot'])

            update_message_by_id(message_id, 4)

            flash("Your message has been sent successfully", "success")
            return redirect(url_for('national_manager.nm_getMessages'))

    # Get the details of the message to reply to
    message = get_message_by_id(message_id)
    
    return render_template('national_manager_reply_message.html', form=form, message=message)
