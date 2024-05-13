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
    
# region lookup tables
def get_product_category(include_all=True):
    cursor = getCursor()
    cursor.execute("""SELECT category_id, category_name FROM product_category WHERE is_active = 1""")
    categories = []
    if include_all:
        categories.append((0, 'All'))
    for row in cursor.fetchall():
        categories.append(row)
    cursor.close()
    return categories

def get_box_size():
    cursor = getCursor()
    cursor.execute("""SELECT size_name FROM box_size""")
    results = cursor.fetchall()
    cursor.close()
    return results

def get_gst_rate():
    cursor = getCursor()
    cursor.execute("""SELECT percentage FROM gst_rate""")
    gst_rate = cursor.fetchone()
    cursor.close()
    return int(gst_rate[0])

def get_product_weight():
    cursor = getCursor()
    cursor.execute("""SELECT product_weight_id, weight, unit FROM product_weight WHERE is_active = 1""")
    product_weight = cursor.fetchall()
    cursor.close()
    return product_weight

# get depot names
def query_depot_names():
    cursor = getCursor()
    cursor.execute("SELECT depot_name FROM depot")
    depot_names = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return depot_names

# get depot 
def depots():
    cursor = getCursor()
    cursor.execute("SELECT depot_id, depot_name FROM depot")
    depots = [{'depot_id': row[0], 'depot_name': row[1]} for row in cursor.fetchall()]
    cursor.close()
    return depots

# endregion

def get_product_type_by_name(product_name):
    conn = getCursor()
    # Get the user info from db
    conn.execute('SELECT * FROM product_type WHERE product_type_name = %s', (product_name,))
    product = conn.fetchall()
    conn.close()
    return product

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
    cursor.execute("""SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description, d.depot_name, pw.weight, pw.unit
                   FROM product p 
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
                   INNER JOIN depot d ON p.depot_id = d.depot_id
                   INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
                   WHERE p.product_id =  %s""", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    return list_with_decoded_image(product, 2)


def get_all_products(page_num, item_num_per_page, depot_name, category_id, size, category_name):
    cursor = getCursor()

    # Calculate the offset for pagination
    offset = (page_num - 1) * item_num_per_page

    # Base SELECT clause for querying products
    select = """
    SELECT p.product_id, pt.product_type_name, p.orig_price, pt.product_image, pt.description, pw.weight, pw.unit
    """

    # Base FROM and JOIN clauses for querying products
    from_inner_join = """
    FROM product p
    INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
    INNER JOIN depot d ON p.depot_id = d.depot_id
    INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
    """

    # Base WHERE clause including the depot name
    where = f" WHERE d.depot_name = '{depot_name}'"
    order_by = " ORDER BY"
    # Default sorting by product type name
    product_type_name = " pt.product_type_name"

    # Pagination clause
    limit = f" LIMIT {item_num_per_page} OFFSET {offset}"
 
    select_count = "SELECT COUNT(*)"

    # Build the initial query string
    from_where = from_inner_join + where + order_by + product_type_name

    if category_id != 0:
        category_inner_join = " INNER JOIN product_category pc ON pt.category_id = pc.category_id"
        and_category = f' AND pc.category_id = {category_id}'

        from_where = from_inner_join + category_inner_join + where + and_category + order_by + product_type_name
        
        if category_name == "Premade Box":
            box_inner_join = " INNER JOIN box b ON b.product_id = p.product_id INNER JOIN box_size bs ON b.box_size_id = bs.box_size_id"
            if size == None:
                sort_box_size = f" FIELD(bs.size_name, 'small', 'medium', 'large'),"
                from_where = from_inner_join + category_inner_join + box_inner_join + where + and_category + order_by + sort_box_size + product_type_name
            
            else:
                and_box_size = f" AND bs.size_name = '{size}'"
                from_where = from_inner_join + category_inner_join + box_inner_join + where + and_category + and_box_size + order_by + product_type_name

    # Combine all parts to form the final query
    query = select + from_where + limit
    count_query = select_count + from_where    
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.execute(count_query)
    total = cursor.fetchone()[0]

    products = []
    # Decode image and create a list of product
    for product in results:
        product_list = list_with_decoded_image(product, -4)
        products.append(product_list)
    cursor.close()
    return products, total


def add_new_product_type(image_data, product_name, product_unit, product_description, product_category):
    cursor = getCursor()

    cursor.execute("""INSERT INTO product_type (product_type_name, product_weight_id, description, category_id, product_image) VALUES
                       (%s, %s, %s, %s, %s)""", 
                       (product_name, product_unit, product_description, product_category, image_data))
    cursor.close()

def update_product_type(product_type_id, image_data, product_name, product_unit, product_description, product_category):
    cursor = getCursor()

    if image_data is None:

        cursor.execute("""Update product_type set product_type_name=%s, product_weight_id=%s, 
                            description=%s, category_id=%s where product_type_id=%s""", 
                        (product_name, product_unit, product_description, product_category, product_type_id))
    else:

        cursor.execute("""Update product_type set product_type_name=%s, product_weight_id=%s, 
                            description=%s, category_id=%s, product_image=%s where product_type_id=%s""", 
                        (product_name, product_unit, product_description, product_category, image_data, product_type_id))
        
    cursor.close()

def delete_product_type_by_id(product_type_id):
    cursor = getCursor()

    cursor.execute("""delete from product_type where product_type_id=%s""", 
                       (product_type_id,))
    cursor.close()

def get_all_product_type(page_num, item_num_per_page, category_id = "0", product_name=""):
    cursor = getCursor()

    if product_name is None:
        product_name = ""

    # Calculate the offset
    offset = (page_num - 1) * item_num_per_page
    if category_id == "0" and len(product_name) == 0:
        cursor.execute("""
            SELECT product_type_id, product_type_name, product_image, description
            FROM product_type
            ORDER BY product_type_id
            LIMIT %s OFFSET %s""", (item_num_per_page, offset))
        
        results = cursor.fetchall()
        cursor.execute("""SELECT COUNT(*) FROM product_type""")
        total = cursor.fetchone()[0]

    else:
        if len(product_name) > 0 and category_id == "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.product_type_name = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (product_name, item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE 
                            pt.product_type_name = %s""", (product_name,))
            total = cursor.fetchone()[0]

        elif len(product_name) > 0 and category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pc.category_id = %s and pt.product_type_name = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (category_id, product_name, item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pc.category_id = %s
                           and pt.product_type_name = %s""", (category_id, product_name,))
            total = cursor.fetchone()[0]
        
        elif category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pc.category_id = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (category_id, item_num_per_page, offset))     

            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pc.category_id = %s""", (category_id,))
            total = cursor.fetchone()[0]

    products = []
    # Decode image and create a list of product
    for product in results:
        product_list = list_with_decoded_image(product, -2)
        products.append(product_list)
    cursor.close()
    return products, total

def get_product_type_by_id(product_type_id):

    cursor = getCursor()

    # Fetch product information from the productid
    cursor.execute("""SELECT product_type_id, product_type_name, product_image, description, product_weight_id, category_id
                        FROM product_type pt 
                        WHERE product_type_id =  %s""", (product_type_id,))
    product = cursor.fetchone()
    cursor.close()
    return list_with_decoded_image(product, 2)

def get_depot_name_by_id(depot_id):
    cursor = getCursor()
    cursor.execute("SELECT depot_name from depot WHERE depot_id = %s", (depot_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0]



def User (email, password, depot_id,first_name, last_name, address, phone, dob):
    cursor = getCursor()

        # Check if the email already exists in the database
    cursor.execute("""
            SELECT email FROM user WHERE email = %s
        """, (email,))
    if cursor.fetchone():
            return "Email already exists."  # Exit the function and inform the user

        # Insert into user table
    cursor.execute("""
            INSERT INTO user (email, password, role_id, is_active, depot_id)
            VALUES (%s, %s, 1, TRUE, %s)
        """, (email, password, depot_id))
    user_id = cursor.lastrowid  # Get the last inserted ID

        # Insert into user_profile table
    cursor.execute("""
            INSERT INTO user_profile (user_id, first_name, last_name, address, phone_number, date_of_birth)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, address, phone, dob))
    cursor.close()
    return User
    
def get_user_full_name(user_id):
    conn = getCursor()
    # Get the user info from db
    conn.execute('SELECT first_name, last_name FROM user_profile WHERE user_id = %s', (user_id,))
    user = conn.fetchone()
    name = f'{user[0]} {user[1]}'
    conn.close()
    return name if name else None

