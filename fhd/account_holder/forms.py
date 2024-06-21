from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Length, Regexp, DataRequired, NumberRange, Optional
from fhd.utilities import get_message_categories, get_box_frequency, get_box_category, get_box_size_full

class ApplyLimitIncreaseForm(FlaskForm):
    reason = StringField(label='Reason for Limit Increase (optional)', validators=[Optional(), Length(min=3, max=255)])
    requested_limit = DecimalField(label='Requested Limit ($)', validators=[InputRequired(),DataRequired(), NumberRange(min=0, max=5000)])
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

class sendMessageForm(FlaskForm):
    categories = get_message_categories()

    message_category = SelectField(label='Message Category', choices=[(c[0], c[1]) for c in categories])
    message_content = TextAreaField(label='Message Content', render_kw={"rows": 3})
    submit = SubmitField('Submit')
