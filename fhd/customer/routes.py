
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, make_response, send_file
from fhd.utilities import check_auth, get_gst_rate, get_full_product_info_by_id, get_user_orders, get_order_details_by_id
from fhd.utilities import get_user_by_email, get_depot_name_by_id, get_user_full_name, create_order, insert_account_holder
from fhd.utilities import update_payment, get_all_messages_by_user_id, delete_message_by_id, generate_invoice_db, cancel_order_by_id
from fhd.utilities import account_holder_exists_check, get_depot_addr_by_name, get_user_addr_by_id, get_order_receipts,get_order_status_by_id
from fhd.utilities import get_invoice_date_and_num, flash_form_errors, modify_order_by_id, get_payment_diff, insert_payment, get_order_details_by_invoice_id
from fhd.utilities import send_message, get_local_manager_id_for_user_id, get_customer_shipping_fee, get_customer_subscription
from fhd.utilities import create_subscription, get_box_price_by_box_size_id, get_subscription_details_by_invoice_id, cancel_customer_subscription
from fhd.utilities import retrieve_subscription, activate_subscription
from fhd.main.routes import view_products
from datetime import datetime
import random
import pdfkit
from decimal import Decimal

from fhd.customer.forms import ApplyAccountHolderForm, sendMessageForm, AddSubscriptionForm



customer = Blueprint("customer", __name__, template_folder="templates")

# region functions
def check_is_customer():
    return check_auth(1)

def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


def calculate_cart():
    # function will calculate the grand total, tax, shipping fee, cart items
    # and return them to to caller
    subtotal = 0
    grandtotal = 0
    gst_rate = get_gst_rate() / 100
    cart_items = {}
    checkout_cart_items = {}

    for key, product in session['shoppingcart'].items():
        line_total = float(product['price']) * int(product['quantity'])
        subtotal += line_total
        # Create a new dictionary for the item with additional information
        product_info = get_full_product_info_by_id(key)
        item_info = {
            'product_id': key,
            'name': product_info[0],
            'quantity': product['quantity'],
            'price': product['price'],
            'image': product_info[2],
            'unit': str(product_info[5]) + product_info[6]
        }

        item_for_checkout_info = {
            'product_id': key,
            'name': product_info[0],
            'quantity': product['quantity'],
            'price': product['price'],
            'unit': str(product_info[5]) + product_info[6]
        }
        
        # Add the item dictionary
        cart_items[key] = {
            'item_info': item_info,
            'line_total': line_total
        }

        checkout_cart_items[key] = {
            'item_info': item_for_checkout_info,
            'line_total': line_total
        }

    shipping_fee = get_customer_shipping_fee()
    subtotal += float(shipping_fee)
    tax = ("%.2f" % (gst_rate * float(subtotal)))
    grandtotal = "%.2f" % float(subtotal)
    return grandtotal, cart_items, tax, shipping_fee, checkout_cart_items

def calculate_grandtotal_tax(updated_order_details):
    # function will calculate grandtotal, tax, shipping fee and cart items after an update to the order
    # and return them to the caller
    subtotal = 0
    grandtotal = 0
    gst_rate = get_gst_rate() / 100
    items = {}
    for product in updated_order_details:
        quantity = int(product['quantity'])
        line_total = float(product['price']) * quantity
        line_total = round(line_total, 2)
        subtotal += line_total
        # Add the item dictionary
        items[product['product_id']] = {
            'line_total': line_total,
            'quantity': quantity
        }

    shipping_fee = get_customer_shipping_fee()
    subtotal += float(shipping_fee)

    tax = ("%.2f" % (gst_rate * float(subtotal)))
    grandtotal = "%.2f" % float(subtotal)
    return grandtotal, items, tax, subtotal, shipping_fee

def get_all_item_infos(cart_items):
    all_item_infos = []
    for item in cart_items.values():
        all_item_infos.append(item['item_info'])
    return all_item_infos


def generate_invoice(order_hdr_id, payment_id, grandtotal, tax_str, shipping_fee):
    # Fixed prefix for NZ style invoice number
    prefix = "NZ"

    # Generate a random 6-digit number
    random_number = random.randint(100000, 999999)

    # Combine prefix, year_month, and random number to create the invoice number
    invoice_number = f"{prefix}-{random_number}"

    # Convert the string inputs to floats
    grand_total = float(grandtotal)
    tax = float(tax_str)
    subtotal = grand_total - tax - float(shipping_fee)
    invoice_id = generate_invoice_db(invoice_number, order_hdr_id, payment_id,
                   round(subtotal, 2), tax, grandtotal, shipping_fee)
    
    return invoice_id

# this configuration is needed to run pdfkit
# it is used to convert html to pdf (used to display receipts in pdf)
# wkhtmltopdf path
# wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration()
options = {
     'enable-local-file-access': None,
     'page-size': 'A4',
     'margin-top': '0.75in',
     'margin-right': '0.75in',
     'margin-bottom': '0.75in',
     'margin-left': '0.75in'
 }


def add_item(product_id):
    # function will add the item into the shopping cart session
    # if the product is already in the session, then the quantity will be modified
    # if the product is not in session, the product will be added into the session 
    try:

        quantity = request.args.get('quantity', default=1, type=int) 
        product = get_full_product_info_by_id(product_id)

        if product_id and quantity and request.method == "GET":
           
            DictItems = {product_id:{'quantity': quantity, 'price': product[1]}}

            if 'shoppingcart' in session:
                if product_id in session['shoppingcart']:
                    for key, item in session['shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] = quantity
                else:
                    session['shoppingcart'] = MergeDicts(session['shoppingcart'], DictItems)
            else:
                session['shoppingcart'] = DictItems
                return redirect(request.referrer)

    except Exception as e:
        print(e)

    finally:
        return redirect(request.referrer)


def get_cart():    
    #function will route the caller to cart.html aftter calculating the
    #grand total, shipping fee, tax and cart items
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return render_template('cart.html', tax=0, grandtotal=0, cart_items=None)
    
    grandtotal, cart_items, tax, shipping_fee, checkout_cart_items = calculate_cart()
    items = get_all_item_infos(cart_items)
    
    return render_template('cart.html', tax=tax, grandtotal=grandtotal, cart_items=items, shipping_fee=shipping_fee)

def update_cart(product_id):
    # function will update the quantity of the items in the cart
    # there is no adding of new items, just changing the quantity number
    # once update, the user role session value is checked and then routed accordingly
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        flash("Invalid action!", "danger")
        return redirect(url_for('main.home'))
    
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['shoppingcart'].items():
                if int(key) == product_id:
                    item['quantity'] = quantity
            flash('Cart item is updated', "success")
            if str(session['user_role_id']) == '1':
                return redirect(url_for('customer.getCart'))
            else:
                return redirect(url_for('account_holder.getCart'))
        except Exception as e:
            print(e)
            if str(session['user_role_id']) == '1':
             return redirect(url_for('customer.getCart'))
            else:
                return redirect(url_for('account_holder.getCart'))

def delete_item(id):   
    # function to delete an item based on the id parameter
    # the items in shoppingcart session will be looped to get the corresponding 
    # item then if found, it will be deleted
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        flash("Invalid action!", "danger")
        return redirect(url_for('main.home'))
    
    try:
        session.modified = True
        for key, item in session['shoppingcart'].items():
            if int(key) == id:
                session['shoppingcart'].pop(key, None)

        if str(session['user_role_id']) == '1':
            return redirect(url_for('customer.getCart'))
        else:
            return redirect(url_for('account_holder.getCart'))                
    except Exception as e:
        print(e)
        if str(session['user_role_id']) == '1':
            return redirect(url_for('customer.getCart'))
        else:
            return redirect(url_for('account_holder.getCart'))  


def confirm_payment():
    if request.method == 'POST':
        # Get the grand total
        grandtotal = request.form.get('grandtotal')
        # Get the tax
        tax = request.form.get('tax')
        # Get Shipping Fee
        shipping_fee = request.form.get('shipping_fee')

        # Get the current date
        payment_date = datetime.now().strftime('%Y-%m-%d')

        #check if payment is for subscription
        subscription = request.form.get('subscription')
        purpose = request.form.get('purpose')
        user_box_subscription_id = request.form.get('user_box_subscription_id')

        user_id = session['user_id']

        # Customer pay for the new order
        cart_items = session.pop('cart_items', None)
        if cart_items:
            # create_order(grandtotal, cart_items)
            order_hdr_id = create_order(grandtotal, cart_items, user_id, purpose)
            payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date)
            send_message(11, user_id, "Your order #{} is confirmed. We know you are eager to receive your new purchase and we will do our best to process your order as soon as possible.".format(order_hdr_id), 1)


        # if orderitems is in session which means customer pays the price for order modification
        orderitems = session.pop('modifiedItems', None)
        if(orderitems):
            order_hdr_id = request.form.get('order_hdr_id')
            payment_id = update_payment(order_hdr_id, grandtotal, payment_date)
            modify_order_by_id(orderitems, order_hdr_id, grandtotal)
        
        # if the payment is for subscription, after a successful insert payment, the 
        # user subscription will be activated (is_active = true)
        if(subscription and subscription != ""):
            order_hdr_id = create_order(grandtotal, cart_items, user_id, purpose)
            payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date)
            activate_subscription(user_box_subscription_id)
            send_message(11, user_id, "Great news! Your subscription is now active. Head over to 'Manage My Subscription' to explore your options.", 1)

        # Generate/Update the invoice
        invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

        # Render the payment confirmation modal with the success message
        return render_template('payment_confirmation_modal.html',invoice_id=invoice_id, subscription=subscription)
    else:
        flash("Something went wrong. Please contact your local manager.", "danger")
        return redirect(url_for('customer.dashboard'))


def generate_pdf_from_db(invoice_id):
    email = session['user_email']
    customer = get_user_by_email(email)
    depot_name = get_depot_name_by_id(customer[-1])
    depot_addr = get_depot_addr_by_name(depot_name)

    # Get customer name
    user_id = session.get('user_id')
    customer_name = get_user_full_name(user_id)
    user_addr = get_user_addr_by_id(user_id)

    # Get order details
    order_details = get_order_details_by_invoice_id(invoice_id)
    date_issued, invoice_num= get_invoice_date_and_num(invoice_id)

    #if order_details is empty, that means the payment was for susbscription
    if order_details is None or not order_details:
        order_details, grand_total, shipping_fee, gst = get_subscription_details_by_invoice_id(invoice_id)

    else:
        # Calculate grand total
        grand_total = sum(item['subtotal'] for item in order_details)

        shipping_fee = get_customer_shipping_fee()
        grand_total += Decimal(shipping_fee)

        # Calculate GST (15% of grand total)
        gst = grand_total * Decimal('0.15')
        gst = gst.quantize(Decimal('0.01'))

    return depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee


def view_receipt_pdf(invoice_id, account_balance=None):
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
    
    # Render HTML template with order information
    rendered_html = render_template('receipt.html', 
                                depot_name=depot_name,
                                depot_addr=depot_addr, 
                                user_addr=user_addr,
                                invoice=invoice_num, date_issued=date_issued,
                                customer_name=customer_name, 
                                order_details=order_details,
                                grand_total=grand_total,
                                gst=gst,invoice_id=invoice_id,shipping_fee=shipping_fee, account_balance=account_balance)  
    return rendered_html

def generate_pdf_for_user(invoice_id, account_balance=None):
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
    # Render HTML template with order information
    rendered_html = render_template('receipt_pdf.html',
                                    depot_name=depot_name,
                                    depot_addr=depot_addr, 
                                    user_addr=user_addr,
                                    invoice=invoice_num, date_issued=date_issued,
                                    customer_name=customer_name,
                                    order_details=order_details,
                                    grand_total=grand_total,
                                    gst=gst,shipping_fee=shipping_fee, account_balance=account_balance)
 
    pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)

    # Create response with PDF content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'

    response.headers['Content-Disposition'] = f'attachment; filename=Receipt_{invoice_num}.pdf'

    return response


def view_orders_func():
    # function to return all the customer's orders
    orders = get_user_orders()
    return render_template('customer_view_orders.html', orders=orders)


def view_order_func(order_id, payment_amount_diff=None):
    # function to return an order based on order_id parameter
    # it will also return if the order can be modified or cancelled
    order_details, invoice_info, can_modify, can_cancel = get_order_details_by_id(order_id)
    shipping_fee = get_customer_shipping_fee()
    gst_percentage = get_gst_rate()/100
    return render_template('customer_view_an_order.html', order_details=order_details, order_id=order_id, 
                           invoice_info=invoice_info, can_modify=can_modify, can_cancel=can_cancel, 
                           payment_amount_diff=payment_amount_diff, shipping_fee=shipping_fee, gst_percentage=gst_percentage)


def cancel_order_func(order_id):
    # Get order_status from db
    order_status = get_order_status_by_id(order_id)

    # Order passes confirm status
    if order_status > 1:
        user_id = session['user_id']
        user_depot_id = session['user_depot']

        send_message(user_id, 4, "Hi manager, I request to cancel my order #{}!".format(order_id), 3)
        flash("Your cancel request has been sent to the manager. Please allow 1-2 business days to get a response.", "success")
    else:
        cancel_order_by_id(order_id)
        flash("Order has been cancelled successfully! Your refund will be deposited into your account within the next 2-3 business days.", "success")

    if str(session['user_role_id']) == '1':
        return redirect(url_for('customer.view_orders'))
    else:
        return redirect(url_for('account_holder.view_orders'))
    

def save_edited_order_func(order_id):
    # Get all product IDs and their corresponding quantities from the form
    updated_order_details = []
    for key, value in request.form.items():
        if key.startswith('quantity_'):
            index = key.split('_')[1]
            quantity = value
            product_id = request.form.get(f'product_id_{index}')
            price = request.form.get(f'price_id_{index}')
            updated_order_details.append(
            {
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            })

    # Calculate the new amount
    grandtotal, modified_items, tax, subtotal, shipping_fee = calculate_grandtotal_tax(updated_order_details)

    session['modifiedItems'] = modified_items
    payment_amount_diff = get_payment_diff(grandtotal, order_id)
    payment_amount_diff = round(payment_amount_diff, 2)
    return grandtotal, order_id, tax, payment_amount_diff, shipping_fee

# endregion

# region routes
@customer.route("/dashboard")
def dashboard():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)
    return render_template("customer_dashboard.html", name=name)


@customer.route("/view_depot_products", methods=["GET", "POST"])
def view_depot_products():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    email = session['user_email']
    customer = get_user_by_email(email)
    depot_name = get_depot_name_by_id(customer[-1])
    return view_products(depot_name)


@customer.route("/additem/<product_id>", methods=["GET"])
def addItem(product_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return add_item(product_id)
    

@customer.route('/cart')
def getCart():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return get_cart()


@customer.route('/updatecart/<int:product_id>', methods=['POST'])
def updatecart(product_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return update_cart(product_id)

       
@customer.route('/deleteitem/<int:id>')
def deleteitem(id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return delete_item(id)


@customer.route('/clearcart')
def clearcart():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    try:
        session.pop('shoppingcart', None)
        return redirect(url_for('customer.view_depot_products'))
    except Exception as e:
        print(e)
        return redirect(url_for('customer.getCart'))


@customer.route('/checkout')
def checkout():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    # call calculate_cart function to calculate the grand total of the items
    # inside the shopping cart session
    grandtotal, cart_items, tax, shipping_fee, checkout_cart_items = calculate_cart()
    
    session['cart_items'] = checkout_cart_items

    # We can clear shopping cart in the session once checkout button is clicked
    session.pop('shoppingcart', None)

    return render_template('checkout.html', grandtotal=grandtotal, tax=tax, payment_amount_diff=None, shipping_fee=shipping_fee, purpose="order")


@customer.route('/payment', methods=['GET','POST'])
def payment():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return confirm_payment()


@customer.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    # return all messages back to the html
    messages = get_all_messages_by_user_id()
    
    return render_template('customer_messages_list.html', messages=messages)

@customer.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")
    return render_template('customer_messages_list.html', messages=messages)

@customer.route('/apply_account_holder', methods=['GET','POST'])
def apply_account_holder():
    
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    form = ApplyAccountHolderForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            business_name = form.business_name.data
            business_address = form.business_address.data
            business_phone = form.business_phone.data
            message = request.form.get('message')

            # first is to check if there is already a pending account holder application
            account_exists = account_holder_exists_check()

            if account_exists:
                flash("Your application is pending, please do not resubmit a new application", "warning")
                return render_template('apply_account_holder.html',form=form)

            # insert the information into account holder table
            # at the point, the customer is not an account holder yet
            insert_account_holder(business_name, business_address, business_phone)

            # sends a message to the manager's mailbox to notify of an application
            send_message(session['user_id'], 4, message, 1, session['user_depot'] )

            flash("Your application has been submitted successfully", "success")
            return render_template('apply_account_holder.html',form=form)
    
    flash_form_errors(form)

    
    return render_template('apply_account_holder.html',form=form)

@customer.route('/view_orders')
def view_orders():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    return view_orders_func()


@customer.route('/view_order/<int:order_id>')
def view_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    return view_order_func(order_id)


#view receipt
@customer.route('/view_receipt/<invoice_id>', methods=['GET'])
def view_receipt(invoice_id):
    # Check authentication and authorization
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return view_receipt_pdf(invoice_id)


# generate pdf reciept
@customer.route('/generate_pdf/<invoice_id>', methods=['GET'])
def generate_pdf(invoice_id):
    # Check authentication and authorization
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return generate_pdf_for_user(invoice_id)


@customer.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    return cancel_order_func(order_id)


@customer.route('/save_edited_order/<int:order_id>', methods=['POST'])
def save_edited_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    grandtotal, order_id, tax, payment_amount_diff, shipping_fee = save_edited_order_func(order_id)
    flash(f"To complete your order, please pay ${payment_amount_diff}.", "success")
    return render_template('checkout.html', grandtotal=grandtotal, order_hdr_id=order_id, tax=tax, 
                           payment_amount_diff=payment_amount_diff, shipping_fee=shipping_fee, purpose="order")


@customer.route('/view_receipts')
def view_receipts():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    orders = get_order_receipts()

    return render_template('customer_view_receipts.html', orders=orders)


@customer.route('/new_message')
def new_message():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    form = sendMessageForm()

    return render_template('customer_new_message.html', form=form)

@customer.route('/customer_send_message', methods=['GET','POST'])
def customer_send_message():
        
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    form = sendMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            message_category = form.message_category.data
            message_content = form.message_content.data

            # send message to the staff/local manager (3)
            send_message(session['user_id'], 3, message_content, message_category, session['user_depot'])
    
            flash("Your message has been sent successfully", "success")
            return redirect(url_for('customer.getMessages'))
    
    flash_form_errors(form)
    return render_template('customer_new_message.html',form=form)

@customer.route('/view_subscription')
def view_subscription():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    subscriptions = get_customer_subscription()

    return render_template('customer_view_subscription.html', subscriptions=subscriptions)

@customer.route('/add_new_subscription', methods=['GET','POST'])
def add_new_subscription():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    form = AddSubscriptionForm()

    if request.method == 'POST':
       if form.validate_on_submit():
        
        box_frequency = form.box_frequency.data
        box_category = form.box_category.data
        box_size = form.box_size.data
        subscription_quantity = form.subscription_quantity.data

        #insert information into the subscription table
        #at this point of time, the subscription is not active yet as payment has not been made
        user_box_subscription_id = create_subscription(box_frequency, box_category, box_size, subscription_quantity)

        #logic below calculates the grandtotal and shipping fee based on customer selection
        price = Decimal(get_box_price_by_box_size_id(box_size)) * int(subscription_quantity)
        shipping_fee = Decimal(get_customer_shipping_fee()) * int(subscription_quantity)
        price += Decimal(shipping_fee)
        gst_rate = get_gst_rate() / 100
        tax = ("%.2f" % (gst_rate * float(price)))
        grandtotal = "%.2f" % float(price)

        return render_template('checkout.html', grandtotal=grandtotal, tax=tax, payment_amount_diff=None, shipping_fee=shipping_fee, subscription=True, purpose="subscription_payment",user_box_subscription_id=user_box_subscription_id)

        
    flash_form_errors(form)
    return render_template('customer_new_subscription.html', form=form)


@customer.route('/cancel_subscription/<int:user_box_subscription_id>')
def cancel_subscription(user_box_subscription_id):
        
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    order_hdr_id, invoice_num, payment_id, box_size, quantity_sent = retrieve_subscription(user_box_subscription_id)

    price = Decimal(get_box_price_by_box_size_id(box_size)) * int(quantity_sent)
    shipping_fee = Decimal(get_customer_shipping_fee()) * int(quantity_sent)
    price += Decimal(shipping_fee)
    gst_rate = get_gst_rate() / 100
    tax = ("%.2f" % (gst_rate * float(price)))
    grandtotal = "%.2f" % float(price)
    subtotal = float(grandtotal) - float(tax) - float(shipping_fee)
    payment_date = datetime.now().strftime('%Y-%m-%d')

    #update the invoice with the order that was already delivered
    #the rest of the initial payment will be refunded to the customer
    update_payment(order_hdr_id, grandtotal, payment_date)
    generate_invoice_db(invoice_num, order_hdr_id, payment_id, subtotal, tax, grandtotal, shipping_fee)

    #call cancel subscription function to get the refund amount
    refund_amount = cancel_customer_subscription(user_box_subscription_id, grandtotal)

    flash(f"Your subscription has been cancelled. The refund amount of ${refund_amount:.2f} will be deposited into your account within the next 2-3 business days.", "success")
    subscriptions = get_customer_subscription()
    if not subscriptions:
        return redirect(url_for('customer.dashboard'))

    return render_template('customer_view_subscription.html', subscriptions=subscriptions)


# endregion