from flask import Blueprint, render_template, session, flash, request, redirect, url_for, make_response
from fhd.utilities import flash_form_errors, check_auth, get_user_full_name, get_all_messages_by_user_id, delete_message_by_id, get_user_depot_id
from fhd.utilities import get_account_holder_info_by_userid, apply_limit_increase_to_db, get_current_credit_limit, get_current_credit_balance
from fhd.utilities import send_message, check_remaining_credit_low, get_user_by_email, get_depot_name_by_id, update_account_holder_current_balance
from fhd.utilities import get_order_receipts, update_payment, modify_order_by_id, create_order, insert_payment, update_account_holder_balance_after_payment
from fhd.utilities import get_user_id_from_account_holder, get_current_user_id, get_credit_limit, get_payment_history_by_user_id, get_payment_due_date
from fhd.main.routes import view_products
from fhd.customer.routes import add_item, get_cart, update_cart, delete_item, calculate_cart, confirm_payment, view_receipt_pdf, generate_pdf_for_user
from fhd.customer.routes import view_orders_func, view_order_func, cancel_order_func,save_edited_order_func, generate_pdf_from_db, generate_invoice, generate_invoice_db
from fhd.utilities import get_customer_subscription, credit_limit_request_exists_check
from fhd.account_holder.forms import ApplyLimitIncreaseForm
from datetime import datetime, timedelta, date
from markupsafe import Markup
import pdfkit
from calendar import monthrange
from fhd.account_holder.forms import AddSubscriptionForm, sendMessageForm
from decimal import Decimal
from fhd.utilities import get_customer_shipping_fee, get_customer_subscription, get_gst_rate, retrieve_subscription,activate_subscription
from fhd.utilities import create_subscription, get_box_price_by_box_size_id, get_subscription_details_by_invoice_id, cancel_customer_subscription


# Global variable to control demo mode
DEMO_MODE = False


account_holder = Blueprint("account_holder", __name__, template_folder="templates")

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

# region functions


def check_is_account_holder():
    # This function checks if the user is an account holder.
    return check_auth(2)


def view_invoice_html(invoice_id):
    # Generate the necessary invoice details from the database using the invoice_id.
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
    
    # Get the user_id from the session.
    user_id = session.get('user_id')
    
    # Retrieve the account holder information using the user_id.
    account_holder_info = get_account_holder_info_by_userid(user_id)

    # Create a dictionary to store account holder information in a structured format.
    account_holder_info_dict = {
        'account_holder_id': account_holder_info[0],
        'business_name': account_holder_info[1],
        'business_address': account_holder_info[2],
        'business_phone': account_holder_info[3],
        'user_id': account_holder_info[4],
        'credit_account_id': account_holder_info[5],
        'credit_limit': account_holder_info[6],
        'depot_id': account_holder_info[7]
    }

    # Render the HTML template 'invoice.html' with the provided order and account holder information.
    rendered_html = render_template('invoice.html', 
                                depot_name=depot_name,
                                depot_addr=depot_addr, 
                                user_addr=user_addr,
                                invoice=invoice_num, date_issued=date_issued,
                                customer_name=customer_name, 
                                account_holder_info=account_holder_info_dict,
                                order_details=order_details,
                                grand_total=grand_total,
                                gst=gst,invoice_id=invoice_id,shipping_fee=shipping_fee)  
    
    # Return the rendered HTML.
    return rendered_html



def view_invoice_pdf(invoice_id):
    # Generate the necessary invoice details from the database using the invoice_id.
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
    
    # Get the user_id from the session.
    user_id = session.get('user_id')
    
    # Retrieve the account holder information using the user_id.
    account_holder_info = get_account_holder_info_by_userid(user_id)

    # Create a dictionary to store account holder information in a structured format.
    account_holder_info_dict = {
        'account_holder_id': account_holder_info[0],
        'business_name': account_holder_info[1],
        'business_address': account_holder_info[2],
        'business_phone': account_holder_info[3],
        'user_id': account_holder_info[4],
        'credit_account_id': account_holder_info[5],
        'credit_limit': account_holder_info[6],
        'depot_id': account_holder_info[7]
    }

    # Render the HTML template 'invoice_pdf.html' with the provided order and account holder information.
    rendered_html = render_template('invoice_pdf.html',
                                    depot_name=depot_name,
                                    depot_addr=depot_addr, 
                                    user_addr=user_addr,
                                    invoice=invoice_num, date_issued=date_issued,
                                    customer_name=customer_name,
                                    account_holder_info=account_holder_info_dict,
                                    order_details=order_details,
                                    grand_total=grand_total,
                                    gst=gst,shipping_fee=shipping_fee)

    # Convert the rendered HTML to a PDF using pdfkit.
    pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)

    # Create a response with the PDF content.
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Receipt_{invoice_num}.pdf'

    # Return the response containing the PDF.
    return response



def is_last_day_of_month(date):

    if DEMO_MODE:
        return True  # For demo purposes, always return True
    
    # Calculate the date of the next day.
    next_day = date + timedelta(days=1)
    
    # If the next day's month is different from the current day's month,
    # it means the current day is the last day of the month.
    return next_day.month != date.month


# endregion


# region routes

@account_holder.route("/dashboard")
def dashboard():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Get user_id available in session
    user_id = session.get('user_id')
    name = get_user_full_name(user_id)

    # Check for low remaining credit
    if check_remaining_credit_low():
        flash(Markup('Warning: Your remaining credit for this month is low! <a href="' + url_for('account_holder.view_credit_limit') + '">Click here to check.</a>'), 'danger')


    account_balance = get_current_credit_balance(user_id)
    # Get today's date
    today = datetime.now().date()

    # Check if today is the last day of the month
    if is_last_day_of_month(today):
        # if account holder is owing money, send a payment request message
        if account_balance != 0:
            message_content = Markup(f'Dear {name},<br><br>'
                                     f'Your account is due for payment. Your current balance is ${account_balance}.<br><br>'
                                     f'You can view your invoices <a href="{url_for("account_holder.view_invoices")}">here</a>. '
                                     f'Please make a payment at your earliest convenience <a href="{url_for("account_holder.account_holder_confirm_payment")}">here</a>.<br><br>Thank you.')
            flash(message_content, 'danger')

        # if account holder is not owing money, send a message to acknowledge that
        else:
            message_content = Markup(f'Dear {name},<br><br>'
                                     f'Your account is balanced. Thank you for shopping with us.<br><br>'
                                     f'We look forward to serving you again.')
            flash(message_content, 'success')
        
    return render_template("account_holder_dashboard.html", name=name)



#  This function handles the route for retrieving messages for the account holder.
@account_holder.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Retrieve all messages for the authenticated user
    messages = get_all_messages_by_user_id()
    
    return render_template('account_holder_messages_list.html', messages=messages)


#  This function handles the route for deleting a specific message for the account holder.
@account_holder.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Delete the message with the specified ID
    delete_message_by_id(message_id)

    # Retrieve the updated list of messages for the authenticated user
    messages = get_all_messages_by_user_id()

    flash("Your message has been deleted.", "success")
    return render_template('account_holder_messages_list.html', messages=messages)


# This function handles the route for applying for a credit limit increase for the account holder.
@account_holder.route('/apply_limit_increase', methods=['GET','POST'])
def apply_limit_increase():
        
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    form = ApplyLimitIncreaseForm()

    # get account holder info: business name, address, phone, current account limit etc
    user_id = session.get('user_id')
    account_holder_info = get_account_holder_info_by_userid(user_id)

    account_holder_info_dict = {
        'account_holder_id': account_holder_info[0],
        'business_name': account_holder_info[1],
        'business_address': account_holder_info[2],
        'business_phone': account_holder_info[3],
        'user_id': account_holder_info[4],
        'credit_account_id': account_holder_info[5],
        'credit_limit': account_holder_info[6],
        'depot_id': account_holder_info[7]
    }

    if request.method == 'POST':
        if form.validate_on_submit():

            # get reason for application and requested_limit
            reason = form.reason.data
            requested_limit = form.requested_limit.data

            # Get user_id from session
            user_id = session.get('user_id')
            current_limit = get_current_credit_limit(user_id)
            depot_id = get_user_depot_id(user_id)

            requested_date = datetime.now().strftime('%Y-%m-%d')


            # Check if there is already a pending request
            request_exists = credit_limit_request_exists_check(user_id)

            if request_exists:
                flash("Your application is pending, please do not resubmit a new application", "danger")
                return redirect(url_for('account_holder.apply_limit_increase'))


            # insert into database
            apply_limit_increase_to_db(user_id, depot_id, current_limit, reason, requested_limit, requested_date)

            # Send a notification message to the manager
            send_message(user_id, 4, "Dear manager, There is a new Credit Limit Increase Application awaiting your approval.", 1)
                
            flash("Your credit limit increase request has been submitted successfully", "success")

            return redirect(url_for('account_holder.dashboard'))
    
     # Flash form validation errors, if any
    flash_form_errors(form)

    return render_template('apply_limit_increase.html',form=form, account_holder_info=account_holder_info_dict)


# This function handles the route for viewing the credit limit details for the account holder.
@account_holder.route('/view_credit_limit', methods=['GET','POST'])
def view_credit_limit():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Get user_id from session
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance

    # Get account holder information
    account_holder_info = get_account_holder_info_by_userid(user_id)

    account_holder_info_dict = {
        'account_holder_id': account_holder_info[0],
        'business_name': account_holder_info[1],
        'business_address': account_holder_info[2],
        'business_phone': account_holder_info[3],
        'user_id': account_holder_info[4],
        'credit_account_id': account_holder_info[5],
        'credit_limit': account_holder_info[6],
        'depot_id': account_holder_info[7]
    }

    # Render the template with the credit limit details and account holder information
    return render_template('view_credit_limit.html', current_limit=current_limit, current_balance=current_balance, remaining_credit=remaining_credit, account_holder_info=account_holder_info_dict)


# Route to view products in the depot associated with the logged-in account holder.
@account_holder.route("/view_depot_products", methods=["GET", "POST"])
def view_depot_products():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    email = session['user_email']
    customer = get_user_by_email(email)
    # Get depot name using the last element of customer details
    depot_name = get_depot_name_by_id(customer[-1])

    return view_products(depot_name)


# Route to add an item to the cart for the logged-in account holder.
@account_holder.route("/additem/<product_id>", methods=["GET"])
def addItem(product_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Add the specified item to the cart
    return add_item(product_id)


# Route to retrieve the cart for the logged-in account holder.
@account_holder.route('/cart')
def getCart():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Retrieve and return the cart contents
    return get_cart()


# Route to update the cart for the logged-in account holder.
@account_holder.route('/updatecart/<int:product_id>', methods=['POST'])
def updatecart(product_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Update the cart with the specified product
    return update_cart(product_id)


# Route to delete an item from the cart for the logged-in account holder.
@account_holder.route('/deleteitem/<int:id>')
def deleteitem(id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
     # Delete the specified item from the cart
    return delete_item(id)


# Route to clear the cart for the logged-in account holder.
@account_holder.route('/clearcart')
def clearcart():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    try:
         # Clear the shopping cart from session
        session.pop('shoppingcart', None)
        return redirect(url_for('account_holder.view_depot_products'))
    except Exception as e:
        print(e)
        # Redirect to getCart route in case of error
        return redirect(url_for('account_holder.getCart'))


# Route to handle the checkout process for the logged-in account holder.
@account_holder.route('/checkout')
def checkout():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

     # Calculate cart details
    grandtotal, cart_items, tax, shipping_fee, checkout_cart_items= calculate_cart()
    # Store checkout cart items in session
    session['cart_items'] = checkout_cart_items

    # We can clear shopping cart in the session once checkout button is clicked
    session.pop('shoppingcart', None)

    #  calculate remaining credit with user id
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance

    # Check if remaining credit is sufficient for the purchase
    if remaining_credit < float(grandtotal):
        flash("You don't have enough credit to make the purchase!", "danger")
        return redirect(url_for('account_holder.dashboard'))
    
    else:
        # Update current balance with the purchase amount
        current_balance = float(current_balance) + float(grandtotal)
        current_balance = round(current_balance, 2)
        update_account_holder_current_balance(current_balance, user_id)

        # Get the current date
        payment_date = datetime.now().strftime('%Y-%m-%d')

         # Create order, payment, and invoice
        order_hdr_id = create_order(grandtotal, cart_items,session['user_id'],"order")
        payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date)

        #  Activates the subscription if applicable.
        if session.get('user_box_subscription_id') is not None:
            activate_subscription(session.get('user_box_subscription_id'))
            send_message(11, user_id, "Great news! Your subscription is now active. Head over to 'Manage My Subscription' to explore your options.", 1)

        # Generate/Update the invoice
        invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

        # Render the payment confirmation modal with the success message
        return render_template('payment_confirmation_modal.html',invoice_id=invoice_id)



# Route to view the receipt for a specific invoice ID for the logged-in account holder.
@account_holder.route('/view_receipt/<invoice_id>', methods=['GET'])
def view_receipt(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Gets the user's current account balance with user_id
    user_id = session.get('user_id')
    account_balance = get_current_credit_balance(user_id)

    # view the receipt on an HTML page
    return view_receipt_pdf(invoice_id, account_balance)


# Route to generate a PDF receipt for a specific invoice ID for the logged-in account holder.
@account_holder.route('/generate_pdf/<invoice_id>', methods=['GET'])
def generate_pdf(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Gets the user's current account balance with user_id
    user_id = session.get('user_id')
    account_balance = get_current_credit_balance(user_id)

    # generate a PDF receipt for user and automatically download it to their local machine
    return generate_pdf_for_user(invoice_id, account_balance)


# Route to view orders for the logged-in account holder.
@account_holder.route('/view_orders')
def view_orders():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Display orders associated with the logged-in account holder
    return view_orders_func()


# Route to view a specific order for the logged-in account holder.
@account_holder.route('/view_order/<int:order_id>')
def view_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

     # Display details of the specified order
    return view_order_func(order_id)


# Route to cancel a specific order for the logged-in account holder.
@account_holder.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Cancel the specified order
    return cancel_order_func(order_id)


# Route to save edited order details for the logged-in account holder.
@account_holder.route('/save_edited_order/<int:order_id>', methods=['GET', 'POST'])
def save_edited_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Retrieve edited order details from the form
    payment_amount_diff = request.form.get('calculated_amount_diff')
    grandtotal = request.form.get('calculated_grandtotal')
    tax = request.form.get('calculated_tax')
    shipping_fee = request.form.get('shipping_fee')
    
    #  calculate remaining credit with user id
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance

    # Check if remaining credit is sufficient for the purchase
    if remaining_credit < float(payment_amount_diff):
        flash("You don't have enough credit to make the purchase!", "danger")
        return redirect(url_for('account_holder.dashboard'))
    
    else:
        # Update current blance  with the purchase amount
        current_balance = float(current_balance) + float(payment_amount_diff)
        current_balance = round(current_balance, 2)
        update_account_holder_current_balance(current_balance, user_id)


         # Save edited order details
        grandtotal, order_id, tax, payment_amount_diff, shipping_fee = save_edited_order_func(order_id)
        orderitems = session.pop('modifiedItems', None)
        
        if(orderitems):
            # Get the current date
            payment_date = datetime.now().strftime('%Y-%m-%d')

            #Update payment, order
            payment_id = update_payment(order_id, grandtotal, payment_date)
            modify_order_by_id(orderitems, order_id, grandtotal)

            # Generate/Update the invoice
            invoice_id = generate_invoice(order_id, payment_id, grandtotal, tax, shipping_fee)

            # Render the payment confirmation modal with the success message
            return render_template('payment_confirmation_modal.html',invoice_id=invoice_id)
        
        else:
            flash("Something went wrong. Please contact your local manager.", "danger")
            return redirect(url_for('account_holder.dashboard'))



# Route to view invoices for the logged-in account holder.
@account_holder.route('/view_invoices')
def view_invoices():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Retrieve invoices (order receipts)
    orders = get_order_receipts()
    # Get current month and year
    current_month_year = datetime.now().strftime('%B %Y')

    return render_template('account_holder_view_invoices.html', orders=orders, current_month_year=current_month_year)



# Route to view a specific invoice for the logged-in account holder.
@account_holder.route('/view_invoice/<invoice_id>', methods=['GET'])
def view_invoice(invoice_id):
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Display HTML view of the specified invoice
    return view_invoice_html(invoice_id)


# Route to generate a PDF invoice for the logged-in account holder.
@account_holder.route('/view_invoice_pdf/<invoice_id>', methods=['GET'])
def generate_pdf_invoice(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Generate PDF view of the specified invoice, automatically download into local machine
    return view_invoice_pdf(invoice_id)


# Route to confirm payment for the logged-in account holder.
@account_holder.route('/account_holder_confirm_payment', methods=['GET', 'POST'])
def account_holder_confirm_payment():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Get current user ID
    user_id = get_current_user_id()
    
    # get account holder info with user_id
    account_holder_info = get_account_holder_info_by_userid(user_id)

    account_holder_info_dict = {
        'account_holder_id': account_holder_info[0],
        'business_name': account_holder_info[1],
        'business_address': account_holder_info[2],
        'business_phone': account_holder_info[3],
        'user_id': account_holder_info[4],
        'credit_account_id': account_holder_info[5],
        'credit_limit': account_holder_info[6],
        'depot_id': account_holder_info[7]
    }

    # Get payment due date
    payment_due_date = get_payment_due_date() 


    if request.method == 'POST':
        try:
            amount = float(request.form['payment_amount'])
            if amount < 0.01:
                raise ValueError("Amount must be at least $0.01")
            # Redirect to payment route
            return redirect(url_for('account_holder.account_holder_payment', amount=amount))
        
        except (KeyError, ValueError):
            flash("Invalid payment amount. Please enter a valid amount of at least $0.01.", "danger")
            return redirect(url_for('account_holder.account_holder_confirm_payment'))

    else:
        # If request method is GET
        # calculate remaining credit
        current_balance = get_current_credit_balance(user_id)
        current_limit = account_holder_info_dict['credit_limit'] 
        remaining_credit = current_limit - current_balance

        return render_template('account_holder_confirm_payment.html', current_limit=current_limit, current_balance=current_balance, remaining_credit=remaining_credit, account_holder_info=account_holder_info_dict, payment_due_date=payment_due_date)


# Route to process payment for the logged-in account holder.
@account_holder.route('/account_holder_payment/<float:amount>', methods=['GET', 'POST'])
def account_holder_payment(amount):
    # Check authentication and authorization
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Get current user ID
    user_id = get_current_user_id()

    if request.method == 'POST':
        try:
            # Update account holder balance after payment
            update_account_holder_balance_after_payment(amount, user_id)
            # Send payment received message and Display success message
            send_message(11, user_id, f"Your payment of ${amount:.2f} has been received.", 1)
            flash("Thank you very much for your payment. Your balance has been successfully updated", "success")
            return redirect(url_for('account_holder.account_holder_confirm_payment'))
        
        except Exception as e:
            # Display error message and redirect to payment page in case of payment failure
            flash("Payment error. Please contact your local manager for further assistance.", "danger")
            return redirect(url_for('account_holder.account_holder_payment', amount=amount))
 
    # Render payment page with specified amount
    return render_template('account_holder_payment.html', amount=amount)


# Route to view subscriptions for the logged-in account holder.
@account_holder.route('/view_subscription')
def view_subscription():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Retrieve customer subscriptions
    subscriptions = get_customer_subscription()

    return render_template('account_holder_view_subscription.html', subscriptions=subscriptions)


# Route to add a new subscription for the logged-in account holder.
@account_holder.route('/add_new_subscription', methods=['GET','POST'])
def add_new_subscription():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Retrieve form for adding a new subscription
    form = AddSubscriptionForm()

    if request.method == 'POST' and form.validate_on_submit():
        # If request method is POST and form is validated
        # get all the data from form
        box_frequency = form.box_frequency.data
        box_category = form.box_category.data
        box_size = form.box_size.data
        subscription_quantity = form.subscription_quantity.data
        confirmation = request.form['confirmation']

        # calculate price, shipping fee, tax, grand total
        price = Decimal(get_box_price_by_box_size_id(box_size)) * int(subscription_quantity)
        shipping_fee = Decimal(get_customer_shipping_fee()) * int(subscription_quantity)
        price += Decimal(shipping_fee)
        gst_rate = get_gst_rate() / 100
        tax = ("%.2f" % (gst_rate * float(price)))
        grandtotal = "%.2f" % float(price)

        if confirmation != "True":
           confirmation_message = "${} will be deducted from your credit. Are you sure you want to proceed?".format(grandtotal)
           return render_template('account_holder_new_subscription.html', form=form, confirmation_message=confirmation_message, confirmation="True")

        # Create subscription
        user_box_subscription_id = create_subscription(box_frequency, box_category, box_size, subscription_quantity)


        # calculate remaining credit with user_id
        user_id = session.get('user_id')
        current_limit = get_current_credit_limit(user_id)
        current_balance = get_current_credit_balance(user_id)
        remaining_credit = current_limit - current_balance
        cart_items = None

        # Check if the user has enough credit for the purchase
        if remaining_credit < float(grandtotal):
            flash("You don't have enough credit to make the purchase!", "danger")
            return render_template('account_holder_new_subscription.html', form=form)
        
        else:
            # Update current balance
            current_balance = float(current_balance) + float(grandtotal)
            current_balance = round(current_balance, 2)
            update_account_holder_current_balance(current_balance, user_id)

            # Get the current date
            payment_date = datetime.now().strftime('%Y-%m-%d')

            # Create order and payment for the subscription
            order_hdr_id = create_order(grandtotal, cart_items,session['user_id'],"subscription_payment")
            payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date)

            # Activate the subscription and  Send confirmation message
            activate_subscription(user_box_subscription_id)
            send_message(11, user_id, "Great news! Your subscription is now active. Head over to 'Manage My Subscription' to explore your options.", 1)

            # Generate/Update the invoice
            invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

            # Render the payment confirmation modal with the success message
            return render_template('payment_confirmation_modal.html',invoice_id=invoice_id,subscription=True)
        
     # Flash form errors if any
    flash_form_errors(form)

    return render_template('account_holder_new_subscription.html', form=form)



# Route to cancel a subscription for the logged-in account holder.
@account_holder.route('/acc_holder_cancel_subscription/<int:user_box_subscription_id>')
def acc_holder_cancel_subscription(user_box_subscription_id):
        
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    # Retrieve subscription details
    order_hdr_id, invoice_num, payment_id, box_size, quantity_sent = retrieve_subscription(user_box_subscription_id)

    # Calculate price, shipping fee, tax, grand total, subtotal
    price = Decimal(get_box_price_by_box_size_id(box_size)) * int(quantity_sent)
    shipping_fee = Decimal(get_customer_shipping_fee()) * int(quantity_sent)
    price += Decimal(shipping_fee)
    gst_rate = get_gst_rate() / 100
    tax = ("%.2f" % (gst_rate * float(price)))
    grandtotal = "%.2f" % float(price)
    subtotal = float(grandtotal) - float(tax) - float(shipping_fee)

    # Get payment date
    payment_date = datetime.now().strftime('%Y-%m-%d')
    user_id = session.get('user_id')


    # Update payment, Generate/update invoice
    update_payment(order_hdr_id, grandtotal, payment_date)
    generate_invoice_db(invoice_num, order_hdr_id, payment_id, subtotal, tax, grandtotal, shipping_fee)

    # Cancel customer subscription and calculate refund amount
    refund_amount = cancel_customer_subscription(user_box_subscription_id, grandtotal)

    # Update account holder balance after payment with refund amount
    update_account_holder_balance_after_payment(refund_amount, user_id)

    flash(f"Your subscription has been cancelled. The refund amount of ${refund_amount:.2f} is credited back into your account.", "success")
    
    # Retrieve updated customer subscriptions
    subscriptions = get_customer_subscription()

    return render_template('account_holder_view_subscription.html', subscriptions=subscriptions)


# Route to send a message for the logged-in account holder.
@account_holder.route('/acc_holder_send_message', methods=['GET','POST'])
def acc_holder_send_message():
        
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    form = sendMessageForm()

    if request.method == 'POST':
        if form.validate_on_submit():
             # Get message category, message content from the form
            message_category = form.message_category.data
            message_content = form.message_content.data

            # Send the message to the specified recipient
            send_message(session['user_id'], 3, message_content, message_category, session['user_depot'])
    
            flash("Your message has been sent successfully", "success")
            return redirect(url_for('account_holder.getMessages'))
    
    # Flash form errors if any
    flash_form_errors(form)

    return render_template('account_holder_new_message.html',form=form)


# Route to create a new message for the logged-in account holder.
@account_holder.route('/new_message')
def new_message():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    # Retrieve form for composing a new message
    form = sendMessageForm()

    return render_template('account_holder_new_message.html', form=form)

# endregion