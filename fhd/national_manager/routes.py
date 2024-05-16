from flask import Blueprint, render_template, session, flash, redirect, url_for
from fhd.utilities import flash_form_errors, check_auth, delete_message_by_id
from fhd.utilities import get_user_full_name, get_product_weight, get_all_messages_by_user_id
from fhd.utilities import national_manager_add_product_weight, national_manager_delete_product_weight_by_id
from fhd.national_manager.forms import AddProductWeightForm

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
        weight = form.weight.data if form.weight.data else None
        unit = form.unit.data

        national_manager_add_product_weight(weight, unit)
        flash("New product unit added successfully.", "success")
        return redirect(url_for('national_manager.dashboard'))  # Adjust redirect as needed

    return render_template('national_manager_add_product_weight.html', form=form)


@national_manager.route("/view_product_weight", methods=["GET", "POST"])
def view_product_weight():

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    product_weight = get_product_weight()
    return render_template("national_manager_view_product_weight.html", product_weight=product_weight)



@national_manager.route("/delete_product_weight", methods=["GET", "POST"])
def delete_product_weight(product_weight_id):

    # Check authentication and authorization
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    national_manager_delete_product_weight_by_id (product_weight_id)
    flash("Product Unit deleted successfully.", "success")
    return render_template("national_manager_view_product_weight.html")

@national_manager.route('/getMessages')
def getMessages():
    # Check authentication and authorisation
    auth_response = check_is_national_manager()
    if auth_response:
        return auth_response

    messages = get_all_messages_by_user_id()
    
    return render_template('national_manager_list.html', messages=messages)

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