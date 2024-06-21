from flask import Blueprint, flash, session, redirect, url_for, render_template, request
from fhd import my_hashing
from fhd.utilities import flash_form_errors, get_user_by_email, depots, User, get_depot_name_by_id, user_exists_with_email
from fhd.auth.forms import RegistrationForm, LoginForm
from fhd.dbconnection import getCursor
from datetime import datetime
import re


auth = Blueprint("auth", __name__, template_folder="templates")

# region functions
def check_password(db_password, user_password):
    # Compare hashed password with the password stored in db myhashsalt
    if my_hashing.check_value(db_password, user_password, salt='myhashsalt'):
        return True
    else:
        return False


def login_user(email, role_id, user_id, depot):
    #set session variables to be used throughout 
    session['loggedin'] = True
    session['user_email'] = email
    session['user_role_id'] = role_id
    session['user_id'] = user_id
    session['user_depot'] = depot
    session['user_depot_name'] = get_depot_name_by_id(depot)

# endregion

# region routes


@auth.route("/login", methods=['GET', 'POST'])
def login():
    # this function handles user login.

    # GET: Renders the login page.
    # POST: Validates user credentials and logs in if valid.

    # Returns:
    # If successful login, redirects to respective dashboard.
    # If invalid credentials, renders login page with error message.

    form = LoginForm()
    if request.method == 'POST':
        # Handle login form submission
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check username and password
        user = get_user_by_email(email)
        if user:
            hashed_password = user[2]
            user_role = user[3]
            user_id = user[0]
            user_depot = user[5]

            if check_password(hashed_password, password):
                if user[4] == True:
                    # Set session variable to indicate user is logged in
                    login_user(email, user_role, user_id, user_depot)
                    # Redirect to dashboard or some other page
                    if user_role == 1: #customer
                        return redirect(url_for('customer.view_depot_products'))
                    if user_role == 2: #account holder
                        return redirect(url_for('account_holder.dashboard'))
                    if user_role == 3: #staff
                        return redirect(url_for('staff.dashboard'))
                    if user_role == 4: #local manager
                        return redirect(url_for('local_manager.dashboard'))
                    if user_role == 5: #nactional manager
                        return redirect(url_for('national_manager.dashboard'))
                else:
                    return render_template("login.html", form=form, msg="User is inactive")

            else:
                # Invalid credentials, render login page with error message
                return render_template("login.html", form=form, msg="Incorrect password")

        return render_template("login.html", form=form, msg="Invalid email")

    # If it's a GET request, just render the login page
    return render_template("login.html", form=form)


@auth.route("/logout")
def logout():
    # Logs out the current user by clearing the session.
    session.clear() #clear all session
    return redirect(url_for("auth.login"))



@auth.route("/register", methods=["GET", "POST"])
def register():
    # This function handles user registration.

    # GET: Renders the registration page.
    # POST: Validates user registration form and creates a new user if valid.

    # Returns:
    # If successful registration, redirects to the login page.
    # If invalid form data, renders registration page with validation errors.
    
    form = RegistrationForm()
    depots_list = depots()  
    form.depot_id.choices = [(depot['depot_id'], depot['depot_name']) for depot in depots_list] 

    if form.validate_on_submit():

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', form.email.data):
            flash('Invalid email address', 'danger')
            return render_template('register.html', form=form, depots=depots_list)

        # Check if email already exists
        if user_exists_with_email(form.email.data):
            flash('Email address already in use', 'danger')
            return render_template('register.html', form=form, depots=depots_list)

        # Validate names
        if not form.first_name.data.isalpha() or not form.last_name.data.isalpha():
            flash('Name must contain only letters', 'danger')
            return render_template('register.html', form=form, depots=depots_list)

        # Validate phone number
        if not form.phone.data.isdigit():
            flash('Phone number must contain only numbers', 'danger')
            return render_template('register.html', form=form, depots=depots_list)

        # Validate age
        dob = form.dob.data
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            flash('User must be 18 years or older', 'danger')
            return render_template('register.html', form=form, depots=depots_list)

        # Validate password
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=-]).{8,}$'
        if not re.match(password_pattern, form.password.data):
            flash('Password must be at least 8 characters long and include a mix of character types', 'danger')
            return render_template('register.html', form=form, depots=depots_list)


        # Hash the password before storing in the database
        hashed = my_hashing.hash_value(form.password.data, salt='myhashsalt')
        
        # Create a new user object
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed,  
            address=form.address.data,
            phone=form.phone.data,
            dob=form.dob.data,
            depot_id=form.depot_id.data,
            isrural = form.isrural.data #is rural is saved here for shipping option 
        )
        flash("Thank you for signing up! Please log in.", "success")
        return redirect(url_for('auth.login'))  

    return render_template('register.html', form=form, depots=depots_list)
    pass


# endregion
