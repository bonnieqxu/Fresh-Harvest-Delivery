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
from fhd.utilities import get_credit_limit_increase_requests, get_box_category_name_by_id, get_box_category_by_id
from fhd.utilities import get_all_active_subscription, get_full_product_info_by_id, get_customer_shipping_fee, get_gst_rate, get_account_holder_details
from fhd.utilities import get_outstanding_balances_for_depot,get_current_user_id, update_product_quantity, log_perished_product_removal, get_perished_product_logs
from fhd.utilities import generate_months_list, get_credit_limit_increase_request_info, get_credit_account_id, update_credit_limit_after_processing_request, approve_credit_limit_request
from fhd.utilities import reject_credit_limit_request, get_user_id_from_credit_limit_request, cancel_order_by_id, get_discontinued_products
from fhd.utilities import get_account_holders_by_depot, update_credit_limit, get_account_holder_current_credit_balance, update_account_holder_balance 
from fhd.utilities import can_edit_box_items, get_customer_subscription_details, get_box_size_name_by_id
from fhd.local_manager.forms import AddProductTypeForm, SearchProductTypeForm, EditProductTypeForm, ViewProductForm, EditProductForm
from fhd.local_manager.forms import UpdateOrderStatusForm, AddBoxForm, ReplyMessageForm
from datetime import datetime, timedelta
from markupsafe import Markup
import random
from fhd.utilities import create_order, insert_payment, generate_invoice_db, update_subscription_quantity, get_all_active_subscription_display

local_manager = Blueprint("local_manager", __name__, template_folder="templates")

# region functions

def check_is_local_manager():
    # Checks if the current user is a local manager.
    return check_auth(4)


def get_category_id_by_name(category_name, categories):
    # Gets the category ID by its name from a list of categories.
    # Returns: The ID of the category if found, otherwise None.
    for category_id, name in categories:
        if name == category_name:
            return category_id
    return None


# Generates an invoice. returns the ID of the generated invoice in the database.
def generate_invoice(order_hdr_id, payment_id, grandtotal, tax_str, shipping_fee):
    # Fixed prefix for NZ style invoice number
    prefix = "NZ"

    # Generate a random 6-digit number
    random_number = random.randint(100000, 999999)

    # Combine prefix, year_month, and random number to create the invoice number
    invoice_number = f"{prefix}-{random_number}"

    # Convert the string inputs to floats
    # calculate grand total, tax, subtotal
    grand_total = float(grandtotal)
    tax = float(tax_str)
    subtotal = grand_total - tax - float(shipping_fee)

    # Generate invoice in the database
    invoice_id = generate_invoice_db(invoice_number, order_hdr_id, payment_id,
                   round(subtotal, 2), tax, grandtotal, shipping_fee)
    
    return invoice_id



def is_order_due(last_order_date, subscription_type):
    # Function determines if an order is due based on the last order date and subscription type.
    # If there is no last order date, it assumes it's the first order and returns True.
    # Depending on the subscription type, it checks if enough days have passed since the last order.

    if last_order_date is None:
        return True  # First order, so it's due
    today = datetime.now().date()
    # Convert last_order_date to a string before using strptime
    last_order_date_str = last_order_date.strftime("%Y-%m-%d")
    last_order_date = datetime.strptime(last_order_date_str, "%Y-%m-%d")

    if subscription_type == "1":
        # For weekly subscription, check if 7 days have passed since the last order
        return (today - last_order_date).days >= 7
    elif subscription_type == "2":
        # For fortnightly subscription, check if 14 days have passed since the last order
        return (today - last_order_date).days >= 14
    elif subscription_type == "3":
        # For monthly subscription, check if the current month is different from the last order month
        return today.month != last_order_date.month  


def create_box_func():
    # Function to handle the creation of a new box. This includes processing form data,
    # uploading an image, and adding entries to various tables in the database.
    form = AddBoxForm()
    if request.method == 'POST' and form.validate_on_submit():
         # Retrieve data from the form
        box_name = form.box_name.data
        box_unit = form.box_unit.data
        box_size = form.box_size.data
        box_category_id = form.box_category.data
        box_description = form.box_description.data
        box_stock = form.box_stock.data

         # Handle box image upload
        box_image = request.files.getlist('box_image')
        if len(box_image) == 0 or (len(box_image) == 1 and box_image[0].filename == ''):
            flash("Box image is required!", "danger")
            return render_template("local_manager_create_box.html", form=form)
        else:
            image_data = box_image[0].read()
        
        box_size_name = get_box_size_name_by_id(box_size)

        box_name = box_name + ' -' + box_size_name
        # Add a new product type, product and box, set product and box is_active = 0 for now
        product_type_id = add_new_product_type(image_data, box_name, box_unit, box_description, 7)
        depot_id = get_current_user_depot_id()
        if str(session['user_role_id']) == "5" and form.box_depot.data:
            depot_id = form.box_depot.data
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

         # Add a new box with the calculated current week's Sunday date
        box_id = add_new_box(product_id, box_size, today, current_week_sunday, box_category_id, 0)
        session['box_id'] = box_id
        session['box_category_id'] = box_category_id

         # Redirect based on user role
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.add_box_content'))
        else:
            return redirect(url_for('national_manager.add_box_content'))

    # Flash form errors if any and render the form again
    flash_form_errors(form)
    return render_template("local_manager_create_box.html", form=form)



def add_box_content_func(category_name):
    # Function to handle adding content to a box. It manages sessions, retrieves products,
    # and prepares data for rendering the product view template.

    box_id = request.args.get('box_id')
    if not box_id:
        box_id = None

     # Ensure there is a box in the session or via query string
    if 'box_id' not in session and box_id is None:
        flash('Please create a box first!', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.create_box'))
        else:
            return redirect(url_for('national_manager.create_box'))
    
    # Initialize box_contents as an empty dictionary
    box_contents = {}

    # When add to box button is clicked
    if 'box_id' in session and 'box_contents' in session:
        box_contents = session['box_contents']

    # When create a new box, we have it in the session until box if confirmed
    if 'box_category_id' in session:
        box_category_id = session['box_category_id']

    # box_id is passed in, meaning it's from edit box
    if box_id is not None:
        box_contents = get_box_product_quantity_by_id(box_id)
        box_category_id = get_box_category_by_id(box_id)

    # Get the page number from the query string
    page_num = request.args.get('page', 1, type=int)
    item_num_per_page = 11

    # Replace '-' back to ' '
    category_name = str(category_name).replace('-', ' ')

    # Get box category name
    box_category_name = get_box_category_name_by_id(box_category_id)
    if box_category_name == "Mixed":
        box_category_name = "All"

    # Get product categories and category_id
    categories = get_product_category_without_box()

    # Filter categories to only include the box category name
    if box_category_name and box_category_name != "All":
        categories = [category for category in categories if category[1] == box_category_name]
        # When box category is not All, we want to show box_category_name for the title
        category_name = box_category_name

     # Get category_id for the current category name
    category_id = get_category_id_by_name(category_name, categories)

    # Get current user's depot id and name
    depot_id = get_current_user_depot_id()
    depot_name = get_depot_name_by_id(depot_id)

    # Get all product infos
    products, total = get_all_products(page_num, item_num_per_page, depot_name, category_id, None, category_name, filter_out_boxes=True)

    # Calculate total pages
    total_pages = (total + item_num_per_page - 1) // item_num_per_page
    
    # Render the product view template with the relevant data
    return render_template("local_manager_view_products.html", products=products, page=page_num, total_pages=total_pages, 
                           categories=categories, current_category=category_name, depot_name=depot_name, box_id=box_id,
                           box_contents=box_contents)



 # Function to add a product to the box. It manages sessions and updates the box contents.
def add_to_box_func(product_id):
    if 'box_id' not in session:
         # Ensure there is a box in the session
        flash('Please create a box first!', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.create_box'))
        else:
            return redirect(url_for('national_manager.create_box'))
      
    try:
        # Get the quantity from the request arguments, defaulting to 1 if not provided
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
        # Print any exception that occurs
        print(e)
    finally:
        # Always redirect to the referrer page
        return redirect(request.referrer)



def review_box_func():
    # Function to review the contents of the box. It checks for the presence of a box and its contents in the session,
    # retrieves product details, calculates total weight, and renders the review template.

    if 'box_id' not in session:
         # Ensure there is a box in the session
        flash('Please create a box first!', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.create_box'))
        else:
            return redirect(url_for('national_manager.create_box'))
      
    if 'box_contents' not in session or not session['box_contents']:
         # Ensure there are contents in the box
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.dashboard'))
        else:
            return redirect(url_for('national_manager.dashboard'))
      
    
    # Retrieve box contents from the session
    box_contents = session['box_contents']
    product_ids = list(box_contents.keys())
    products = get_products_by_ids(product_ids)

    total_weight = 0
    # Add quantity back to the list
    enhanced_results = []

    # Add quantity back to the list and calculate the total weight
    for product in products:
        product_id = str(product[0])
        quantity = box_contents[product_id]
        product.append(quantity)
        enhanced_results.append(product)
        total_weight += quantity * float(product[3])

    return render_template('local_manager_review_box_content.html', box_items=enhanced_results, total_weight=total_weight)



def confirm_box_func():
    # Function to confirm the contents of a box. It retrieves the box ID, validates and updates quantities,
    # saves the contents to the database, and clears session data if necessary.

    box_id = request.args.get('box_id')
    box_id_from_session = False

    # Validate box_id from session if not provided in request args
    if not box_id:
        box_id = session.get('box_id')
        box_id_from_session = True

    if not box_id:
         # Ensure there is a box in the session or provided in the request
        flash('Please create a box first!', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.create_box'))
        else:
            return redirect(url_for('national_manager.create_box'))

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
            # Set the box and its products as active
            set_box_and_its_product_active(box_id)

            # Clear the box contents from the session
            session.pop('box_contents', None)
            session.pop('box_id', None)
            session.pop('box_category_id', None)
            session.modified = True

        # Flash a success message and redirect based on user role
        flash('Box contents have been successfully confirmed and saved.', 'success')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.view_box', box_id=box_id))
        else:
            return redirect(url_for('national_manager.view_box', box_id=box_id))       

    except Exception as e:
        # Flash an error message and redirect to the dashboard if an exception occurs
        flash(f'An error occurred while confirming the box: {str(e)}', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.dashboard'))
        else:
             return redirect(url_for('national_manager.dashboard'))



def clear_box_func():
    # Function to clear the contents of a box. It validates the box ID, either from the session or request arguments,
    # and deletes the box contents or the box itself if necessary.

    box_id = request.args.get('box_id')
    box_id_from_session = False

    # Validate box_id from session if not provided in request args
    if not box_id:
        box_id = session.get('box_id')
        box_id_from_session = True

    if not box_id:
        # Ensure there is a box in the session or provided in the request
        flash('Please create a box first!', 'danger')
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.create_box'))
        else:
            return redirect(url_for('national_manager.create_box'))
    
    if box_id_from_session:
        # Delete the inactive box and product
        box_id = session['box_id']
        delete_inactive_product_box(box_id)
        session.pop('box_contents', None)
        session.pop('box_id', None)
    else:
         # Delete all box contents by box ID if the box ID is provided in the request
        delete_all_box_content_by_box_id(box_id)

     # Flash a success message and redirect based on user role
    flash('All items have been cleared from the box!', 'success')
    if str(session['user_role_id']) == '4':
        return redirect(url_for('local_manager.dashboard'))
    else:
        return redirect(url_for('national_manager.dashboard'))




def delete_box_item_func(item_id):
    # Function to delete an item from the box contents in the session.
    try:
        # Attempt to remove the item from the session
        box_contents = session.get('box_contents', {})
        if str(item_id) in box_contents:
            del box_contents[str(item_id)]
            session['box_contents'] = box_contents  # Update the session
            session.modified = True
            flash('Item successfully removed from the box.', 'success')
        else:
            flash('Item not found in the box.', 'danger')
    except Exception as e:
        # Handle any exceptions that occur during deletion
        flash(f'An error occurred while deleting the item: {str(e)}', 'danger')

    # Redirect based on user role
    if str(session['user_role_id']) == '4':
        return redirect(url_for('local_manager.review_box'))
    else:
        return redirect(url_for('national_manager.review_box'))



# Function to retrieve and display all boxes for the current week.
def view_boxes_func():
    # Get all boxes from db for this week
    depot_id = get_current_user_depot_id()

     # If the user is a national manager, set depot_id to None to fetch boxes across all depots
    if str(session['user_role_id']) == '5':
        depot_id = None

    # Retrieve all weekly boxes for the specified depot or all depots if depot_id is None
    boxes = get_all_weekly_boxes(depot_id)

    return render_template('local_manager_view_boxes.html', boxes=boxes)



# Function to view the details of a specific box.
def view_box_func(box_id):
     # Retrieve the optional box_product_id from the request arguments
    box_product_id = request.args.get('box_product_id')

    if not box_product_id:
         # If box_product_id is not provided, get the box product name using box_id
        box_product_name = get_box_product_name_by_box_id(box_id)
    else:
         # If box_product_id is provided, get the box product name using that ID
        box_product_name = get_box_product_name_by_product_id(box_product_id)

    # Get box content 
    box_details = get_box_details_by_id(box_id)

    # Cannot clear box content if there are orders associated with the box
    can_edit_box = can_edit_box_items(box_id)

    # Calculate the total weight
    total_weight = 0
    for detail in box_details:
        total_weight += detail[3] * detail[5]  # detail[3] is weight, detail[5] is quantity

    return render_template('local_manager_view_a_box.html', box_id=box_id, box_details=box_details, 
                           box_product_name=box_product_name, total_weight=total_weight, can_edit_box=can_edit_box)


# Function to delete a box by setting its products to inactive.
def delete_box_func(box_id):
    # Set the box and its products to inactive in the database
    set_box_product_to_inactive(box_id)

    # Flash a success message
    flash('The box is deleted successfully!', 'success')

     # Redirect based on user role
    if str(session['user_role_id']) == '4':
        return redirect(url_for('local_manager.dashboard'))
    else:
        return redirect(url_for('national_manager.dashboard'))



 # Function to delete a specific item from a box.
def delete_box_detail_func(item_product_id):
    # Retrieve the box_id from the request arguments
    box_id = request.args.get('box_id')

    # Ensure that box_id is provided
    if not box_id:
        flash("Oops! Something went wrong.", "danger")
        if str(session['user_role_id']) == '4':
            return redirect(url_for('local_manager.dashboard'))
        else:
            return redirect(url_for('national_manager.dashboard'))
    
    # Delete the specified item from the box
    delete_single_content_from_box(item_product_id, box_id)

    # Flash a success message
    flash('Item successfully removed from the box.', 'success')

    # Redirect based on user role
    if str(session['user_role_id']) == '4':
        return redirect(url_for('local_manager.view_box', box_id=box_id))
    else:
        return redirect(url_for('national_manager.view_box', box_id=box_id))




def add_to_existing_box_func(product_id):
    # Function to add an item to an existing box
    # It retrieves the quantity and box ID from the request arguments.
    # Then, it updates the box with the specified product and quantity.

    try:
        # Attempt to get the quantity and box_id from the request arguments
        quantity = request.args.get('quantity', default=1, type=int)
        box_id = request.args.get('box_id', type=int)

        # Check if all required parameters are provided and the request method is GET
        if product_id and quantity and box_id and request.method == "GET":
            # Update the box with the specified product and quantity
            update_box_with_product_id(box_id, product_id, quantity)
            flash("Item has been successfully added to the box.", "success")

        # Redirect to the referrer page
        return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        # Always redirect to the referrer page
        return redirect(request.referrer)
    

# endregion


# region routes



# Route to add a new product type.
# It checks authentication and authorization of the user.
# Then, it handles form submission to add a new product type.
@local_manager.route("/add_product_type", methods=["GET", "POST"])
def add_product_type():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Initialize form for adding product type
    form = AddProductTypeForm()

    
    if form.validate_on_submit():
        # Retrieve product images from request
        images = request.files.getlist('product_image')
        
        # Read image data
        image_data = images[0].read()

        # Retrieve product information from form data
        product_name = form.product_name.data
        product_unit = form.product_unit.data
        product_description = form.product_description.data
        product_category = form.product_category.data

        # Check if product type with the same name already exists
        if get_product_type_by_name(product_name):
            flash("Product type name already exist", "danger")
            return render_template("add_product_type.html", form=form)

        # Add new product type to the database
        add_new_product_type(image_data, product_name, product_unit, product_description, product_category)
        flash("Product type created successfully", "success")
        return search_product_type()
    
    # Display form errors if any
    flash_form_errors(form)

    return render_template("add_product_type.html", form=form)




@local_manager.route("/search_product_type", methods=["GET","POST"])
def search_product_type():
    # Route to search for product types.
    # It checks authentication and authorization of the user.
    # Then, it handles form submission and requests to search for product types.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Initialize search form
    form = SearchProductTypeForm()
    
    # Initialize variables
    product_name = None
    product_category = None
    page_num = request.args.get('page', 1, type=int)

    if request.method == 'POST' and form.validate_on_submit():
        # Retrieve search parameters from form submission
        product_name = form.product_name.data
        product_category = form.product_category.data

    if request.method == 'GET':
        # Retrieve search parameters from URL query string
        product_name = request.args.get('product_name')
        if product_name == '':
            product_name = None  # Set to None if empty string

        product_category = request.args.get('product_category')
        if product_category == '':
            product_category = None  # Set to None if empty string

    # Number of items to display per page
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
    # Route to edit a product type.
    # It checks authentication and authorization of the user.
    # Then, it handles form submission to update a product type.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
 
    # Initialize edit form
    form = EditProductTypeForm()

    # Retrieve product type information by ID
    product = get_product_type_by_id(product_type_id)
    if not product:
        # Redirect if product type is not found
        flash('Product Type not found!', 'danger')
        return redirect(url_for('local_manager.search_product_type'))
 
    # When user clicks on submit button
    if form.validate_on_submit():

        # Retrieve product images from request
        images = request.files.getlist('product_image')

        # Read image data
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

    # Prefill form fields with existing product type information
    form.product_name.data = product[1]
    form.product_unit.data = str(product[4])
    form.product_description.data = product[3]
    form.product_category.data = str(product[5])
 
    # Display form errors if any
    flash_form_errors(form)

    return render_template("edit_product_type.html", form=form, product_type_id=product_type_id, product_image=product[2])


@local_manager.route("/delete_product_type/<product_type_id>", methods=["GET", "POST"])
def delete_product_type(product_type_id):
    # Route to delete a product type.
    # It checks authentication and authorization of the user.
    # Then, it deletes the specified product type.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Delete product type by ID
    delete_product_type_by_id(product_type_id)
 
    # Return to the product type page after the successful update
    flash("Product Type deleted successfully.", "success")

    return search_product_type()


@local_manager.route("/dashboard")
def dashboard():
    # Route to display the dashboard for local managers.
    # It checks authentication and authorization of the user.
    # Then, it retrieves relevant information to display on the dashboard.

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
    # Retrieve user's full name
    name = get_user_full_name(user_id)

    # Clear these if user click on dashboard while in the process of creating a box
    # Delete the inactive box and product
    box_id = session.pop('box_id', None)
    if box_id is not None:
        delete_inactive_product_box(box_id)
    session.pop('box_contents', None)

    return render_template("local_manager_dashboard.html", name=name)


@local_manager.route('/getMessages')
def getMessages():
    # Route to fetch messages for the local manager.
    # It checks authentication and authorization of the user.
    # Then, it retrieves all messages associated with the user.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve all messages associated with the user
    messages = get_all_messages_by_user_id()
    
    return render_template('local_manager_messages_list.html', messages=messages)


@local_manager.route('/delete_message/<int:message_id>')
def delete_message(message_id):     
    # Route to delete a message by its ID.
    # It checks authentication and authorization of the user.
    # Then, it deletes the specified message.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Delete message by its ID
    delete_message_by_id(message_id)

    # Retrieve all messages associated with the user
    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")

    return render_template('account_holder_messages_list.html', messages=messages)


@local_manager.route('/local_manager_product_list/<int:depot_id>', methods=["GET", "POST"])
def local_manager_product_list(depot_id):
    # Route to display the list of products for a specific depot managed by the local manager.
    # It checks authentication and authorization of the user.
    # Then, it retrieves and displays the products associated with the specified depot.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = ViewProductForm()

    # Retrieve page number from URL query string, default is 1
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Define the number of items per page
    
    # Retrieve status filter from URL query string
    status_filter = request.args.get('status', '')
    
    # Retrieve products associated with the specified depot
    products, total_products = get_products_by_user_depot(depot_id, page, per_page, status_filter)
    
    return render_template('local_manager_product_list.html', form=form, products=products, depot_id=depot_id, page=page, per_page=per_page, total_products=total_products)


@local_manager.route("/local_manager_edit_product/<int:product_id>", methods=["GET", "POST"])
def local_manager_edit_product(product_id):
    # Route to edit product details for the local manager.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to edit product details.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    form = EditProductForm()
    # Retrieve product details for editing
    product = edit_product(product_id)

    if request.method == 'POST' and form.validate_on_submit():
        # Update product details based on form data
        new_price = form.product_price.data
        new_quantity = form.product_quantity.data
        
        # Check if the 'Discontinued' checkbox was checked
        is_discontinued = 'discontinued' in request.form

        # Perform database update using the new function
        update_product(product_id, new_price, new_quantity, is_discontinued)

        # Display success message
        flash('Product updated successfully!', 'success')

        return redirect(url_for('local_manager.local_manager_edit_product', product_id=product_id))

    # Pre-fill form fields with existing product data
    if product:
        form.product_price.data = product[2]
        form.product_quantity.data = product[3]

    return render_template('local_manager_edit_product.html', form=form, product=product, product_id=product_id)



@local_manager.route('/update_order_status/<int:depot_orderid>', methods=['GET', 'POST'])
def update_order_status(depot_orderid):
    # Route to update the status of an order by depot order ID.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to update the status of the order.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Initialize form for updating order status
    form = UpdateOrderStatusForm()
    # Set choices for order status
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        # Retrieve selected status ID from form
        status_id = form.status.data
        # Update order status in database
        update_order_status_by_depot_orderid(depot_orderid, status_id)
        # Retrieve order header ID and user ID associated with the order
        order_hdr_id, user_id = get_order_hdr_and_user_id(depot_orderid)

        if status_id == "3" or status_id == 3: #when the order is shipped
            send_message(11, user_id, "Great news! Your order #{} has been successfully shipped and is now on its way to you. Get ready to receive your items soon! Should you have any questions or need further assistance, feel free to reach out. We're here to help. Happy shopping!".format(order_hdr_id), 1)
    
        if status_id == "5" or status_id == 5: #when the order is cancelled
            # cancel the order
            cancel_order_by_id(order_hdr_id)

        # Display success message
        flash(f"Order {order_hdr_id} status updated successfully.", "success")
        return redirect(url_for('local_manager.update_order_statuses'))

    # Retrieve depot ID of the current user and all orders associated with the depot
    depot_id = get_current_user_depot_id()
    orders = get_all_orders(depot_id)

    return render_template('local_manager_update_order_status.html', orders=orders, form=form)


@local_manager.route('/update_order_statuses', methods=['GET'])
def update_order_statuses():
    # Route to update statuses of multiple orders.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to update statuses of orders.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Initialize form for updating order status
    form = UpdateOrderStatusForm()
    # Retrieve all order statuses
    all_order_status = get_status_choices()

    # Retrieve depot ID of the current user
    depot_id = get_current_user_depot_id()
    # Get the selected status from the query parameters
    selected_status = request.args.get('status')
    
    # Retrieve all orders associated with the depot, with optional status filtering
    orders = get_all_orders(depot_id, status_id=selected_status)

    # Initialize list to store orders with updated status information
    list_orders = []
    for order in orders:
        list_order = list(order)
        # We only get the status which is greater than the current status
        order_status = [status for status in all_order_status if status[0] >= int(order[6])]
        # Append the status at the end of the list as this is for each order
        list_order.append(order_status)
        list_orders.append(list_order)

    return render_template('local_manager_update_order_status.html', orders=list_orders, form=form, all_order_status=all_order_status)



@local_manager.route('/view_order_details/<int:order_hdr_id>/<int:depot_order_id>', methods=['GET', 'POST'])
def view_order_details(order_hdr_id, depot_order_id):
    # Route to view details of a specific order.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view and update details of the order.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Initialize form for updating order status
    form = UpdateOrderStatusForm()
    # Set choices for order status
    form.status.choices = get_status_choices()

    if request.method == 'POST' and form.validate_on_submit():
        # Retrieve selected status ID from form
        status_id = form.status.data
        # Update order status in database
        update_order_status_by_depot_orderid(depot_order_id, status_id)
        flash(f"Order {depot_order_id} status updated successfully.", "success")

        return redirect(url_for('local_manager.update_order_statuses'))
    
    # Retrieve order details
    order_details = get_order_details(order_hdr_id)
    # Retrieve customer information associated with the order
    customer_info = get_customer_info(order_hdr_id)

    return render_template('local_manager_view_order_details.html', order_details=order_details, customer_info=customer_info, form=form, depot_order_id=depot_order_id, order_hdr_id=order_hdr_id)


@local_manager.route('/create_box', methods=['GET', 'POST'])
def create_box():
    # Route to create a new box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to create a new box.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to create a box
    return create_box_func()


@local_manager.route('/add_box_content/')
@local_manager.route('/add_box_content/', defaults={'category_name': 'All'})
@local_manager.route('/add_box_content/<category_name>/')
def add_box_content(category_name="All"):
    # Route to add contents to a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to add contents to a box.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to add box content
    return add_box_content_func(category_name)



@local_manager.route("/add_to_box/<product_id>", methods=["GET"])
def add_to_box(product_id):
    # Route to add a product to a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to add a product to a box.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to add product to box
    return add_to_box_func(product_id)



@local_manager.route('/review_box')
def review_box():
    # Route to review the contents of a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to review the contents of a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to review box contents
    return review_box_func()



@local_manager.route('/confirm_box', methods=['GET', 'POST'])
def confirm_box():
    # Route to confirm the contents of a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to confirm the contents of a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to confirm box contents
    return confirm_box_func()


@local_manager.route('/clear_box')
def clear_box():
    # Route to clear the contents of a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to clear the contents of a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to clear box contents
    return clear_box_func()


@local_manager.route('/delete_box_item/<int:item_id>')
def delete_box_item(item_id):
    # Route to delete an item from a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to delete an item from a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to delete box item
    return delete_box_item_func(item_id)


@local_manager.route('/view_requests', methods=['GET'])
def view_requests():
    # Route to view pending requests.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view pending requests.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve depot ID of the current user
    depot_id = get_current_user_depot_id()
    # Retrieve pending requests associated with the depot
    requests = get_pending_requests(depot_id)

    return render_template('local_manager_view_requests.html', requests=requests)



@local_manager.route('/view_request_details/<int:request_id>', methods=['GET'])
def view_request_details(request_id):
    # Route to view details of a specific request.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view details of the request.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Retrieve details of the request by ID
    request = get_request_details(request_id)
    
    if request is None:
        # Display error message if request is not found
        flash("Request not found.", "danger")

        return redirect(url_for('local_manager.view_requests'))
    
    return render_template('local_manager_view_request_details.html', request=request)




@local_manager.route('/handle_request/<int:request_id>', methods=['POST'])
def handle_request(request_id):

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    # Handle approval or rejection of a request.
    
    # Extract action and message content from form
    action = request.form['action']
    message_content = request.form['message']
    
    # get user_id from account_holder
    user_id = get_user_id_from_account_holder(request_id)
    if user_id is None:
        flash("Error fetching user ID.", "danger")
        return redirect(url_for('local_manager.view_request_details', request_id=request_id))
    
    if action == 'approve':
        # If action is approval, retrieve and validate credit limit
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
        # If action is rejection, reject request
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
    # Route to reply to a message.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to reply to a message.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Initialize form for replying to message
    form = ReplyMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Retrieve message content, category, original message, and sender ID from form
            message_content = form.message_content.data
            message_category = request.form.get('message_category')
            original_message = request.form.get('original_message')
            sender_id = request.form.get('sender_id')

            # Append original message to the reply content
            message_content = f"{message_content}\n=====\n{original_message}\n=====\n"

            # Send the reply message
            send_message(session['user_id'], sender_id, message_content, message_category, session['user_depot'])

            
            #update status of message as Processes - 4
            update_message_by_id(message_id, 4)

            flash("Your message has been sent successfully", "success")
            return redirect(url_for('local_manager.getMessages'))

    # Retrieve message details by ID
    message = get_message_by_id(message_id)
    
    return render_template('local_manager_reply_message.html', form=form, message=message)




@local_manager.route('/view_boxes')
def view_boxes():
    # Route to view boxes.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view boxes.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to view boxes
    return view_boxes_func()


@local_manager.route('/view_box/<int:box_id>')
def view_box(box_id):
    # Route to view details of a specific box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view details of a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to view box details
    return view_box_func(box_id)
 


@local_manager.route('/delete_box/<int:box_id>')
def delete_box(box_id):
    # Route to delete a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to delete a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to delete box
    return delete_box_func(box_id)



@local_manager.route('/delete_box_detail/<int:item_product_id>')
def delete_box_detail(item_product_id):
    # Route to delete a detail from a box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to delete a detail from a box.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to delete box detail
    return delete_box_detail_func(item_product_id)



@local_manager.route("/add_to_existing_box/<product_id>", methods=["GET"])
def add_to_existing_box(product_id):
    # Route to add a product to an existing box.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to add a product to an existing box.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Call function to add product to existing box
    return add_to_existing_box_func(product_id)



@local_manager.route('/view_credit_limit_increase_requests', methods=['GET'])
def view_credit_limit_increase_requests():
    # Route to view credit limit increase requests.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view credit limit increase requests.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve current user's depot ID
    depot_id = get_current_user_depot_id()

    # Get credit limit increase requests for the current depot
    requests = get_credit_limit_increase_requests(depot_id=depot_id)

    return render_template('lm_credit_limit_increase_list.html', requests=requests)



@local_manager.route('/view_credit_limit_increase_request/<int:request_id>', methods=['GET'])
def view_credit_limit_increase_request(request_id):
    # Route to view details of a credit limit increase request.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to view details of a credit limit increase request.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Get information of the credit limit increase request
    request_info = get_credit_limit_increase_request_info(request_id)

    return render_template('lm_credit_limit_increase_details.html', request_info=request_info)



@local_manager.route('/handle_credit_limit_request/<int:request_id>', methods=['POST'])
def handle_credit_limit_request(request_id):
     # Route to handle a credit limit increase request.
    # It checks authentication and authorization of the user.
    # Then, it allows the local manager to approve or reject a credit limit increase request.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Get action, message content, credit limit, and requested limit from the form
    action = request.form['action']
    message_content = request.form['message']
    credit_limit = request.form.get('credit_limit', type=int)
    requested_limit = request.form['requested_limit']

    # get user_id and credit_account_id and user name
    user_id = get_user_id_from_credit_limit_request(request_id)

    credit_account_id = get_credit_account_id(user_id)

    user_name = get_user_full_name(user_id)
    

    # Handle different actions
    if action == 'approve_same':
        # if approving the requested amount
        new_limit = requested_limit
        # update credit_account table
        update_credit_limit_after_processing_request(new_limit, credit_account_id)
        # update credit_limit_change_request table
        approve_credit_limit_request(new_limit, request_id)

        # Flash message for approval
        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been approved,<br><br>"
                            f'The new credit limit is ${new_limit}.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'success')


    elif action == 'approve_diff' and credit_limit is not None:
        # if approving a different amount
        new_limit = credit_limit
        # update credit_account table
        update_credit_limit_after_processing_request(new_limit, credit_account_id)
        # update credit_limit_change_request table
        approve_credit_limit_request(new_limit, request_id)

        # Flash message for approval with different limit
        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been approved,<br><br>"
                            f'The new credit limit is ${new_limit}.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'success')

    # if decline the request
    elif action == 'reject':
        # update credit_limit_change_request table
        reject_credit_limit_request(request_id)

        # Flash message for rejection
        flash_message = Markup(f"{user_name}'s Credit Limit Increase Application has been declined,<br><br>"
                            f'The credit limit remains the same as before.<br><br>'
                            f'Your message has been sent to {user_name}.')
        flash(flash_message, 'warning')
    
    # Send message
    send_message(11, user_id, message_content, 1)
    
    return redirect(url_for('local_manager.view_credit_limit_increase_requests'))




@local_manager.route('/view_trigger_list', methods=['GET'])
def view_trigger_list():
    # Route to view trigger list, which includes due subscriptions and customer subscriptions.
    # It checks authentication and authorization of the user.
    # Then, it retrieves and displays the trigger list for the local manager.

    # Check authentication and authorization    
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

     # Get the depot ID from the session
    depot_id = session['user_depot']
    # Get all active subscriptions
    subscriptions = get_all_active_subscription_display(depot_id)

    # Filter subscriptions that are due
    due_subscriptions = [subscription for subscription in subscriptions if is_order_due(subscription[-1], subscription[-2])]

    if not subscriptions:
        no_boxes_available_to_trigger = True
    else:
        no_boxes_available_to_trigger = False

    # Get details of customer subscriptions
    customer_subscriptions = get_customer_subscription_details(depot_id)

    return render_template('local_manager_trigger_list.html', subscriptions=due_subscriptions, 
                           no_boxes_available_to_trigger=no_boxes_available_to_trigger, customer_subscriptions=customer_subscriptions)



@local_manager.route('/create_subcription_orders', methods=["POST"])
def create_subcription_orders():
    # Route to create subscription orders for due subscriptions.
    # It checks authentication and authorization of the user.
    # Then, it creates orders for subscriptions that are due for the local manager.

    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response
    
    # Get the GST rate
    gst_rate = get_gst_rate() / 100
    
    # Get the depot ID, current date for payment
    depot_id = session['user_depot']
    payment_date = datetime.now().strftime('%Y-%m-%d')
    # Get all active subscriptions for the depot
    subscriptions = get_all_active_subscription(depot_id)


    # Iterate over each subscription
    for subscription in subscriptions:
        checkout_cart_items = {}    # Initialize checkout cart items
        subtotal = 0    # Initialize subtotal for the order

        # Check if quantity of order to be placed is greater than 0 and if the order is due
        if int(subscription[5]) > 0 and is_order_due(subscription[8], subscription[2]): #quantity of order to be placed
             # Extract necessary information from subscription
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

             # Get shipping fee and update subtotal
            shipping_fee = get_customer_shipping_fee(subscription[0])
            subtotal += float(shipping_fee)
            # Calculate tax and grand total
            tax = ("%.2f" % (gst_rate * float(subtotal)))
            grandtotal = "%.2f" % float(subtotal)

            # Create order header
            order_hdr_id = create_order(grandtotal, checkout_cart_items, user_id, "subscription_order")
            # Insert payment
            payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date,user_id)
            # Generate invoice
            invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

            send_message(11, user_id, "Your order #{} is confirmed. We know you are eager to receive your new purchase and we will do our best to process your order as soon as possible.".format(order_hdr_id), 1)

            # Update subscription quantity
            update_subscription_quantity(subscription[1])

    # Flash success message and redirect to trigger list view
    flash('Subscription orders triggered successfully!', 'success')

    return redirect(url_for('local_manager.view_trigger_list'))



@local_manager.route('/view_outstanding_balances')
def view_outstanding_balances():
    # Route to view outstanding balances for the current user's depot.
    # It checks authentication and authorization of the user.
    # Then, it retrieves outstanding balances for the user's depot.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Get the current user's ID and their associated depot ID
    user_id = get_current_user_id()
    depot_id = session['user_depot']

    # Retrieve outstanding balances for the user's depot   
    outstanding_balances = get_outstanding_balances_for_depot(depot_id)
    
    return render_template('local_manager_view_outstanding_balances.html', outstanding_balances=outstanding_balances)



@local_manager.route('/view_balance_details/<int:account_holder_id>', methods=['GET', 'POST'])
def view_balance_details(account_holder_id):
    # Route to view balance details for a specific account holder.
    # It checks authentication and authorization of the user.
    # It also allows filtering by month.
    # It retrieves account holder details and purchase records for the selected month.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve selected month from request arguments
    selected_month = request.args.get('month', default=None, type=str)

    # Retrieve account holder details and purchase records for the selected month
    account_holder_details, purchase_records = get_account_holder_details(account_holder_id, selected_month)
    # Generate a list of months for filtering
    months = generate_months_list()
    
    # Render the template to display account holder details and purchase records
    return render_template('local_manager_view_balance_details.html', 
                           account_holder=account_holder_details, 
                           purchases=purchase_records, 
                           selected_month=selected_month, 
                           months=months,
                           account_holder_id=account_holder_id)




@local_manager.route('/update_balance/<int:account_holder_id>', methods=['GET', 'POST'])
def update_balance(account_holder_id):
    # Route to update the balance for a specific account holder.
    # It checks authentication and authorization of the user.
    # It handles both GET and POST requests.
    # For POST requests, it validates and updates the payment amount.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    if request.method == 'POST':
        # Retrieve the payment amount from the form
        payment_amount = float(request.form['payment_amount'])
        # Retrieve the current balance of the account holder
        current_balance = get_account_holder_current_credit_balance(account_holder_id)

        # Validate the payment amount
        if payment_amount > current_balance:
            flash("Payment amount cannot be greater than the current balance.", "danger")
            return redirect(url_for('local_manager.update_balance', account_holder_id=account_holder_id))

        try:
            # Update account holder balance after payment
            update_account_holder_balance (payment_amount, account_holder_id)
            # Send payment received message and display success message
            send_message(11, account_holder_id, f"Payment of ${payment_amount:.2f} received, balance updated", 1)
            
            flash("Balance has been successfully updated.", "success")

            return redirect(url_for('local_manager.view_balance_details', account_holder_id=account_holder_id))
        
        # Handle any exceptions that occur during the payment update process
        except Exception as e:
            flash("Error updating balance. Please try again.", "danger")

            return redirect(url_for('local_manager.update_balance', account_holder_id=account_holder_id))

    # If it's a GET request, render the update balance template with account holder details
    account_holder, _ = get_account_holder_details(account_holder_id)

    return render_template('local_manager_update_balance.html', account_holder=account_holder, account_holder_id=account_holder_id)



@local_manager.route("/local_manager_remove_perished_product/<int:product_id>", methods=["POST"])
def local_manager_remove_perished_product(product_id):
    # Route to remove perished products from stock.
    # It checks authentication and authorization of the user.
    # It handles POST requests to validate and update the quantity of perished products.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve the perished quantity from the form
    perished_quantity = int(request.form['perished_quantity'])

    # Fetch the current product details
    product = edit_product(product_id)
    if not product:
        flash('Product not found!', 'danger')

        return redirect(url_for('local_manager.local_manager_product_list', depot_id=session['user_depot']))

    # Retrieve the current quantity of the product
    current_quantity = product[3] 

    # Validate the perished quantity
    if perished_quantity > current_quantity:
        flash(f'Cannot remove {perished_quantity} items. Only {current_quantity} available.', 'danger')
        return redirect(url_for('local_manager.local_manager_edit_product', product_id=product_id))

    # Calculate the new quantity after removing the perished quantity
    new_quantity = max(0, current_quantity - perished_quantity)
    product_name = product[1] 

    # Update the product quantity in the database
    update_product_quantity(product_id, new_quantity)

    # Log the removal
    log_perished_product_removal(product_id, product_name, perished_quantity)

    # Display a success message and redirect to the product edit page
    flash(f'{perished_quantity} {product_name} removed from stock. Updated quantity is {new_quantity}.', 'success')
    
    return redirect(url_for('local_manager.local_manager_edit_product', product_id=product_id))




@local_manager.route("/local_manager_perished_product_log", methods=["GET"])
def local_manager_perished_product_log():
    # Route to display the log of perished products.
    # It checks authentication and authorization of the user.
    # It retrieves the logs from the database and renders the template to display them.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Get the page number from the request, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of logs per page

    # Retrieve logs and total count of logs
    logs, total_logs = get_perished_product_logs(page, per_page)
    
    # Calculate total pages for pagination
    total_pages = (total_logs + per_page - 1) // per_page

    return render_template('local_manager_perished_product_log.html', logs=logs, page=page, total_pages=total_pages)



@local_manager.route("/local_manager_discontinued_products", methods=["GET"])
def local_manager_discontinued_products():
    # Route to display discontinued products.
    # It checks authentication and authorization of the user.
    # It retrieves discontinued products from the database and renders the template to display them.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Retrieve discontinued products
    discontinued_products_list = get_discontinued_products()

    return render_template('local_manager_discontinued_products.html', discontinued_products=discontinued_products_list)



@local_manager.route('/manage_credit_limits', methods=['GET', 'POST'])
def manage_credit_limits():
    # Route to manage credit limits.
    # It checks authentication and authorization of the user.
    # It allows updating credit limits for account holders.

    # Check authentication and authorization
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    # Get the depot ID of the current user
    depot_id = session.get('user_depot')  

    # Update credit limit
    if request.method == 'POST':
        # Get the account holder ID and the new credit limit from the form
        account_holder_id = request.form.get('account_holder_id')
        new_credit_limit = request.form.get('new_credit_limit')

        # Call the function to update the credit limit
        result, business_name = update_credit_limit(account_holder_id, new_credit_limit)

        # Display a flash message based on the result of the update operation
        if result:
            flash(f"Credit limit updated successfully for {business_name}.", "success")
        else:
            flash("Failed to update credit limit. Please try again.", "danger")

        return redirect(url_for('local_manager.manage_credit_limits'))

    # Get account holders for the current depot
    account_holders = get_account_holders_by_depot(depot_id)

    if not account_holders:
        account_holders = []

    return render_template('local_manager_manage_credit_limits.html', account_holders=account_holders)