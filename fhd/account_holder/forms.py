from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DecimalField
from wtforms.validators import InputRequired, Length, Regexp, DataRequired, NumberRange, Optional


class ApplyLimitIncreaseForm(FlaskForm):
    reason = StringField(label='Reason for Limit Increase (optional)', validators=[Optional(), Length(min=3, max=255)])
    requested_limit = DecimalField(label='Requested Limit ($)', validators=[InputRequired(),DataRequired(), NumberRange(min=0, max=5000)])
    submit = SubmitField('Submit')