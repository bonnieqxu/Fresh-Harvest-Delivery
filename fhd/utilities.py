from fhd.dbconnection import getCursor
from flask import flash, session, redirect, url_for

# Contains all the shared and db methods

def check_auth(user_role):
    if not 'loggedin' in session:
        flash("Please login first.", "danger")
        return redirect(url_for('auth.login'))

    if session['user_role_id'] != user_role:
        flash("Invalid action! Back to home page.", "danger")
        return redirect(url_for('main.home'))
    return None

def flash_form_errors(form):
    if form.errors:
        for error_messages in form.errors.values():
            for error in error_messages:
                flash(f"{error}", "danger")


def user_exists_with_email(email):
    if get_user_by_email(email):
        return True
    else:
        return False


def get_user_by_email(email):
    conn = getCursor()
    # Get the user info from db
    conn.execute('SELECT * FROM user WHERE email = %s', (email,))
    user = conn.fetchone()
    conn.close()
    return user
