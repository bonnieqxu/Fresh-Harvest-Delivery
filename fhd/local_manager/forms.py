from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields import FileField, SubmitField, StringField, SelectField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from fhd.utilities import get_product_category, get_product_weight, get_product_type_by_name, get_box_size_full, get_product_weight_kilo_only
from fhd.utilities import get_box_category, get_all_depots
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


class ViewProductForm(FlaskForm):

    product_weight = get_product_weight()

    product_name = StringField(label='Product Type Name')
    product_price = StringField(label='Product Price')
    product_quantity = StringField(label='Product Quantity')
    product_unit = SelectField(label='Product Type Unit', choices=[(w[0], f"{w[1]} {w[2]}") for w in product_weight])

class EditProductForm(FlaskForm):

    product_weight = get_product_weight()

    product_price = DecimalField(label='Product Price', validators=[NumberRange(min=0)])
    product_quantity = IntegerField(label='Product Quantity', validators=[NumberRange(min=0)])
    submit = SubmitField('Submit')


class UpdateOrderStatusForm(FlaskForm):
    status = SelectField(label='Status', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddBoxForm(FlaskForm):
    categories = get_product_category(False)
    product_weight = get_product_weight_kilo_only()
    box_sizes = get_box_size_full()
    category = get_box_category()
    depots = get_all_depots()

    box_name = StringField(label='Name', validators=[DataRequired(), Length(min=3, max=50)])
    box_unit = SelectField(label='Unit', choices=[(w[0], f"{w[1]} {w[2]}") for w in product_weight])
    box_size = SelectField(label='Size', choices=[(w[0], f"{w[1]} - ${w[2]}") for w in box_sizes])
    box_category = SelectField(label='Category', choices=[(c[0], c[1]) for c in category])
    box_depot = SelectField(label='Depot', choices=[(int(d['id']), d['name']) for d in depots], validators=[Optional()])
    box_description = TextAreaField(label='Description', render_kw={"rows": 3})
    box_stock = IntegerField('Stock', validators=[DataRequired("Stock is required!"), NumberRange(min=1, message="At least 1.")])
    box_image = FileField("Box Image (Max 1 image)", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

    def validate_box_name(form, field):
        if get_product_type_by_name(field.data):
            raise ValidationError("Box name already exist!")


class ReplyMessageForm(FlaskForm):

    message_content = TextAreaField(label='Message Content', render_kw={"rows": 3})
    submit = SubmitField('Submit')