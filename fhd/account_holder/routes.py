from flask import Blueprint, render_template, session, flash, request, redirect, url_for, make_response
from fhd.utilities import flash_form_errors, check_auth, get_user_full_name, get_all_messages_by_user_id, delete_message_by_id, get_user_depot_id
from fhd.utilities import get_account_holder_info_by_userid, apply_limit_increase_to_db, get_current_credit_limit, get_current_credit_balance
from fhd.utilities import send_message, check_remaining_credit_low, get_user_by_email, get_depot_name_by_id, update_account_holder_current_balance
from fhd.utilities import get_order_receipts, update_payment, modify_order_by_id, create_order, insert_payment
from fhd.main.routes import view_products
from fhd.customer.routes import add_item, get_cart, update_cart, delete_item, calculate_cart, confirm_payment, view_receipt_pdf, generate_pdf_for_user
from fhd.customer.routes import view_orders_func, view_order_func, cancel_order_func,save_edited_order_func, generate_pdf_from_db, generate_invoice
from fhd.account_holder.forms import ApplyLimitIncreaseForm
from datetime import datetime, timedelta
from markupsafe import Markup
import pdfkit


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
    return check_auth(2)

def view_invoice_html(invoice_id):
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
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

    # Render HTML template with order information
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
    return rendered_html


def view_invoice_pdf(invoice_id):
    depot_name, depot_addr, user_addr, invoice_num, date_issued, customer_name, order_details, grand_total, gst, shipping_fee = generate_pdf_from_db(invoice_id)
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
 
    pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)

    # Create response with PDF content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Receipt_{invoice_num}.pdf'

    return response



def is_last_day_of_month(date):
    if DEMO_MODE:
        return True  # For demo purposes, always return True
    next_day = date + timedelta(days=1)
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
        if account_balance != 0:
            message_content = Markup(f'Dear {name},<br><br>'
                                     f'Your account is due for payment. Your current balance is ${account_balance}.<br><br>'
                                     f'You can view your invoices <a href="{url_for("account_holder.view_invoices")}">here</a>. '
                                     f'Please make a payment at your earliest convenience.<br><br>Thank you.')
            flash(message_content, 'danger')

        else:
            message_content = Markup(f'Dear {name},<br><br>'
                                     f'Your account is balanced. Thank you for shopping with us.<br><br>'
                                     f'We look forward to serving you again.')
            flash(message_content, 'success')
        
    return render_template("account_holder_dashboard.html", name=name)


@account_holder.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('account_holder_messages_list.html', messages=messages)

@account_holder.route('/delete_message/<int:message_id>')
def delete_message(message_id):
        
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    delete_message_by_id(message_id)

    messages = get_all_messages_by_user_id()
    flash("Your message has been deleted.", "success")
    return render_template('account_holder_messages_list.html', messages=messages)



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

            # insert into database
            apply_limit_increase_to_db(user_id, depot_id, current_limit, reason, requested_limit, requested_date)

            send_message(user_id, 4, "Dear manager, There is a new Credit Limit Increase Application awaiting your approval.", 1)
                
            flash("Your credit limit increase request has been submitted successfully", "success")

            return redirect(url_for('account_holder.dashboard'))
    
    flash_form_errors(form)
    return render_template('apply_limit_increase.html',form=form, account_holder_info=account_holder_info_dict)



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

    return render_template('view_credit_limit.html', current_limit=current_limit, current_balance=current_balance, remaining_credit=remaining_credit, account_holder_info=account_holder_info_dict)


@account_holder.route("/view_depot_products", methods=["GET", "POST"])
def view_depot_products():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    email = session['user_email']
    customer = get_user_by_email(email)
    depot_name = get_depot_name_by_id(customer[-1])
    return view_products(depot_name)


@account_holder.route("/additem/<product_id>", methods=["GET"])
def addItem(product_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return add_item(product_id)


@account_holder.route('/cart')
def getCart():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return get_cart()

@account_holder.route('/updatecart/<int:product_id>', methods=['POST'])
def updatecart(product_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return update_cart(product_id)


@account_holder.route('/deleteitem/<int:id>')
def deleteitem(id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return delete_item(id)


@account_holder.route('/clearcart')
def clearcart():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    try:
        session.pop('shoppingcart', None)
        return redirect(url_for('account_holder.view_depot_products'))
    except Exception as e:
        print(e)
        return redirect(url_for('account_holder.getCart'))


@account_holder.route('/checkout')
def checkout():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    grandtotal, cart_items, tax, shipping_fee = calculate_cart()
    session['cart_items'] = cart_items

    # We can clear shopping cart in the session once checkout button is clicked
    session.pop('shoppingcart', None)

    # Check the credit balance is greater than value purchses
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance

    if remaining_credit < float(grandtotal):
        flash("You don't have enough credit to make the purchase!", "danger")
        return redirect(url_for('account_holder.dashboard'))
    else:
        # Update current blance
        current_balance = float(current_balance) + float(grandtotal)
        current_balance = round(current_balance, 2)
        update_account_holder_current_balance(current_balance, user_id)

        # Get the current date
        payment_date = datetime.now().strftime('%Y-%m-%d')
        order_hdr_id = create_order(grandtotal, cart_items)
        payment_id = insert_payment(order_hdr_id, grandtotal, 1, payment_date)
        # Generate/Update the invoice
        invoice_id = generate_invoice(order_hdr_id, payment_id, grandtotal, tax, shipping_fee)

        # Render the payment confirmation modal with the success message
        return render_template('payment_confirmation_modal.html',invoice_id=invoice_id)

@account_holder.route('/view_receipt/<invoice_id>', methods=['GET'])
def view_receipt(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    user_id = session.get('user_id')
    account_balance = get_current_credit_balance(user_id)
    return view_receipt_pdf(invoice_id, account_balance)


# generate pdf reciept
@account_holder.route('/generate_pdf/<invoice_id>', methods=['GET'])
def generate_pdf(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    user_id = session.get('user_id')
    account_balance = get_current_credit_balance(user_id)
    return generate_pdf_for_user(invoice_id, account_balance)


@account_holder.route('/view_orders')
def view_orders():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    return view_orders_func()


@account_holder.route('/view_order/<int:order_id>')
def view_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    return view_order_func(order_id)


@account_holder.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return cancel_order_func(order_id)


@account_holder.route('/save_edited_order/<int:order_id>', methods=['GET', 'POST'])
def save_edited_order(order_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    payment_amount_diff = request.form.get('calculated_amount_diff')
    grandtotal = request.form.get('calculated_grandtotal')
    tax = request.form.get('calculated_tax')
    shipping_fee = request.form.get('shipping_fee')
    
    # Check the credit balance is greater than value purchses
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance

    if remaining_credit < float(payment_amount_diff):
        flash("You don't have enough credit to make the purchase!", "danger")
        return redirect(url_for('account_holder.dashboard'))
    else:
        # Update current blance
        current_balance = float(current_balance) + float(payment_amount_diff)
        current_balance = round(current_balance, 2)
        update_account_holder_current_balance(current_balance, user_id)


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


@account_holder.route('/view_invoices')
def view_invoices():
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response

    orders = get_order_receipts()
    current_month_year = datetime.now().strftime('%B %Y')

    return render_template('account_holder_view_invoices.html', orders=orders, current_month_year=current_month_year)


@account_holder.route('/view_invoice/<invoice_id>', methods=['GET'])
def view_invoice(invoice_id):
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    return view_invoice_html(invoice_id)


@account_holder.route('/view_invoice_pdf/<invoice_id>', methods=['GET'])
def generate_pdf_invoice(invoice_id):
    # Check authentication and authorisation
    auth_response = check_is_account_holder()
    if auth_response:
        return auth_response
    
    return view_invoice_pdf(invoice_id)




# endregion