from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, Regexp, DataRequired, NumberRange
from fhd.utilities import get_message_categories, get_box_frequency, get_box_category, get_box_size_full


# class PaymentForm(FlaskForm):
#     card_number = StringField('Card Number', validators=[InputRequired(), Length(min=16, max=16), Regexp('^[0-9]*$', message='Card number must contain 16 digits')])
#     cardholder_name = StringField('Cardholder Name', validators=[InputRequired(), Regexp('^[A-Za-z0-9 -]*$', message='Cardholder name must contain only letters, spaces and hyphens allowed')])
#     expiry_month = SelectField('Expiry Month', choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)], validators=[InputRequired()])
#     expiry_year = SelectField('Expiry Year', choices=[(str(i), str(i)) for i in range(2025, 2030)], validators=[InputRequired()])
#     cvv = StringField('CVV', validators=[InputRequired(), Length(min=3, max=3), Regexp('^[0-9]*$', message='CVV must contain only 3 numbers')])

class ApplyAccountHolderForm(FlaskForm):

    business_name = StringField(label='Business Name', validators=[InputRequired(),DataRequired(),Length(min=3,max=50)])
    business_address = StringField(label='Business Address', validators=[InputRequired(),DataRequired(),Length(min=3,max=255)])
    business_phone = StringField(label='Business Contact No', validators=[InputRequired(),DataRequired(),Length(min=3,max=20),Regexp(regex=r'^\d{10}$', message="Phone number must be 10 digits.")])

    submit = SubmitField('Submit')

class sendMessageForm(FlaskForm):
    categories = get_message_categories()

    message_category = SelectField(label='Message Category', choices=[(c[0], c[1]) for c in categories])
    message_content = TextAreaField(label='Message Content', render_kw={"rows": 3})
    submit = SubmitField('Submit')

class AddSubscriptionForm(FlaskForm):
    frequency = get_box_frequency()
    category = get_box_category()
    size = get_box_size_full()

    box_frequency = SelectField(label='Frequency', choices=[(c[0], c[1]) for c in frequency])
    box_category = SelectField(label='Category', choices=[(c[0], c[1]) for c in category])
    box_size = SelectField(label='Size', choices=[(w[0], f"{w[1]} - ${w[2]}") for w in size])
    subscription_quantity = IntegerField('Quantity', validators=[DataRequired("Quantity is required!"), NumberRange(min=1, message="At least 1.")])
    submit = SubmitField('Submit')
