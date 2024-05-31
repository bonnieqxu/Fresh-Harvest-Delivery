from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields import FileField, SubmitField, StringField, SelectField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, InputRequired, NumberRange
from fhd.utilities import get_product_category, get_product_weight

class AddProductTypeForm(FlaskForm):

    categories = get_product_category(False)
    product_weight = get_product_weight()

    product_name = StringField(label='Product Type Name', validators=[DataRequired(),Length(min=3,max=50)])
    product_unit = SelectField(label='Product Type Unit', choices=[(w[0], f"{w[1]} {w[2]}") for w in product_weight])
    product_description = TextAreaField(label='Product Type Description', render_kw={"rows": 3})
    product_category = SelectField(label='Product Type Category', choices=[(c[0], c[1]) for c in categories])
    product_image = FileField("Product Type Image (Max 1 image)", validators=[
                              FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit')

class EditProductTypeForm(FlaskForm):

    categories = get_product_category(False)
    product_weight = get_product_weight()

    product_name = StringField(label='Product Type Name', validators=[DataRequired(),Length(min=3,max=50)])
    product_unit = SelectField(label='Product Type Unit', choices=[(w[0], f"{w[1]} {w[2]}") for w in product_weight])
    product_description = TextAreaField(label='Product Type Description', render_kw={"rows": 3})
    product_category = SelectField(label='Product Type Category', choices=[(c[0], c[1]) for c in categories])
    product_image = FileField("Product Type Image (Max 1 image)", validators=[
                              FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit')



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


class UpdateOrderStatusForm(FlaskForm):
    status = SelectField(label='Status', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProductForm(FlaskForm):

    product_weight = get_product_weight()

    product_price = DecimalField(label='Product Price', validators=[NumberRange(min=0)])
    product_quantity = IntegerField(label='Product Quantity', validators=[NumberRange(min=0)])
    submit = SubmitField('Submit')