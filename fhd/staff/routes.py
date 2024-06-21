from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, check_auth
from fhd.local_manager.routes import get_user_full_name
from fhd.utilities import flash_form_errors, check_auth, add_new_product_type, get_product_type_by_name, get_user_full_name
from fhd.utilities import get_product_category, get_all_product_type, get_product_type_by_id, update_product_type, get_products_by_user_depot
from fhd.utilities import delete_product_type_by_id, get_all_messages_by_user_id, delete_message_by_id, update_product_quantity
from fhd.utilities import get_all_orders, update_order_status_by_depot_orderid, get_status_choices, get_current_user_depot_id, get_discontinued_products
from fhd.utilities import get_order_details, get_customer_info, send_message, get_order_hdr_and_user_id, update_message_by_id, log_perished_product_removal
from fhd.utilities import cancel_order_by_id, edit_product, update_product, check_low_stock_product_by_depot, get_perished_product_logs
from fhd.staff.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm, ViewProductForm, UpdateOrderStatusForm, EditProductForm
from markupsafe import Markup
from fhd.local_manager.forms import ReplyMessageForm
from fhd.utilities import get_message_by_id


staff = Blueprint("staff", __name__, template_folder="templates")

# region functions


def check_is_staff():
    # This function checks if the current user has staff-level authorization.
    # It calls the check_auth function with a level of 3, which corresponds to staff-level access.

    return check_auth(3)

# endregion


# region routes


@staff.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # This function handles requests to the staff dashboard, accessible via the "/dashboard" route.
    # It supports both GET and POST methods.

    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
    

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
    # This function handles requests to add a new product type, accessible via the "/staff_add_product_type" route.
    # It supports both GET and POST methods.

    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = AddProductTypeForm()

    if form.validate_on_submit():
        # Get the list of uploaded product images from the request.
        images = request.files.getlist('product_image')

        
        image_data = images[0].read()

        # Retrieve product details from the form data.
        product_name = form.product_name.data
        product_unit = form.product_unit.data
        product_description = form.product_description.data
        product_category = form.product_category.data

        # Check if a product type with the same name already exists.
        if get_product_type_by_name(product_name):
            flash("Product type name already exist", "danger")
            return render_template("staff_add_product_type.html", form=form)

        # If the product type name is unique, add the new product type to the database.
        add_new_product_type(image_data, product_name, product_unit, product_description, product_category)
        
        flash("Product type created successfully", "success")
        
        return staff_search_product_type()
    
    flash_form_errors(form)

    return render_template("staff_add_product_type.html", form=form)




@staff.route("/staff_search_product_type", methods=["GET","POST"])
def staff_search_product_type():
    # This function handles requests to search for product types, accessible via the "/staff_search_product_type" route.
    # It supports both GET and POST methods.

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
        # Retrieve the product name and category from the form data.
        product_name = form.product_name.data
        product_category = form.product_category.data


    if request.method == 'GET':
        # Retrieve the product name and category from the query string.
        product_name = request.args.get('product_name')
        if product_name == '':
            product_name = None  # Set to None if empty string

        product_category = request.args.get('product_category')
        if product_category == '':
            product_category = None  # Set to None if empty string

    # Define the number of items per page for pagination.
    item_num_per_page = 20

    categories = get_product_category()

    products, total = get_all_product_type(page_num, item_num_per_page, product_category, product_name)

    total_pages = (total + item_num_per_page - 1) // item_num_per_page

    return render_template("staff_product_type_list.html", form=form, products=products, page=page_num, total_pages=total_pages, categories=categories, product_name=product_name, product_category=product_category)




@staff.route("/staff_edit_product_type/<product_type_id>", methods=["GET", "POST"])
def staff_edit_product_type(product_type_id):
    # This function handles requests to edit a product type, accessible via the "/staff_edit_product_type/<product_type_id>" route.
    # It supports both GET and POST methods.

    # Check authentication and authorisation
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
 
    form = EditProductTypeForm()

    product = get_product_type_by_id(product_type_id)

    # If the product type is not found, flash an error message and redirect to the search product type page.
    if not product:
        flash('Product Type not found!', 'danger')
        return redirect(url_for('staff.search_product_type'))
 
    # When user clicks on submit button
    if form.validate_on_submit():

        images = request.files.getlist('product_image')

        
        image_data = images[0].read()

         # Retrieve product details from the form data
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

    # Prefill the form with the existing product type data.
    form.product_name.data = product[1]
    form.product_unit.data = str(product[4])
    form.product_description.data = product[3]
    form.product_category.data = str(product[5])
 
    flash_form_errors(form)

    return render_template("staff_edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])



@staff.route("/staff_delete_product_type/<product_type_id>", methods=["GET", "POST"])
def staff_delete_product_type(product_type_id):
    # This function deletes a product type based on the provided product_type_id.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it proceeds to delete the product type by its ID.
    # Finally, it flashes a success message and redirects to the product type search page.
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    delete_product_type_by_id(product_type_id)

    flash("Product Type deleted successfully.", "success")
    return staff_search_product_type()



@staff.route('/getMessages')
def getMessages():
    # This function retrieves all messages for the currently authenticated staff user.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it proceeds to retrieve all messages associated with the user.
    # Finally, it renders a template to display the list of messages.
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('staff_messages_list.html', messages=messages)



@staff.route('/delete_message/<int:message_id>')
def delete_message(message_id):
    # This function deletes a specific message based on the provided message_id.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it proceeds to delete the message by its ID.
    # After deletion, it retrieves all remaining messages and flashes a success message.
    # Finally, it renders a template to display the updated list of messages.
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")
    return render_template('staff_messages_list.html', messages=messages)



@staff.route('/staff_product_list/<int:depot_id>', methods=["GET", "POST"])
def staff_product_list(depot_id):
    # This function displays a paginated list of products for a specific depot.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the product view form and pagination parameters.
    # It then retrieves the list of products based on the depot ID, current page, items per page, and status filter.
    # Finally, it renders a template to display the list of products with pagination controls.
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
    # This function updates the status of an order based on the provided depot_orderid.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the form for updating order status and sets the status choices.
    # It then processes the form submission to update the order status, send notifications to the customer, and handle specific status actions.
    # Finally, it flashes a success message and redirects to the order statuses update page.
    auth_response = check_is_staff()
    if auth_response:
        return auth_response
    
    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    # Update order status
    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_orderid, status_id)
        order_hdr_id, user_id = get_order_hdr_and_user_id(depot_orderid)

        # Send message to customer based on the status
        if status_id == "3" or status_id == 3: #when the order is shipped
            send_message(11, user_id, "Great news! Your order #{} has been successfully shipped and is now on its way to you. Get ready to receive your items soon! Should you have any questions or need further assistance, feel free to reach out. We're here to help. Happy shopping!".format(order_hdr_id), 1)
    
        if status_id == "5" or status_id == 5: #when the order is cancelled
            cancel_order_by_id(order_hdr_id)

        flash(f"Order {order_hdr_id} status updated successfully.", "success")
        return redirect(url_for('staff.update_order_statuses'))

    # If the form is not submitted or not valid, retrieve the current depot ID and orders
    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)

    return render_template('staff_update_order_status.html', orders=orders, form=form)



@staff.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    # This function retrieves and displays orders with the option to update their statuses.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the form for updating order status and gets all status choices.
    # It then retrieves the orders for the current depot, filtered by the selected status if provided.
    # The function processes each order to prepare the list of possible status updates.
    # Finally, it renders a template to display the orders with their update options.
    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    all_order_status = get_status_choices()

    depot_id = get_current_user_depot_id()
    selected_status = request.args.get('status')
    
    orders = get_all_orders(depot_id, status_id=selected_status)
        
    list_orders = []

    for order in orders:
        list_order = list(order)
        # We only get the status which is greater than the current status
        order_status = [status for status in all_order_status if status[0] >= int(order[6])]
        # Convert status ID to string
        order_status = [(str(status[0]), status[1]) for status in order_status]
        # Append the status at the end of the list as this is for each order
        list_order.append(order_status)
        list_orders.append(list_order)

    # Convert all status IDs to string
    all_order_status = [(str(status[0]), status[1]) for status in all_order_status]

    return render_template('staff_update_order_status.html', orders=list_orders, form=form, all_order_status=all_order_status)



@staff.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    # This function displays the details of a specific order and allows updating its status.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the form for updating order status and sets the status choices.
    # If the form is submitted and valid, it updates the order status and flashes a success message.
    # Finally, it retrieves the order details and customer information, and renders a template to display them.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    # Update order status
    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_order_id, status_id)
        flash(f"Order {depot_order_id} status updated successfully.", "success")

        return redirect(url_for('staff.view_order_details', order_hdr_id=order_hdr_id, depot_order_id=depot_order_id))

    # Retrieve order details and customer information
    order_details = get_order_details(order_hdr_id)
    customer_info = get_customer_info(order_hdr_id)

    return render_template('staff_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)



@staff.route("/staff_edit_product/<int:product_id>", methods=["GET", "POST"])
def staff_edit_product(product_id):
    # This function allows staff to edit the details of a specific product.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the form for editing the product and retrieves the current product details.
    # If the form is submitted and valid, it updates the product details in the database and flashes a success message.
    # Finally, it pre-fills the form with existing product data and renders the edit product template.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = EditProductForm()
    product = edit_product(product_id)

    # Update product details if the form is submitted and valid
    if request.method == 'POST' and form.validate_on_submit():

        new_price = form.product_price.data
        new_quantity = form.product_quantity.data

        is_discontinued = 'discontinued' in request.form

        update_product(product_id, new_price, new_quantity, is_discontinued)

        flash('Product updated successfully!', 'success')

        return redirect(url_for('staff.staff_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('staff_edit_product.html', form=form, product=product, product_id=product_id)



@staff.route('/reply_message/<int:message_id>', methods=["GET", "POST"])
def reply_message(message_id):
    # This function allows staff to reply to a specific message.
    # It first checks if the user is authenticated and authorized as staff.
    # If the user is authorized, it initializes the form for replying to the message.
    # If the form is submitted and valid, it processes the reply, sends the message, and updates the original message status.
    # Finally, it retrieves the original message details and renders a template to display the reply form.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    form = ReplyMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get form data and additional information from the request
            message_content = form.message_content.data
            message_category = request.form.get('message_category')
            original_message = request.form.get('original_message')
            sender_id = request.form.get('sender_id')

            # Append the original message to the reply
            message_content = f"{message_content}\n=====\n{original_message}\n=====\n"

            send_message(session['user_id'], sender_id, message_content, message_category, session['user_depot'])

            update_message_by_id(message_id, 4)

            flash("Your message has been sent successfully", "success")

            return redirect(url_for('staff.getMessages'))

    # Retrieve the original message details
    message = get_message_by_id(message_id)
    
    return render_template('staff_reply_message.html', form=form, message=message)



@staff.route("/staff_remove_perished_product/<int:product_id>", methods=["POST"])
def staff_remove_perished_product(product_id):
    # This route handles the removal of perished products from the stock.
    # If the removal is successful, it updates the quantity in the database and logs the removal action.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    perished_quantity = int(request.form['perished_quantity'])

    # Fetch the current product details
    product = edit_product(product_id)
    if not product:
        flash('Product not found!', 'danger')
        
        return redirect(url_for('staff.staff_product_list', depot_id=session['user_depot']))

    current_quantity = product[3]

    # Validate the perished quantity
    if perished_quantity > current_quantity:
        flash(f'Cannot remove {perished_quantity} items. Only {current_quantity} available.', 'danger')
        
        return redirect(url_for('staff.staff_edit_product', product_id=product_id))

    # Calculate the new quantity after removal
    new_quantity = max(0, current_quantity - perished_quantity)
    product_name = product[1]

    # Update the product quantity in the database
    update_product_quantity(product_id, new_quantity)

    # Log the removal
    log_perished_product_removal(product_id, product_name, perished_quantity)

    flash(f'{perished_quantity} {product_name} removed from stock. Updated quantity is {new_quantity}.', 'success')
    
    return redirect(url_for('staff.staff_edit_product', product_id=product_id))



@staff.route("/staff_perished_product_log", methods=["GET"])
def staff_perished_product_log():
    # This route retrieves the log of perished product removals from the database and displays them paginated.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    # Get the page number from the request, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of logs per page

    # Retrieve perished product logs from the database
    logs, total_logs = get_perished_product_logs(page, per_page)
    total_pages = (total_logs + per_page - 1) // per_page  # Calculate total pages

    return render_template('staff_perished_product_log.html', logs=logs, page=page, total_pages=total_pages)


@staff.route("/staff_discontinued_products", methods=["GET"])
def staff_discontinued_products():
    # This route retrieves a list of discontinued products from the database and renders a template to display them.

    auth_response = check_is_staff()
    if auth_response:
        return auth_response

    discontinued_products_list = get_discontinued_products()

    return render_template('staff_discontinued_products.html', discontinued_products=discontinued_products_list)
