from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from fhd.utilities import flash_form_errors, check_auth, delete_message_by_id
from fhd.utilities import get_user_full_name, get_product_weight, get_all_messages_by_user_id
from fhd.utilities import add_product_weight_by_id, delete_product_weight_by_id
from fhd.utilities import update_product_weight, unit_exists_check
from fhd.utilities import get_all_category_List, category_exists_check
from fhd.utilities import insert_product_category, get_product_category_by_id, update_product_category, delete_product_category
from fhd.utilities import get_all_shipping_option_list, insert_shipping_option, get_shipping_option_name_by_id, update_shipping_option
from fhd.utilities import delete_shipping_option_by_id, get_all_depots, get_products_by_depot_and_status
from fhd.utilities import get_all_pending_requests, get_request_details, get_user_id_from_account_holder,reject_request, send_message
from fhd.utilities import get_credit_limit, update_account_holder, update_user_role, get_status_choices, update_order_status_by_depot_orderid
from fhd.utilities import get_order_hdr_and_user_id, get_all_orders, get_current_user_depot_id, get_order_details, get_customer_info
from fhd.national_manager.forms import AddProductWeightForm, EditProductWeightForm, AddCategoryForm, EditCategoryForm, AddShippingOptionForm
from fhd.national_manager.forms import EditShippingOptionForm, UpdateOrderStatusForm
from fhd.utilities import insert_product_category, get_product_category_by_id, update_product_category, delete_product_category, get_all_product, update_product, edit_product, check_low_stock_product_by_all
from fhd.national_manager.forms import ViewProductForm, EditProductForm
from markupsafe import Markup


national_manager = Blueprint("national_manager", __name__, template_folder="templates")
# region functions
def check_is_national_manager():
    return check_auth(5)

# endregion

# region routes


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
# endregion

@national_manager.route("/add_product_weight", methods=["GET", "POST"])
def add_product_weight():
    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddProductWeightForm()

    if form.validate_on_submit():
        # Extract data from the form
        weight_str = form.weight.data
        if weight_str:
            try:
                weight = float(weight_str)
                if weight == 0:
                    weight = None
            except ValueError:
                flash("Weight must be a positive number or zero.", "danger")
                return render_template('national_manager_add_product_weight.html', form=form)

        else:
            weight = None
        
        unit = form.unit.data

        unit_exists = unit_exists_check(weight, unit)

        if unit_exists:
            flash("Product Unit already exists", "danger")
            return render_template('national_manager_add_product_weight.html', form=form)

        add_product_weight_by_id(weight, unit)
        flash("New product unit added successfully.", "success")
        return redirect(url_for('national_manager.view_product_weight'))

    return render_template('national_manager_add_product_weight.html', form=form)



@national_manager.route("/view_product_weight", methods=["GET", "POST"])
def view_product_weight():

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    product_weight = get_product_weight()
    return render_template("national_manager_view_product_weight.html", product_weight=product_weight)



@national_manager.route("/delete_product_weight/<int:product_weight_id>", methods=["GET", "POST"])
def delete_product_weight(product_weight_id):

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


@national_manager.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('national_manager_messages_list.html', messages=messages)



@national_manager.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
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
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    categories = get_all_category_List()
    
    return render_template('national_manager_category_list.html', categories=categories)

@national_manager.route('/add_category', methods=["GET", "POST"])
def add_category():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddCategoryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            category_name = form.categoryname.data
            status = form.status.data

            category_exists = category_exists_check(category_name)

            if category_exists:
                flash("Product Category already exists", "danger")
                return render_template('national_manager_add_category.html',form=form)

            insert_product_category(category_name, status)

            flash("Product Category created successfully", "success")
            categories = get_all_category_List()
    
            return render_template('national_manager_category_list.html', categories=categories)

    return render_template('national_manager_add_category.html', form=form)

@national_manager.route('/edit_category/<int:category_id>', methods=["GET", "POST"])
def edit_category(category_id):
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = EditCategoryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            category_name = form.categoryname.data
            status = form.status.data

            update_product_category(category_id, category_name, status)

            flash("Product Category updated successfully", "success")
            categories = get_all_category_List()
    
            return render_template('national_manager_category_list.html', categories=categories)
    
    category = get_product_category_by_id(category_id)
    form.categoryname.data = category[1]
    form.status.data = category[2]

    return render_template('national_manager_edit_category.html', form=form, category_id=category_id)

@national_manager.route('/delete_category/<int:category_id>', methods=["GET", "POST"])
def delete_category(category_id):
        
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
    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = ViewProductForm()

    depots = get_all_depots()
    form.depot.choices = [(0, 'All Depots')] + [(int(d['id']), d['name']) for d in depots]

    selected_depot = None
    selected_status = 'All'

    if request.method == 'POST':
        selected_depot = int(request.form.get('depot'))
        selected_status = request.form.get('status')
    else:
        selected_depot = request.args.get('depot', 0, type=int)  # Get from query parameters if GET
        selected_status = request.args.get('status', 'All')  # Get status from query parameters if GET

    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    products, total = get_products_by_depot_and_status(selected_depot, selected_status, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template('national_manager_product_list.html', form=form, products=products, depots=depots, selected_depot=selected_depot, selected_status=selected_status, page=page, total_pages=total_pages)


@national_manager.route('/getShippingOptionList')
def getShippingOptionList():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
      
    shipping_option = get_all_shipping_option_list()
    
    return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)


@national_manager.route('/addShippingOption', methods=["GET", "POST"])
def addShippingOption():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = AddShippingOptionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            shipping_option_name = form.shippingOption.data
            shipping_price = form.price.data
            status = form.status.data

            shipping_option_exists = category_exists_check(shipping_option_name)

            if shipping_option_exists:
                flash("Shipping option already exists", "danger")
                return render_template('national_manager_add_shipping_option.html',form=form)

            insert_shipping_option(shipping_option_name, shipping_price, status)

            flash("Shipping option created successfully", "success")
            shipping_option = get_all_shipping_option_list()
    
            return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)

    return render_template('national_manager_add_shipping_option.html', form=form)

@national_manager.route('/edit_shipping_option/<int:shipping_option_id>', methods=["GET", "POST"])
def edit_shipping_option(shipping_option_id):
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    
    form = EditShippingOptionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            shipping_option_name = form.shippingOption.data
            shipping_price = form.price.data
            status = form.status.data

            update_shipping_option(shipping_option_id, shipping_option_name, shipping_price, status)

            flash("Shipping option updated successfully", "success")
            shipping_option = get_all_shipping_option_list()
    
            return render_template('national_manager_shipping_option_list.html', shipping_option=shipping_option)
        
    shipping_option = get_shipping_option_name_by_id(shipping_option_id)
    form.shippingOption.data = shipping_option[1]
    form.price.data = shipping_option[2]
    form.status.data = shipping_option[3]

    return render_template('national_manager_edit_shipping_option.html', form=form, shipping_option_id=shipping_option_id)


@national_manager.route("/national_manager_edit_product/<int:product_id>", methods=["GET", "POST"])
def national_manager_edit_product(product_id):
  
    auth_response = check_is_national_manager()
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
        return redirect(url_for('national_manager.national_manager_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('national_manager_edit_product.html', form=form, product=product, product_id=product_id)


@national_manager.route('/delete_shipping_option/<int:shipping_option_id>', methods=["GET", "POST"])
def delete_shipping_option(shipping_option_id):
        
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
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    requests = get_all_pending_requests()
    return render_template('national_manager_view_requests.html',requests=requests)


@national_manager.route('/view_request_details/<int:request_id>', methods=['GET'])
def view_request_details(request_id):
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response
    request = get_request_details(request_id)
    
    if request is None:
        flash("Request not found.", "danger")
        return redirect(url_for('national_manager.view_requests'))
    
    return render_template('national_manager_view_request_details.html', request=request)


@national_manager.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):
    action = request.form['action']
    message_content = request.form['message']
    
    # get user_id from account_holder
    user_id = get_user_id_from_account_holder(request_id)
    if user_id is None:
        flash("Error fetching user ID.", "danger")
        return redirect(url_for('national_manager.view_request_details', request_id=request_id))
    
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
    auth_response = check_is_national_manager()
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
        return redirect(url_for('national_manager.update_order_statuses'))

    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)
    return render_template('national_manager_update_order_status.html', orders=orders, form=form)


@national_manager.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    selected_depot = request.args.get('depot_id')
    if selected_depot:
        orders = get_all_orders(selected_depot)
    else:
        orders = []

    depots = get_all_depots()  # Assuming you have a function to get all depots
    return render_template('national_manager_update_order_status.html', orders=orders, form=form, depots=depots, selected_depot=selected_depot)


@national_manager.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    auth_response = check_is_national_manager()  
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_order_id, status_id)
        flash(f"Order {depot_order_id} status updated successfully.", "success")
        return redirect(url_for('national_manager.update_order_statuses')) 

    order_details = get_order_details(order_hdr_id)
    customer_info = get_customer_info(order_hdr_id)
    return render_template('national_manager_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)