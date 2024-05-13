from flask import Blueprint, render_template, session
from fhd.utilities import flash_form_errors, check_auth, get_user_full_name

account_holder = Blueprint("account_holder", __name__, template_folder="templates")

# region functions
def check_is_account_holder():
    return check_auth(2)


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
    return render_template("account_holder_dashboard.html", name=name)
# endregion
