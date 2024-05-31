from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from fhd.utilities import flash_form_errors, check_auth, add_new_product_type, get_product_type_by_name, get_user_full_name
from fhd.utilities import get_product_category, get_all_product_type, get_product_type_by_id, update_product_type, get_products_by_user_depot, update_product, edit_product
from fhd.utilities import delete_product_type_by_id, delete_message_by_id, get_all_messages_by_user_id, get_status_choices
from fhd.utilities import update_order_status_by_depot_orderid, get_order_hdr_and_user_id, get_current_user_depot_id
from fhd.utilities import get_all_orders, get_customer_info, send_message, get_order_details, add_new_product, get_box_price_by_box_size_id
from fhd.utilities import add_new_box, get_depot_name_by_id, get_all_products, get_product_category_without_box, get_products_by_ids
from fhd.utilities import set_box_and_its_product_active, delete_inactive_product_box, get_pending_requests, check_low_stock_product_by_depot
from fhd.utilities import get_request_details, get_credit_limit, update_account_holder, get_user_id_from_account_holder, update_user_role
from fhd.utilities import reject_request, get_all_weekly_boxes, get_box_details_by_id, set_box_product_to_inactive, get_message_by_id
from fhd.utilities import get_box_product_name_by_box_id, update_box_with_product_id, delete_single_content_from_box, get_box_product_quantity_by_id
from fhd.utilities import delete_all_box_content_by_box_id, get_box_product_name_by_product_id, update_message_by_id
from fhd.local_manager.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm, ViewProductForm, EditProductForm
from fhd.local_manager.forms import UpdateOrderStatusForm, AddBoxForm, ReplyMessageForm
from datetime import datetime, timedelta
from markupsafe import Markup

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
    
    # Retrieve depot_id from the session
    depot_id = session.get('user_depot')
    
    # Check for low stock products and set a flash message if any
    if check_low_stock_product_by_depot(depot_id):
        flash(Markup('Warning: Some products are low in stock! <a href="' + url_for('local_manager.local_manager_product_list', depot_id=session['user_depot']) + '">Click here to check product inventory</a>'), 'danger')

    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)

    # Clear these if user click on dashboard while in the process of creating a box
    session.pop('box_contents', None)
    session.pop('box_id', None)
    return render_template("local_manager_dashboard.html", name=name)

@local_manager.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('local_manager_messages_list.html', messages=messages)

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

@local_manager.route('/local_manager_product_list/<int:depot_id>', methods=["GET", "POST"])
def local_manager_product_list(depot_id):

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = ViewProductForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Define the number of items per page
    status_filter = request.args.get('status', '')
    
    products, total_products = get_products_by_user_depot(depot_id, page, per_page, status_filter)
    
    return render_template('local_manager_product_list.html', form=form, products=products, depot_id=depot_id, page=page, per_page=per_page, total_products=total_products)

@local_manager.route("/local_manager_edit_product/<int:product_id>", methods=["GET", "POST"])
def local_manager_edit_product(product_id):
    auth_response = check_is_local_manager()
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
        return redirect(url_for('local_manager.local_manager_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('local_manager_edit_product.html', form=form, product=product, product_id=product_id)



@local_manager.route('/update_order_status/<int:depot_orderid>', methods=['GET', 'POST'])
def update_order_status(depot_orderid):
    auth_response = check_is_local_manager()
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
        return redirect(url_for('local_manager.update_order_statuses'))

    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)
    return render_template('local_manager_update_order_status.html', orders=orders, form=form)


@local_manager.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)
    return render_template('local_manager_update_order_status.html', orders=orders, form=form)

@local_manager.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = UpdateOrderStatusForm()
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        status_id = form.status.data
        update_order_status_by_depot_orderid(depot_order_id, status_id)
        flash(f"Order {depot_order_id} status updated successfully.", "success")
        return redirect(url_for('local_manager.update_order_statuses'))
    
    order_details = get_order_details(order_hdr_id)
    customer_info = get_customer_info(order_hdr_id)
    return render_template('local_manager_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)


@local_manager.route('/create_box', methods=['GET', 'POST'])
def create_box():
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    form = AddBoxForm()
    if request.method == 'POST' and form.validate_on_submit():
        box_name = form.box_name.data
        box_unit = form.box_unit.data
        box_size = form.box_size.data
        box_description = form.box_description.data
        box_stock = form.box_stock.data
        box_image = request.files.getlist('box_image')
        if len(box_image) == 0 or (len(box_image) == 1 and box_image[0].filename == ''):
            flash("Box image is required!", "danger")
            return render_template("local_manager_create_box.html", form=form)
        else:
            image_data = box_image[0].read()
        
        # Add a new product type, product and box, set product and box is_active = 0 for now
        product_type_id = add_new_product_type(image_data, box_name, box_unit, box_description, 7)
        depot_id = get_current_user_depot_id()
        box_price = get_box_price_by_box_size_id(box_size)
        product_id = add_new_product(box_price, box_stock, depot_id, product_type_id, 0)

        # Get today's date
        today = datetime.now()
        # Calculate the current week's Sunday's date
        # If today is Sunday (index 6), today is already the current week's Sunday
        if today.weekday() == 6:
            current_week_sunday = today
        else:
            # Calculate days to add to reach Sunday (6 - today.weekday())
            days_to_sunday = 6 - today.weekday()
            current_week_sunday = today + timedelta(days=days_to_sunday)

        box_id = add_new_box(product_id, box_size, today, current_week_sunday, 0)
        session['box_id'] = box_id
        return redirect(url_for('local_manager.add_box_content'))

    flash_form_errors(form)
    return render_template("local_manager_create_box.html", form=form)

@local_manager.route('/add_box_content/')
@local_manager.route('/add_box_content/', defaults={'category_name': 'All'})
@local_manager.route('/add_box_content/<category_name>/')
def add_box_content(category_name="All"):
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    box_id = request.args.get('box_id')
    if not box_id:
        box_id = None

    if 'box_id' not in session and box_id is None:
        flash('Please create a box first!', 'danger')
        return redirect(url_for('local_manager.create_box'))
    
    # Initialize box_contents as an empty dictionary
    box_contents = {}

    if 'box_id' in session and 'box_contents' in session:
        box_contents = session['box_contents']

    if box_id is not None:
        box_contents = get_box_product_quantity_by_id(box_id)


    # Get the page number from the query string
    page_num = request.args.get('page', 1, type=int)
    item_num_per_page = 11

    # Replace '-' back to ' '
    category_name = str(category_name).replace('-', ' ')

    # Get product categories and category_id
    categories = get_product_category_without_box()
    category_id = get_category_id_by_name(category_name, categories)

    depot_id = get_current_user_depot_id()
    depot_name = get_depot_name_by_id(depot_id)
    # Get all product infos
    products, total = get_all_products(page_num, item_num_per_page, depot_name, category_id, None, category_name, filter_out_boxes=True)

    # Calculate total pages
    total_pages = (total + item_num_per_page - 1) // item_num_per_page
    return render_template("local_manager_view_products.html", products=products, page=page_num, total_pages=total_pages, 
                           categories=categories, current_category=category_name, depot_name=depot_name, box_id=box_id,
                           box_contents=box_contents)


@local_manager.route("/add_to_box/<product_id>", methods=["GET"])
def add_to_box(product_id):
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    if 'box_id' not in session:
        flash('Please create a box first!', 'danger')
        return redirect(url_for('local_manager.create_box'))
      
    try:
        quantity = request.args.get('quantity', default=1, type=int) 

        if product_id and quantity and request.method == "GET":

            # Prepare the item to add/update in the session
            DictItems = {str(product_id): quantity}

            # Check if 'box_contents' is already in the session
            if 'box_contents' in session:
                # If the product_id is already in 'box_contents', update its quantity
                if str(product_id) in session['box_contents']:
                    session['box_contents'][str(product_id)] += quantity
                else:
                    # If the product_id is not in 'box_contents', add it
                    session['box_contents'].update(DictItems)
            else:
                # If 'box_contents' is not in the session, create it and add the item
                session['box_contents'] = DictItems

            # ensures that the session is saved after any updates.
            session.modified = True

        # Redirect to the referrer page
        flash("Item added successfully!", "success")
        return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@local_manager.route('/review_box')
def review_box():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    if 'box_id' not in session:
        flash('Please create a box first!', 'danger')
        return redirect(url_for('local_manager.create_box'))
      
    if 'box_contents' not in session or not session['box_contents']:
        flash("Invalid action! Back to dashboard", "danger")
        return redirect(url_for('local_manager.dashboard'))
    
    box_contents = session['box_contents']
    product_ids = list(box_contents.keys())
    products = get_products_by_ids(product_ids)

    total_weight = 0
    # Add quantity back to the list
    enhanced_results = []
    for product in products:
        product_id = str(product[0])
        quantity = box_contents[product_id]
        product_enhanced = product + (quantity,)
        enhanced_results.append(product_enhanced)
        total_weight += quantity * float(product[3])

    return render_template('local_manager_review_box_content.html', box_items=enhanced_results, total_weight=total_weight)


@local_manager.route('/confirm_box', methods=['GET', 'POST'])
def confirm_box():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    box_id = request.args.get('box_id')
    box_id_from_session = False

    # Validate box_id from session if not provided in request args
    if not box_id:
        box_id = session.get('box_id')
        box_id_from_session = True

    if not box_id:
        flash('Please create a box first!', 'danger')
        return redirect(url_for('local_manager.create_box'))

    try:
        # Retrieve the updated quantities from the form data
        box_contents = {
            key.split('_')[1]: int(value)
            for key, value in request.form.items()
            if key.startswith('quantity_')
        }

        # Save each item in the box to the database
        for product_id, quantity in box_contents.items():
            update_box_with_product_id(box_id, product_id, quantity)
        
        if box_id_from_session:
            set_box_and_its_product_active(box_id)
            # Clear the box contents from the session
            session.pop('box_contents', None)
            session.pop('box_id', None)
            session.modified = True

        flash('Box contents have been successfully confirmed and saved.', 'success')
        return redirect(url_for('local_manager.view_box', box_id=box_id))

    except Exception as e:
        flash(f'An error occurred while confirming the box: {str(e)}', 'danger')
        return redirect(url_for('local_manager.dashboard'))


@local_manager.route('/clear_box')
def clear_box():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    box_id = request.args.get('box_id')
    box_id_from_session = False

    # Validate box_id from session if not provided in request args
    if not box_id:
        box_id = session.get('box_id')
        box_id_from_session = True

    if not box_id:
        flash('Please create a box first!', 'danger')
        return redirect(url_for('local_manager.create_box'))
    
    if box_id_from_session:
        # Delete the inactive box and product
        box_id = session['box_id']
        delete_inactive_product_box(box_id)
        session.pop('box_contents', None)
        session.pop('box_id', None)
    else:
        delete_all_box_content_by_box_id(box_id)


    flash('All items have been cleared from the box!', 'success')
    return redirect(url_for('local_manager.dashboard'))


@local_manager.route('/delete_box_item/<int:item_id>')
def delete_box_item(item_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Attempt to remove the item from the session
    try:
        box_contents = session.get('box_contents', {})
        if str(item_id) in box_contents:
            del box_contents[str(item_id)]
            session['box_contents'] = box_contents  # Update the session
            session.modified = True
            flash('Item successfully removed from the box.', 'success')
        else:
            flash('Item not found in the box.', 'danger')
    except Exception as e:
        flash(f'An error occurred while deleting the item: {str(e)}', 'danger')

    return redirect(url_for('local_manager.review_box'))


@local_manager.route('/view_requests', methods=['GET'])
def view_requests():
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    depot_id = get_current_user_depot_id()
    requests = get_pending_requests(depot_id)
    return render_template('local_manager_view_requests.html', requests=requests)


@local_manager.route('/view_request_details/<int:request_id>', methods=['GET'])
def view_request_details(request_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    request = get_request_details(request_id)
    
    if request is None:
        flash("Request not found.", "danger")
        return redirect(url_for('local_manager.view_requests'))
    
    return render_template('local_manager_view_request_details.html', request=request)


@local_manager.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):
    action = request.form['action']
    message_content = request.form['message']
    
    # get user_id from account_holder
    user_id = get_user_id_from_account_holder(request_id)
    if user_id is None:
        flash("Error fetching user ID.", "danger")
        return redirect(url_for('local_manager.view_request_details', request_id=request_id))
    
    if action == 'approve':
        credit_limit = request.form['credit_limit']
        
        # Validate that the credit limit is a positive number
        try:
            credit_limit = float(credit_limit)
            if credit_limit <= 0:
                raise ValueError("Credit limit must be a positive amount.")
        except ValueError as e:
            flash(f"Invalid credit limit: {str(e)}", "danger")
            return redirect(url_for('local_manager.view_request_details', request_id=request_id))
        
        # Get credit account ID
        credit_account_id = get_credit_limit(credit_limit)
        
        if credit_account_id is None:
            flash("Error creating credit account.", "danger")
            return redirect(url_for('local_manager.view_request_details', request_id=request_id))
        
        # Update account_holder with credit account ID
        update_account_holder(request_id, credit_account_id)
        
        # Update role ID to "Credit Account Holder" (role_id = 2)
        update_user_role(user_id, 2)
        
        # Get user name
        user_name = get_user_full_name(user_id)
        if user_name is None:
            flash("Error fetching user name.", "danger")
            return redirect(url_for('local_manager.view_request_details', request_id=request_id))
        
        flash(f"{user_name}'s account holder application has been approved.", "success")
    
    elif action == 'reject':
        user_name = reject_request(request_id)
        
        if user_name is None:
            flash("Error fetching user name.", "danger")
            return redirect(url_for('local_manager.view_request_details', request_id=request_id))
        
        flash(f"{user_name}'s account holder application has been rejected.", "danger")
    
    # Send message
    send_message(11, user_id, message_content, 1)
    
    return redirect(url_for('local_manager.view_requests'))


@local_manager.route('/reply_message/<int:message_id>', methods=["GET", "POST"])
def reply_message(message_id):

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = ReplyMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            message_content = form.message_content.data
            message_category = request.form.get('message_category')
            sender_id = request.form.get('sender_id')

            send_message(session['user_id'], sender_id, message_content, message_category, session['user_depot'])

            #delete_message_by_id(message_id)
            #update status of message as Processes - 4
            update_message_by_id(message_id, 4)

            flash("Your message has been sent successfully", "success")
            return redirect(url_for('local_manager.getMessages'))

    message = get_message_by_id(message_id)
    
    return render_template('local_manager_reply_message.html', form=form, message=message)

@local_manager.route('/view_boxes')
def view_boxes():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Get all boxes from db for this week
    depot_id = get_current_user_depot_id()
    boxes = get_all_weekly_boxes(depot_id)
    return render_template('local_manager_view_boxes.html', boxes=boxes)


@local_manager.route('/view_box/<int:box_id>')
def view_box(box_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    box_product_id = request.args.get('box_product_id')
    if not box_product_id:
        box_product_name = get_box_product_name_by_box_id(box_id)
    else:
        box_product_name = get_box_product_name_by_product_id(box_product_id)

    # Get box content 
    box_details = get_box_details_by_id(box_id)

    # Calculate the total weight
    total_weight = 0
    for detail in box_details:
        total_weight += detail[3] * detail[5]  # detail[3] is weight, detail[5] is quantity

    return render_template('local_manager_view_a_box.html', box_id=box_id, box_details=box_details, box_product_name=box_product_name, total_weight=total_weight)


@local_manager.route('/delete_box/<int:box_id>')
def delete_box(box_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    set_box_product_to_inactive(box_id)
    flash('The box is deleted successfully!', 'success')
    return redirect(url_for('local_manager.dashboard'))


@local_manager.route('/delete_box_detail/<int:item_product_id>')
def delete_box_detail(item_product_id):
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    box_id = request.args.get('box_id')
    if not box_id:
        flash("Oops! Something went wrong.", "danger")
        return redirect(url_for('local_manager.dashboard'))
    
    delete_single_content_from_box(item_product_id, box_id)
    flash('Item successfully removed from the box.', 'success')
    return redirect(url_for('local_manager.view_box', box_id=box_id))


@local_manager.route("/add_to_existing_box/<product_id>", methods=["GET"])
def add_to_existing_box(product_id):
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    try:
        quantity = request.args.get('quantity', default=1, type=int)
        box_id = request.args.get('box_id', type=int)

        if product_id and quantity and box_id and request.method == "GET":
            update_box_with_product_id(box_id, product_id, quantity)
            flash("Item has been successfully added to the box.", "success")

        # Redirect to the referrer page
        return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)
