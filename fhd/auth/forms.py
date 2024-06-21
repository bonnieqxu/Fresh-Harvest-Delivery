from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, SubmitField, EmailField, StringField, DateField, SelectField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError, EqualTo, Email 
import re
from wtforms.validators import ValidationError

from fhd.utilities import user_exists_with_email


def validate_user_not_exists(form, field):
    if user_exists_with_email(field.data) == False:
        raise ValidationError( "There is no registered account with that email.")


def validate_user_email(form, field):
    if user_exists_with_email(field.data) == True:
        raise ValidationError( "This email address has already been registered.")
    

def validate_email_format(form, field):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', field.data):
        raise ValidationError("You did not enter a valid email!")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired("Input is required!"),
                                              DataRequired("Data is required!"),
                                              Length(min=5, max=50, message="Email must be between 5 and 50 characters long!"),
                                              validate_email_format, validate_user_not_exists])

    password = PasswordField("Password", validators=[InputRequired("Input is required!"),
                                                       DataRequired("Data is required!"),
                                                       Length(min=8, max=40, message="Password must be between 8 and 40 characters long!")])
    submit = SubmitField("Login")



class RegistrationForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired(), Length(min=2, max=40)])
    last_name = StringField(label='Family Name', validators=[DataRequired(), Length(min=2, max=40)])
    email = EmailField(label='Email *', validators=[InputRequired("Input is required!"),
                                                    DataRequired("Data is required!"),
                                                    Length(min=5, max=50, message="Email must be between 5 and 50 characters long!"),
                                                    validate_email_format, validate_user_email])
    password = PasswordField('Password *', validators=[InputRequired("Input is required!"),
                                                       DataRequired("Data is required!"),
                                                       Length(min=8, max=40, message="Password must be between 8 and 40 characters long!")])
    confirm_password = PasswordField('Confirm Password *', validators=[InputRequired("Input is required!"),
                                                                       DataRequired("Data is required!"),
                                                                       EqualTo('password', message="Passwords must match!")])
    address = StringField(label='Address', validators=[DataRequired()])
    phone = StringField(label='Phone', validators=[DataRequired()])
    dob = DateField(label='Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    depot_id = SelectField(label='Depot', choices=[], validators=[DataRequired()])
    isrural = BooleanField('Are you located more than 20km from your depot?')
    submit = SubmitField("Register")
