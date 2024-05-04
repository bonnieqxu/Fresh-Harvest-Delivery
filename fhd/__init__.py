import os
from flask import Flask
from flask_hashing import Hashing

app = Flask(__name__)
my_hashing = Hashing(app)


def create_app():

    app.secret_key = os.environ.get('SECRET_KEY') or "MySecretKey"

    from fhd.account_holder.routes import account_holder
    from fhd.auth.routes import auth
    from fhd.customer.routes import customer
    from fhd.local_manager.routes import local_manager
    from fhd.main.routes import main
    from fhd.national_manager.routes import national_manager
    from fhd.staff.routes import staff

    app.register_blueprint(account_holder, url_prefix="/account_holder")
    app.register_blueprint(auth)
    app.register_blueprint(customer, url_prefix="/customer")
    app.register_blueprint(local_manager, url_prefix="/local_manager")
    app.register_blueprint(main)
    app.register_blueprint(national_manager, url_prefix="/national_manager")
    app.register_blueprint(staff, url_prefix="/staff")
    return app
