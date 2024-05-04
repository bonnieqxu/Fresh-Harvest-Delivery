from flask import Blueprint, render_template
from fhd.utilities import flash_form_errors, check_auth

customer = Blueprint("customer", __name__, template_folder="templates")

# region functions
def check_is_customer():
    # Need to pass in the correct user_role to check_auth function
    # return check_auth()
    pass

# endregion

# region routes
@customer.route("/example", methods=["GET", "POST"])
def example():
    # Check authentication and authorisation
    auth_response = check_is_customer()
    if auth_response:
        return auth_response

    pass

# endregion
