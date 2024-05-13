from flask import Blueprint, render_template, session
from fhd.utilities import flash_form_errors, check_auth, get_user_full_name

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
