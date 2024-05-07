from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from fhd.utilities import flash_form_errors, check_auth, get_basic_product_info_by_id

customer = Blueprint("customer", __name__, template_folder="templates")

# region functions
def check_is_customer():
    # Need to pass in the correct user_role to check_auth function
    # return check_auth()
    pass

def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

# endregion

# region routes
@customer.route("/example", methods=["GET", "POST"])
def example():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    pass


@customer.route("/additem", methods=["POST"])
def addItem():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

        product = get_basic_product_info_by_id(product_id)

        if product_id and quantity and request.method == "POST":
            DictItems = {product_id:{'name':product[0], 'price': product[1], 'quantity': quantity, 'image': product[2]}}

            if 'Shoppingcart' in session:
                if product_id in session['shoppingcart']:
                    for key, item in session['shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
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
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('home'))
    
    subtotal = 0
    grandtotal = 0

    for key, product in session['shoppingcart'].items():
        subtotal += float(product['price']) * int(product['quantity'])
    
    tax = ("%.2f" % (.15 * float(subtotal)))
    grandtotal = float("%.2f" % (1.15 * subtotal)) 
    
    return render_template('cart.html', tax=tax, grandtotal=grandtotal)

@customer.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
            flash('Item is updated')
            return redirect(url_for('customer.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('customer.getCart'))
        
@customer.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('home'))
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
    try:
        session.pop('shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
        return redirect(url_for('customer.getCart'))


# endregion


