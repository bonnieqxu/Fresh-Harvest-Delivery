from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields import FileField, SubmitField, StringField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired, NumberRange, Optional
from fhd.utilities import get_product_weight


class AddProductWeightForm(FlaskForm):
    weight = DecimalField('Weight', places=3, validators=[
        Optional(), 
        NumberRange(min=0, message="Weight must be a positive number or zero.")
    ])
    unit = StringField('Unit', validators=[DataRequired(message="Unit is required")])
    submit = SubmitField('Submit')


