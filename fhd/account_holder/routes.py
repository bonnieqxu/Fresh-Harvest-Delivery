from flask import Blueprint, render_template, session, flash
from fhd.utilities import flash_form_errors, check_auth, get_user_full_name, get_all_messages_by_user_id, delete_message_by_id

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
# endregion
