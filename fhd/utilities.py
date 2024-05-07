from fhd.dbconnection import getCursor
from flask import flash, session, redirect, url_for
import base64

# Contains all the shared and db methods


def check_auth(user_role):
    if not 'loggedin' in session:
        flash("Please login first.", "danger")
        return redirect(url_for('auth.login'))

    if session['user_role_id'] != user_role:
        flash("Invalid action! Back to home page.", "danger")
        return redirect(url_for('main.home'))
    return None


def flash_form_errors(form):
    if form.errors:
        for error_messages in form.errors.values():
            for error in error_messages:
                flash(f"{error}", "danger")


def list_with_decoded_image(object_tuple, image_index):
    object_list = list(object_tuple)
    if object_list[image_index]:
        object_list[image_index] = base64.b64encode(
            object_list[image_index]).decode('utf-8')
    return object_list


def user_exists_with_email(email):
    if get_user_by_email(email):
        return True
    else:
        return False


def get_user_by_email(email):
    conn = getCursor()
    # Get the user info from db
    conn.execute('SELECT * FROM user WHERE email = %s', (email,))
    user = conn.fetchone()
    conn.close()
    return user


def get_basic_product_info_by_id(product_id):

    cursor = getCursor()

    # Fetch product information from the productid
    cursor.execute("""SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description FROM product p
                    INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
                    WHERE p.product_id =  %s""", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    return list_with_decoded_image(product, 2)


def get_full_product_info_by_id(product_id):

    cursor = getCursor()

    # Fetch product information from the productid
    cursor.execute("""SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description, d.location_name, pw.weight, pw.unit
                   FROM product p 
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
                   INNER JOIN depot d ON p.depot_id = d.depot_id
                   INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
                   WHERE p.product_id =  %s""", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    return list_with_decoded_image(product, 2)


def get_all_products(page_num, item_num_per_page):
    cursor = getCursor()

    # Calculate the offset
    offset = (page_num - 1) * item_num_per_page

    cursor.execute("""
        SELECT p.product_id, pt.product_type_name, p.orig_price, pt.product_image, pt.description
        FROM product p
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        ORDER BY p.product_id
        LIMIT %s OFFSET %s""", (item_num_per_page, offset))

    # Fetch the limited set of results
    results = cursor.fetchall()

    cursor.execute("""SELECT COUNT(*) FROM product""")
    total = cursor.fetchone()[0]

    products = []
    # Decode image and create a list of product
    for product in results:
        product_list = list_with_decoded_image(product, -2)
        products.append(product_list)
    cursor.close()
    return products, total
