from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields import FileField, SubmitField, StringField, SelectField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired, NumberRange, Optional, Regexp
from fhd.utilities import get_product_weight, get_product_category


class AddProductWeightForm(FlaskForm):
    weight = StringField('Weight', validators=[Optional()])
    unit = StringField('Unit', validators=[DataRequired(message="Unit is required")])
    submit = SubmitField('Submit')


class EditProductWeightForm(FlaskForm):
    weight = StringField('Weight', validators=[Optional()])
    unit = StringField('Unit', validators=[DataRequired(message="Unit is required")])
    submit = SubmitField('Submit')

class AddCategoryForm(FlaskForm):
    categoryname = StringField(label='Name', validators=[DataRequired(),Length(min=3,max=50)])
    choices = [('1', 'Active'), ('0', 'Inactive')]
    status = SelectField(label='Status', coerce=int, choices=choices)
    submit = SubmitField('Submit')

class EditCategoryForm(FlaskForm):
    categoryname = StringField(label='Name', validators=[DataRequired(),Length(min=3,max=50)])
    choices = [('1', 'Active'), ('0', 'Inactive')]
    status = SelectField(label='Status', coerce=int, choices=choices)
    submit = SubmitField('Submit')

class AddShippingOptionForm(FlaskForm):
    shippingOption = StringField(label='Shipping Option', validators=[DataRequired(),Length(min=3,max=50)])
    price = StringField('Price', validators=[DataRequired(message="Price is required"), Regexp(r'^\d+(\.\d{1,2})?$', message="Price must be a valid number")])
    submit = SubmitField('Submit')

class EditShippingOptionForm(FlaskForm):
    shippingOption = StringField(label='Shipping Option', validators=[DataRequired(),Length(min=3,max=50)])
    price = StringField('Price', validators=[DataRequired(message="Price is required"), Regexp(r'^\d+(\.\d{1,2})?$', message="Price must be a valid number")])
    submit = SubmitField('Submit')
    
class ViewProductForm(FlaskForm):

    product_weight = get_product_weight()

    product_name = StringField(label='Product Type Name')
    product_price = StringField(label='Product Price')
    product_quantity = StringField(label='Product Quantity')
    product_unit = SelectField(label='Product Type Unit', choices=[(w[0], f"{w[1]} {w[2]}") for w in product_weight])
    depot = SelectField(label='Depot', coerce=int, choices=[(0, 'All Depots')])

class EditProductForm(FlaskForm):

    product_weight = get_product_weight()

    product_price = DecimalField(label='Product Price', validators=[NumberRange(min=0)])
    product_quantity = IntegerField(label='Product Quantity', validators=[NumberRange(min=0)])

class UpdateOrderStatusForm(FlaskForm):
    status = SelectField(label='Status', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddProductTypeForm(FlaskForm):
    product_name = StringField(label='Product Type Name', validators=[DataRequired(), Length(min=3, max=50)])
    product_unit = SelectField(label='Product Type Unit')
    product_description = TextAreaField(label='Product Type Description', render_kw={"rows": 3})
    product_category = SelectField(label='Product Type Category')
    product_image = FileField("Product Type Image (Max 1 image)", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AddProductTypeForm, self).__init__(*args, **kwargs)
        # Retrieve the latest categories and product weights from the database
        categories = get_product_category(False)
        product_weight = get_product_weight()
        # Update the choices for the select fields
        self.product_unit.choices = [(w[0], f"{w[1]} {w[2]}") for w in product_weight]
        self.product_category.choices = [(c[0], c[1]) for c in categories]

class EditProductTypeForm(FlaskForm):

    product_name = StringField(label='Product Type Name', validators=[DataRequired(), Length(min=3, max=50)])
    product_unit = SelectField(label='Product Type Unit')
    product_description = TextAreaField(label='Product Type Description', render_kw={"rows": 3})
    product_category = SelectField(label='Product Type Category')
    product_image = FileField("Product Type Image (Max 1 image)", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProductTypeForm, self).__init__(*args, **kwargs)
        # Retrieve the latest categories and product weights from the database
        categories = get_product_category(False)
        product_weight = get_product_weight()
        # Update the choices for the select fields
        self.product_unit.choices = [(w[0], f"{w[1]} {w[2]}") for w in product_weight]
        self.product_category.choices = [(c[0], c[1]) for c in categories]



class SearchProductTypeForm(FlaskForm):

    categories = get_product_category()

    product_name = StringField(label='Product Type Name')
    product_category = SelectField(label='Product Type Category', choices=[(c[0], c[1]) for c in categories])

class ReplyMessageForm(FlaskForm):

    message_content = TextAreaField(label='Message Content', render_kw={"rows": 3})
    submit = SubmitField('Submit')