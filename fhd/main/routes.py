from flask import Blueprint, render_template
from fhd.utilities import flash_form_errors

main = Blueprint("main", __name__, template_folder="templates")


# region functions
# endregion

# region routes
@main.route("/")
@main.route("/home")
@main.route("/index")
@main.route("/default")
def home():
    return render_template("home.html", is_home=True)

@main.route("/view_products", methods = ['GET'])
def view_products():
    pass
# endregion
