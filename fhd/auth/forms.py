from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError
import re
from wtforms.validators import ValidationError
from fhd.utilities import user_exists_with_email

def validate_user_not_exists(form, field):
    if user_exists_with_email(field.data) == False:
        raise ValidationError( "There is no registered account with that email.")


def validate_email_format(form, field):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', field.data):
        raise ValidationError("You did not enter a valid email!")


class LoginForm(FlaskForm):
    email = EmailField("Email *", validators=[InputRequired("Input is required!"),
                                              DataRequired("Data is required!"),
                                              Length(min=5, max=50, message="Email must be between 5 and 50 characters long!"),
                                              validate_email_format, validate_user_not_exists])

    password = PasswordField("Password *", validators=[InputRequired("Input is required!"),
                                                       DataRequired("Data is required!"),
                                                       Length(min=8, max=40, message="Password must be between 8 and 40 characters long!")])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    pass
