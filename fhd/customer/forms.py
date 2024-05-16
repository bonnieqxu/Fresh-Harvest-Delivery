# from flask_wtf import FlaskForm
# from wtforms import StringField, SelectField
# from wtforms.validators import InputRequired, Length, Regexp


# class PaymentForm(FlaskForm):
#     card_number = StringField('Card Number', validators=[InputRequired(), Length(min=16, max=16), Regexp('^[0-9]*$', message='Card number must contain 16 digits')])
#     cardholder_name = StringField('Cardholder Name', validators=[InputRequired(), Regexp('^[A-Za-z0-9 -]*$', message='Cardholder name must contain only letters, spaces and hyphens allowed')])
#     expiry_month = SelectField('Expiry Month', choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)], validators=[InputRequired()])
#     expiry_year = SelectField('Expiry Year', choices=[(str(i), str(i)) for i in range(2025, 2030)], validators=[InputRequired()])
#     cvv = StringField('CVV', validators=[InputRequired(), Length(min=3, max=3), Regexp('^[0-9]*$', message='CVV must contain only 3 numbers')])
