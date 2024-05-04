from flask import Blueprint, flash, session, redirect, url_for
from fhd import my_hashing
from fhd.utilities import flash_form_errors

auth = Blueprint("auth", __name__, template_folder="templates")

# region functions
def check_password(db_password, user_password):
    # Compare hashed password with the password stored in db
    if my_hashing.check_value(db_password, user_password, salt='myhashsalt'):
        return True
    else:
        return False


def login_user(email, role_id, user_id):
    session['loggedin'] = True
    session['user_email'] = email
    session['user_role_id'] = role_id
    session['user_id'] = user_id

# endregion

# region routes
@auth.route("/login", methods=['GET', 'POST'])
def login():
    pass


@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_role_id", None)
    session.pop("user_email", None)
    session.pop("loggedin", None)
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    pass
# endregion
