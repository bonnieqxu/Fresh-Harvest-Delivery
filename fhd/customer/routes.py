from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from fhd.utilities import flash_form_errors, check_auth, get_gst_rate, get_full_product_info_by_id
from fhd.utilities import  get_user_by_email, get_depot_name_by_id, get_user_full_name, create_order
from fhd.utilities import  insert_payment, status_confirmed, get_all_messages_by_user_id, delete_message_by_id

from fhd.main.routes import view_products
from datetime import datetime
# from fhd.customer.forms import PaymentForm

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
    subtotal = 0
    grandtotal = 0
    gst_rate = get_gst_rate() / 100
    cart_items = {}

    for key, product in session['shoppingcart'].items():
        subtotal += float(product['price']) * int(product['quantity'])
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
        # Add the item dictionary
        cart_items[key] = {
            'item_info': item_info,
            'subtotal': subtotal
        }

    tax = ("%.2f" % (gst_rate * float(subtotal)))
    grandtotal = "%.2f" % float(subtotal)
    return grandtotal, cart_items, tax


def get_all_item_infos(cart_items):
    all_item_infos = []
    for item in cart_items.values():
        all_item_infos.append(item['item_info'])
    return all_item_infos


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
    try:
        #product_id = request.form.get('product_id')
        #quantity = request.form.get('quantity')
        quantity = request.args.get('quantity', default=1, type=int) 
        product = get_full_product_info_by_id(product_id)

        if product_id and quantity and request.method == "GET":
            #DictItems = {product_id:{'name':product[0], 'price': product[1], 'quantity': quantity, 'image': product[2], 'unit': str(product[5]) + product[6]}}
            DictItems = {product_id:{'quantity': quantity, 'price': product[1]}}

            if 'shoppingcart' in session:
                if product_id in session['shoppingcart']:
                    for key, item in session['shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += quantity
                else:
                    session['shoppingcart'] = MergeDicts(session['shoppingcart'], DictItems)
            else:
                session['shoppingcart'] = DictItems
                return redirect(request.referrer)

    except Exception as e:
        print(e)

    finally:
        return redirect(request.referrer)
    
@customer.route('/cart')
def getCart():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return render_template('cart.html', tax=0, grandtotal=0, cart_items=None)
    
    grandtotal, cart_items, tax = calculate_cart()
    items = get_all_item_infos(cart_items)
    
    return render_template('cart.html', tax=tax, grandtotal=grandtotal, cart_items=items)

@customer.route('/updatecart/<int:product_id>', methods=['POST'])
def updatecart(product_id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

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
            return redirect(url_for('customer.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('customer.getCart'))
        
@customer.route('/deleteitem/<int:id>')
def deleteitem(id):
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response
    
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        flash("Invalid action!", "danger")
        return redirect(url_for('main.home'))
    
    try:
        session.modified = True
        for key, item in session['shoppingcart'].items():
            if int(key) == id:
                session['shoppingcart'].pop(key, None)
        return redirect(url_for('customer.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('customer.getCart'))

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

    grandtotal, cart_items, tax = calculate_cart()
    
    # create_order(grandtotal, cart_items)
    order_hdr_id = create_order(grandtotal, cart_items)

    return render_template('checkout.html', grandtotal=grandtotal,  order_hdr_id= order_hdr_id)


@customer.route('/payment', methods=['GET','POST'])
def payment():
    # form = PaymentForm()
    if request.method == 'POST':
        # Get the order header ID
        order_hdr_id = request.form.get('order_hdr_id')

        # Get the grand total
        grandtotal = request.form.get('grandtotal')
        
        # Get the current date
        payment_date = datetime.now().strftime('%Y-%m-%d')

        # Insert payment information into the database
        insert_payment(order_hdr_id, grandtotal, 1, payment_date)

        status_confirmed()

        # Clear the shopping cart in the session
        session.pop('shoppingcart', None)
    
        # Render the payment confirmation modal with the success message
        return render_template('payment_confirmation_modal.html')
    return render_template('checkout.html')
    
@customer.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

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

# endregion



