from flask import Blueprint, render_template
from fhd.utilities import flash_form_errors, check_auth

local_manager = Blueprint("local_manager", __name__, template_folder="templates")

# region functions
def check_is_local_manager():
    # Need to pass in the correct user_role to check_auth function
    # return check_auth()
    pass

# endregion

# region routes


@local_manager.route("/example", methods=["GET", "POST"])
def example():
    # Check authentication and authorisation
    auth_response = check_is_local_manager()
    if auth_response:
        return auth_response

    pass
# endregion
