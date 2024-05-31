from fhd.dbconnection import getCursor
from flask import flash, session, redirect, url_for
import base64, mysql.connector

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

def get_product_category_without_box(include_all=True):
    cursor = getCursor()
    cursor.execute("""SELECT category_id, category_name FROM product_category WHERE is_active = 1 AND category_id != 7""")
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

def get_box_size_full():
    cursor = getCursor()
    cursor.execute("""SELECT * FROM box_size""")
    results = cursor.fetchall()
    cursor.close()
    return results

def get_gst_rate():
    cursor = getCursor()
    cursor.execute("""SELECT percentage FROM gst_rate""")
    gst_rate = cursor.fetchone()
    cursor.close()
    return int(gst_rate[0])

def get_product_weight(product_weight_id=None):
    cursor = getCursor()
    if product_weight_id is not None:
        cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit FROM product_weight WHERE product_weight_id = %s AND is_active = 1""", (product_weight_id,))
    else:
        cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit FROM product_weight WHERE is_active = 1 ORDER BY unit ASC""")
    product_weight = cursor.fetchall()
    cursor.close()
    return product_weight

def get_product_weight_kilo_only():
    cursor = getCursor()
    cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit 
                   FROM product_weight WHERE weight IS NOT NULL AND is_active = 1""")
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

def get_depot_name_by_id(depot_id):
    cursor = getCursor()
    cursor.execute("SELECT depot_name from depot WHERE depot_id = %s", (depot_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0]

def get_status_choices():
    cursor = getCursor()
    cursor.execute("SELECT status_id, status_name FROM order_status")
    status_choices = [(row[0], row[1]) for row in cursor.fetchall()]
    cursor.close()
    return status_choices

def get_all_category_List():
    cursor = getCursor()
    # Get all the product category info from db
    cursor.execute("""SELECT * FROM product_category;""")
    categories = cursor.fetchall()
    cursor.close()
    return categories

# endregion

def get_product_type_by_name(product_name):
    conn = getCursor()
    # Get the product_type info from db
    conn.execute('SELECT * FROM product_type WHERE is_active = 1 AND product_type_name = %s', (product_name,))
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

    # Fetch product information from the product_id, including category name
    cursor.execute("""
        SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description, d.depot_name, pw.weight, pw.unit, pc.category_name, stock_quantity
        FROM product p 
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN depot d ON p.depot_id = d.depot_id
        INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
        INNER JOIN product_category pc ON pt.category_id = pc.category_id
        WHERE p.product_id = %s
    """, (product_id,))
    
    product = cursor.fetchone()
    cursor.close()
    return list_with_decoded_image(product, 2)


def get_all_products(page_num, item_num_per_page, depot_name, category_id, size, category_name, filter_out_boxes=False):
    cursor = getCursor()

    # Calculate the offset for pagination
    offset = (page_num - 1) * item_num_per_page

    # Base SELECT clause for querying products
    select = """
    SELECT p.product_id, pt.product_type_name, p.orig_price, pt.product_image, pt.description, pw.weight, pw.unit, stock_quantity
    """

    # Base FROM and JOIN clauses for querying products
    from_inner_join = """
    FROM product p
    INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
    INNER JOIN depot d ON p.depot_id = d.depot_id
    INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
    """

    # Base WHERE clause including the depot name
    where = f" WHERE p.is_active = 1 AND d.depot_name = '{depot_name}'"
    order_by = " ORDER BY"
    # Default sorting by product type name
    product_type_name = " pt.product_type_name"

    # Pagination clause
    limit = f" LIMIT {item_num_per_page} OFFSET {offset}"
 
    select_count = "SELECT COUNT(*)"

    # Build the initial query string
    from_where_order_by = from_inner_join + where + order_by + product_type_name

    if category_id != 0:
        category_inner_join = " INNER JOIN product_category pc ON pt.category_id = pc.category_id"
        and_category = f' AND pc.category_id = {category_id}'

        from_where_order_by = from_inner_join + category_inner_join + where + and_category + order_by + product_type_name
        
        if category_name == "Premade Box":
            box_inner_join = " INNER JOIN box b ON b.product_id = p.product_id INNER JOIN box_size bs ON b.box_size_id = bs.box_size_id"
            if size == None:
                sort_box_size = f" FIELD(bs.size_name, 'small', 'medium', 'large'),"
                from_where_order_by = from_inner_join + category_inner_join + box_inner_join + where + and_category + order_by + sort_box_size + product_type_name
            
            else:
                and_box_size = f" AND bs.size_name = '{size}'"
                from_where_order_by = from_inner_join + category_inner_join + box_inner_join + where + and_category + and_box_size + order_by + product_type_name
    else:
        if filter_out_boxes:
            not_boxes_query = " AND pt.category_id != 7"
            from_where_order_by = from_inner_join + where + not_boxes_query + order_by + product_type_name

    # Combine all parts to form the final query
    query = select + from_where_order_by + limit
    count_query = select_count + from_where_order_by    
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.execute(count_query)
    total = cursor.fetchone()[0]

    products = []
    # Decode image and create a list of product
    for product in results:
        product_list = list_with_decoded_image(product, 3)
        products.append(product_list)
    cursor.close()
    return products, total


def add_new_product_type(image_data, product_name, product_unit, product_description, product_category):
    cursor = getCursor()
    cursor.execute("""INSERT INTO product_type (product_type_name, product_weight_id, description, category_id, product_image) VALUES
                       (%s, %s, %s, %s, %s)""", 
                       (product_name, product_unit, product_description, product_category, image_data))
    product_type_id = cursor.lastrowid
    cursor.close()
    return product_type_id

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

    cursor.execute("""DELETE FROM product_type WHERE product_type_id=%s""", 
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
            FROM product_type WHERE is_active = 1
            ORDER BY product_type_id
            LIMIT %s OFFSET %s""", (item_num_per_page, offset))
        
        results = cursor.fetchall()
        cursor.execute("""SELECT COUNT(*) FROM product_type WHERE is_active = 1""")
        total = cursor.fetchone()[0]

    else:
        if len(product_name) > 0 and category_id == "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.is_active = 1 AND pt.product_type_name = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (product_name, item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pt.is_active = 1 AND 
                            pt.product_type_name = %s""", (product_name,))
            total = cursor.fetchone()[0]

        elif len(product_name) > 0 and category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.is_active = 1 AND pc.category_id = %s and pt.product_type_name = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (category_id, product_name, item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pt.is_active = 1 AND pc.category_id = %s
                           and pt.product_type_name = %s""", (category_id, product_name,))
            total = cursor.fetchone()[0]
        
        elif category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.is_active = 1 AND pc.category_id = %s
                ORDER BY pt.product_type_id
                LIMIT %s OFFSET %s""", (category_id, item_num_per_page, offset))     

            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pt.is_active = 1 AND pc.category_id = %s""", (category_id,))
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


def User (email, password, depot_id,first_name, last_name, address, phone, dob, isrural):
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
            INSERT INTO user_profile (user_id, first_name, last_name, address, phone_number, date_of_birth, is_rural)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, address, phone, dob, isrural))
    
    cursor.close()
    
    customer_name = first_name + " " + last_name
    #sender = 11 (national manager/administrator)
    send_message(11, user_id, "Welcome to Fresh Harvest Delivery {},  We're thrilled to have you join our community of fresh produce enthusiasts. Get ready to experience the convenience of farm-fresh goodness delivered right to your doorstep. Whether you're craving a vibrant salad, succulent fruits, or wholesome veggies, we've got you covered.".format(customer_name), 1, depot_id)
    
    return User
    
def get_user_full_name(user_id):
    conn = getCursor()
    # Get the user info from db
    conn.execute('SELECT first_name, last_name FROM user_profile WHERE user_id = %s', (user_id,))
    user = conn.fetchone()
    name = f'{user[0]} {user[1]}'
    conn.close()
    return name if name else None


def insert_payment(order_hdr_id, grandtotal, payment_method_id, payment_date):
    user_id = session['user_id']
    cursor = getCursor()
    cursor.execute("INSERT INTO payment (order_hdr_id, amount, payment_method_id, payment_date) VALUES (%s, %s, %s, %s)",
                (order_hdr_id, grandtotal, payment_method_id, payment_date))
    payment_id = cursor.lastrowid

    # Get the product_id and the quantity, we need to decrease the stock
    product_quantity_dict = get_consumed_product_quantity(order_hdr_id, cursor)
    # Adjust product quantity
    update_product_stock_db(product_quantity_dict, cursor)

    cursor.execute("INSERT INTO depot_order (order_hdr_id, depot_id) VALUES (%s, %s)",(order_hdr_id, session['user_depot']))    
    cursor.close()

    send_message(11, user_id, "Your order #{} is confirmed. We know you are eager to receive your new purchase and we wll do our best to process your order as soon as possible.".format(order_hdr_id), 1)
    return payment_id


def update_payment(order_hdr_id, grandtotal, payment_date):
    user_id = session['user_id']
    cursor = getCursor()
    payment_id = 0
    cursor.execute("""SELECT payment_id FROM payment WHERE order_hdr_id = %s""", (order_hdr_id,))
    result = cursor.fetchone()
    if result:
        payment_id = result[0]
        cursor.execute("""UPDATE payment SET amount = %s, payment_date = %s WHERE payment_id = %s""", (grandtotal, payment_date, payment_id))

        cursor.close()
        send_message(11, user_id, "Your order #{} is confirmed. We know you are eager to receive your new purchase and we wll do our best to process your order as soon as possible.".format(order_hdr_id), 1)
    return payment_id


def generate_invoice_db(invoice_num, order_hdr_id, payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee):
    cursor = getCursor()
    # Check if there's an existing invoice associated with the order_hdr, update if yes, otherwise insert
    cursor.execute("""SELECT invoice_id FROM invoice WHERE order_hdr_id = %s""", (order_hdr_id,))
    result = cursor.fetchone()
    if result:
        invoice_id = result[0]
        cursor.execute("""UPDATE invoice SET payment_id = %s, date_issued = CURDATE(), subtotal_amount = %s, gst_amount = %s, 
                       total_amount = %s, shipping_fee=%s WHERE invoice_id = %s""", (payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee, invoice_id))
    else:
        # Note that gst_rate_id is hard coded 1 as it's a locla NZ business for now
        cursor.execute(
            """INSERT INTO invoice (invoice_num, order_hdr_id, payment_id, date_issued, subtotal_amount, gst_amount, total_amount, gst_rate_id, shipping_fee)
            VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, 1, %s)""", (invoice_num, order_hdr_id, payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee))
        invoice_id = cursor.lastrowid
    cursor.close()
    return invoice_id

def create_order(grandtotal, cart_items):
    conn = getCursor()
    user_id = session['user_id']

    shipping_option_id = 1 #default to standard shipping
    conn.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (user_id ,))
    is_rural = conn.fetchone()[0]

    if is_rural:
        shipping_option_id = 2 #rural shipping

    conn.execute(
        """INSERT INTO order_hdr (user_id, order_date, total_price, status_id, shipping_option_id) VALUES (%s, CURDATE(), %s, %s, %s)""",
        (user_id, grandtotal, 1, shipping_option_id))
    order_hdr_id = conn.lastrowid

    for product_id, details in cart_items.items():
        item_info = details['item_info']
        quantity = item_info['quantity']
        line_total = details['line_total']
        conn.execute(
        """INSERT INTO order_detail (order_hdr_id, product_id, quantity, line_total_price) VALUES (%s, %s, %s, %s)""", 
        (order_hdr_id, product_id, quantity, line_total))
    conn.close()
    return order_hdr_id


def add_product_weight_by_id(weight, unit):
    cursor = getCursor()
    cursor.execute("""INSERT INTO product_weight (weight, unit) VALUES (%s, %s)""", (weight, unit))
    cursor.close()


def unit_exists_check(weight, unit):
    cursor = getCursor()
    try:
        if weight is None:
            cursor.execute("""
                SELECT product_weight_id FROM product_weight WHERE weight IS NULL AND unit = %s
            """, (unit,))
        else:
            cursor.execute("""
                SELECT product_weight_id FROM product_weight WHERE weight = %s AND unit = %s
            """, (weight, unit))
        
        if cursor.fetchone():
            return True
        return False
    finally:
        cursor.close()


def delete_product_weight_by_id(product_weight_id):
    cursor = getCursor()
    cursor.execute("""delete from product_weight where product_weight_id=%s""", 
                       (product_weight_id,))
    cursor.close()


def update_product_weight(product_weight_id, weight, unit):
    cursor = getCursor()
    cursor.execute("""UPDATE product_weight SET weight=%s, unit=%s WHERE product_weight_id=%s""",
                   (weight, unit, product_weight_id))
    cursor.close()


def get_all_messages_by_user_id():

    user_id = session['user_id']
    user_role_id = session['user_role_id']

    cursor = getCursor()

    # Fetch all messages based on user_role
    #if the user is a customer, return all messages 
    if user_role_id in (1, 2):
        cursor.execute("""select * from message a
                            inner join message_category b on a.message_category_id = b.message_category_id
                            WHERE receiver_id =  %s order by sent_time desc""", (user_id,))
    #if user is staff, return all the messages that is for the staff group ()
    elif user_role_id == 3:
        cursor.execute("""select * from message a
                            inner join message_category b on a.message_category_id = b.message_category_id
                            WHERE receiver_id in ('3') 
                            and message_status_id ='1' and depot_id = %s
                            order by sent_time desc;""", (session['user_depot'],))
    
    elif user_role_id == 4:
        cursor.execute("""select * from message a
                            inner join message_category b on a.message_category_id = b.message_category_id
                            inner join message_status c on a.message_status_id = c.message_status_id     
                             WHERE receiver_id in ('3','4') 
                            and depot_id = %s
                            order by sent_time desc;""", (session['user_depot'],))

    elif user_role_id == 5:
        cursor.execute("""select * from message a
                            inner join message_category b on a.message_category_id = b.message_category_id
                            WHERE receiver_id in ('3','4') 
                            and message_status_id='1' order by sent_time desc;""")
        
    messages = cursor.fetchall()
    cursor.close()

    modified_messages = []

    # Loop through each message in the messages list
    for message in messages:
        # Extract sender's ID from the message tuple
        sender_id = message[1]
        # Get sender's full name
        if sender_id == 11:
            sender_full_name = "Administrator"
        else:
            sender_full_name = get_user_full_name(sender_id)
        # Convert the message tuple to a list
        message_list = list(message)
        # Append sender's full name to the list
        message_list.append(sender_full_name)
        # Convert the list back to a tuple
        modified_message = tuple(message_list)
        # Append the modified message tuple to the new list
        modified_messages.append(modified_message)

    return modified_messages

def send_message(sender_id, receiver_id, content, message_category_id, user_depot=""):

    if user_depot == "":
        user_depot = session['user_depot']
    
    cursor = getCursor()

    cursor.execute(
        """INSERT INTO message (sender_user_id, receiver_id, content, sent_time, message_status_id, message_category_id,depot_id) VALUES (%s, %s, %s, Now(), 1, %s, %s)""",
        (sender_id, receiver_id, content, message_category_id, user_depot))
    
    cursor.close()


def delete_message_by_id(message_id):
    cursor = getCursor()

    cursor.execute("""DELETE FROM message WHERE message_id =%s""",
                       (message_id,))
    cursor.close()


def get_products_by_user_depot(user_depot, page=None, per_page=None, status_filter=''):
    cursor = getCursor()
    user_depot = session.get('user_depot')
    
    query = """SELECT   pt.product_type_name, 
                        p.orig_price, 
                        p.stock_quantity,
                        CONCAT(pw.weight, ' ', pw.unit) AS weight_unit,
                        CASE 
                            WHEN p.stock_quantity = 0 THEN 'Unavailable'
                            WHEN p.stock_quantity <= 20 THEN 'Low'
                            ELSE 'Available'
                        END AS status,
                        p.product_id
                    FROM product p
                    JOIN product_type pt ON p.product_type_id = pt.product_type_id
                    JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
                    WHERE p.is_active = 1 AND p.depot_id = %s"""

    params = [user_depot]

    if status_filter:
        query += " AND CASE WHEN p.stock_quantity = 0 THEN 'Unavailable' WHEN p.stock_quantity <= 20 THEN 'Low' ELSE 'Available' END = %s"
        params.append(status_filter)
    
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
    
    try:
        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return [], 0
    
    if page is not None and per_page is not None:
        count_query = """SELECT COUNT(*) FROM product WHERE is_active = 1 AND depot_id = %s"""
        if status_filter:
            count_query += " AND CASE WHEN stock_quantity = 0 THEN 'Unavailable' WHEN stock_quantity <= 20 THEN 'Low' ELSE 'Available' END = %s"
            cursor.execute(count_query, (user_depot, status_filter))
        else:
            cursor.execute(count_query, (user_depot,))
        total_products = cursor.fetchone()[0]
        cursor.close()
        return products, total_products
    else:
        cursor.close()
        return products

def edit_product(product_id):
    cursor = getCursor()
    query = """
        SELECT  p.product_id, 
                pt.product_type_name, 
                p.orig_price, 
                p.stock_quantity,
                CASE WHEN p.stock_quantity > 0 THEN 'Available' ELSE 'Unavailable' END AS status
        FROM product p
        JOIN product_type pt ON p.product_type_id = pt.product_type_id
        WHERE p.product_id = %s
    """
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    
    return product


def get_order_details_by_invoice_id(invoice_id):
    cursor = getCursor()
    order_details = []
    try:

        query = """
                SELECT od.order_hdr_id, od.product_id, od.quantity, od.line_total_price, 
                        p.product_type_id, p.orig_price, pt.product_type_name, 
                        CONCAT(pw.weight, ' ', pw.unit) AS unit
                FROM order_detail od
                JOIN product p ON od.product_id = p.product_id
                JOIN product_type pt ON p.product_type_id = pt.product_type_id
                JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
                WHERE od.order_hdr_id IN (SELECT order_hdr_id FROM invoice WHERE invoice_id = %s)
            """
        cursor.execute(query, (invoice_id,))
        
        rows = cursor.fetchall()

        for row in rows:
            product_name = row[6]
            price = row[5]
            quantity = row[2]
            subtotal = price * quantity
            unit = row[7]

            order_detail = {
                'product_name': product_name,
                'unit': unit,
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            }

            order_details.append(order_detail)

    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return order_details


def get_depot_addr_by_name(name):
    cursor = getCursor()
    query = "SELECT address FROM depot WHERE depot_name = %s"
    cursor.execute(query, (name,))
    address = cursor.fetchone()[0]
    return address


def get_user_addr_by_id(id):
    cursor = getCursor()
    query = "SELECT address FROM user_profile WHERE user_id = %s"
    cursor.execute(query, (id,))
    address = cursor.fetchone()[0]
    return address

 
def insert_account_holder(business_name, business_address, business_phone):
    
    cursor = getCursor()

    cursor.execute(
        """INSERT INTO account_holder (business_name, business_address, business_phone, user_id, credit_account_id, isApproved) 
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (business_name, business_address, business_phone, session['user_id'], 1, False))
    
    cursor.close()
    
    send_message(11, session['user_id'], "Thank you for submitting your application to become an account holder. We have received it successfully. Our team will now review your application thoroughly. You will receive a notification once the review process is complete. We appreciate your patience.", 1)
    


def account_holder_exists_check():
    cursor = getCursor()
    # Get the user account holder info from db
    cursor.execute('SELECT * FROM account_holder WHERE user_id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    return user


def get_user_orders():
    user_id = session['user_id']
    cursor = getCursor()
    cursor.execute(
        """SELECT oh.order_hdr_id, oh.order_date, oh.total_price, os.status_name, so.shipping_option_name, oh.status_id
        FROM order_hdr oh 
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        WHERE user_id = %s AND oh.is_active = 1
        ORDER BY oh.status_id ASC, oh.order_date DESC, oh.order_hdr_id DESC""", (user_id,))

    result = cursor.fetchall()
    cursor.close()
    return result


def get_order_details_by_id(order_id):
    cursor = getCursor()
    cursor.execute("""SELECT pt.product_image, pt.product_type_name, p.orig_price, od.quantity, od.line_total_price, pw.weight, pw.unit,
                   p.product_id, oh.status_id FROM order_hdr oh
                   INNER JOIN order_detail od ON oh.order_hdr_id = od.order_hdr_id
                   INNER JOIN product p ON p.product_id = od.product_id
                   INNER JOIN product_type pt ON pt.product_type_id = p.product_type_id
                   INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
                   WHERE oh.order_hdr_id = %s""", (order_id,))
    results = cursor.fetchall()
    items = []
    can_modify = True
    can_cancel = True
    # Decode image and create a list of item
    for item in results:
        item_list = list_with_decoded_image(item, 0)
        items.append(item_list)

    # We can check any of the last element of the item in the list, should be the same as status_id in order_hdr table
    if int(items[0][-1]) > 1:
        can_modify = False
    
    if int(items[0][-1]) > 2:
        can_cancel = False 

    cursor.execute("""SELECT total_amount, gst_amount, subtotal_amount FROM order_hdr oh
                    INNER JOIN invoice i ON i.order_hdr_id = oh.order_hdr_id 
                   WHERE oh.order_hdr_id = %s""", (order_id,))
    invoice_info = cursor.fetchone()
    cursor.close()
    return items, invoice_info, can_modify, can_cancel


def category_exists_check(category_name):
    cursor = getCursor()
    # Check if the category name is already in the db, if yes, return the row
    cursor.execute("""SELECT * FROM product_category where category_name = %s""", (category_name,))
    categories = cursor.fetchall()
    cursor.close()
    return categories

def insert_product_category(category_name, status):
    cursor = getCursor()
    cursor.execute(
    """INSERT INTO product_category (category_name, is_active) 
    VALUES (%s, %s)""",
    (category_name, status))
    
    cursor.close()

def get_product_category_by_id(category_id):
    cursor = getCursor()
    # return the category detail to the caller based on the category id
    cursor.execute("""SELECT * FROM product_category where category_id = %s""", (category_id,))
    category = cursor.fetchone()
    cursor.close()
    return category

def update_product_category(category_id, category_name, status):
    cursor = getCursor()
    # update the product category
    cursor.execute("""update product_category set category_name = %s, is_active = %s
                         where category_id = %s""", (category_name, status, category_id,))

    cursor.close()

def delete_product_category(category_id):
    cursor = getCursor()
    # delete the product category
    cursor.execute("""delete from product_category where category_id = %s""", (category_id,))

    cursor.close()


def get_invoice_date_and_num(invoice_id):
    cursor = getCursor()
    query = "SELECT date_issued, invoice_num FROM invoice WHERE invoice_id = %s"
    cursor.execute(query, (invoice_id,))
    result = cursor.fetchone()
    cursor.close()
    date_issued = result[0]
    invoice_num = result[1]
    return date_issued, invoice_num


def cancel_order_by_id(order_hdr_id):
    cursor = getCursor()
    # Set order_hdr to inactive
    cursor.execute("UPDATE order_hdr SET is_active = 0, status_id = 5 WHERE order_hdr_id = %s", (order_hdr_id,))

    # Get the product_id and the quantity, we need to add the stock back
    product_quantity_dict = get_consumed_product_quantity(order_hdr_id, cursor)
    # Adjust product quantity
    update_product_stock_db(product_quantity_dict, cursor, decrease=False)

    # Delete payment and invoice
    cursor.execute("SELECT invoice_id FROM invoice WHERE order_hdr_id = %s", (order_hdr_id,))
    invoice_id = cursor.fetchone()
    if invoice_id:
        cursor.execute("DELETE FROM invoice WHERE order_hdr_id = %s", (order_hdr_id,))
        cursor.execute("DELETE FROM payment WHERE order_hdr_id = %s", (order_hdr_id,))
    cursor.close()


def get_consumed_product_quantity(order_hdr_id, cursor):
    cursor.execute("""SELECT product_id, quantity FROM order_detail WHERE order_hdr_id = %s""", (order_hdr_id,))
    results = cursor.fetchall()
    # Convert the results to a dictionary
    product_quantity_dict = {product_id: quantity for product_id, quantity in results}
    return product_quantity_dict


def get_all_orders(depot_id=None):
    cursor = getCursor()
    query = """
        SELECT do.depot_orderid, oh.order_hdr_id, up.first_name, up.last_name, oh.order_date, oh.total_price, oh.status_id, os.status_name, so.shipping_option_name, do.depot_id
        FROM order_hdr oh
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        INNER JOIN user_profile up ON oh.user_id = up.user_id
        INNER JOIN depot_order do ON oh.order_hdr_id = do.order_hdr_id
    """
    if depot_id:
        query += " WHERE do.depot_id = %s"
        cursor.execute(query, (depot_id,))
    else:
        cursor.execute(query)
    
    orders = cursor.fetchall()
    cursor.close()
    return orders


def update_order_status_by_depot_orderid(depot_orderid, status_id):
    cursor = getCursor()
    query = """
        UPDATE order_hdr
        SET status_id = %s
        WHERE order_hdr_id = (SELECT order_hdr_id FROM depot_order WHERE depot_orderid = %s)
    """
    cursor.execute(query, (status_id, depot_orderid))
    cursor.close()


def get_order_details(order_hdr_id):
    cursor = getCursor()
    query = """
        SELECT od.order_detail_id, pt.product_type_name, CONCAT(pw.weight, ' ', pw.unit) AS product_weight, od.quantity, od.line_total_price, p.orig_price
        FROM order_detail od
        INNER JOIN product p ON od.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        WHERE od.order_hdr_id = %s
    """
    cursor.execute(query, (order_hdr_id,))
    order_details = cursor.fetchall()
    cursor.close()
    return order_details


def get_customer_info(order_hdr_id):
    cursor = getCursor()
    query = """
        SELECT up.first_name, up.last_name, up.phone_number, up.address, oh.order_date, oh.total_price, so.shipping_option_name
        FROM order_hdr oh
        INNER JOIN user_profile up ON oh.user_id = up.user_id
        INNER JOIN shipping_option so ON oh.shipping_option_id = so.shipping_option_id
        WHERE oh.order_hdr_id = %s
    """
    cursor.execute(query, (order_hdr_id,))
    customer_info = cursor.fetchone()
    cursor.close()
    return customer_info


# Actually goes to db and updated the product quantity
# quantity_diffs is a collection id dict of product_id as key and quantity as value
def update_product_stock_db(quantity_diffs, cursor, decrease = True):
    symbol = "-" if decrease else "+"
    update_product_query = f"UPDATE product SET stock_quantity = stock_quantity {symbol} %s WHERE product_id = %s"
    for key, value in quantity_diffs.items():
        product_id = int(key)
        quantity_diff = int(value)
        cursor.execute(update_product_query, (quantity_diff, product_id))

# Calculated the quantity diff and then update in db
def update_product_stock(old_dict, new_dict, cursor):

    # Get a set of all product IDs from both dictionaries
    all_product_ids = set(old_dict.keys()).union(set(new_dict.keys()))
    
    # Calculate the quantity differences
    quantity_diffs = {}
    for product_id in all_product_ids:
        old_quantity = old_dict.get(product_id, 0)
        new_quantity = new_dict.get(product_id, 0)
        quantity_diffs[product_id] = int(new_quantity - old_quantity)
    # Update product stock accordingly
    update_product_stock_db(quantity_diffs, cursor)
  

def get_current_user_depot_id():
    cursor = getCursor()
    cursor.execute("SELECT depot_id FROM user WHERE user_id = %s", (session['user_id'],))
    depot_id = cursor.fetchone()[0]
    cursor.close()
    return depot_id


def modify_order_by_id(items, order_hdr_id, grandtotal):
    user_id = session['user_id']
    cursor = getCursor()

    # Get old product_id and quantity from order_detail
    old_product_quantity = get_consumed_product_quantity(order_hdr_id, cursor)

    # update order_detail 
    for key, value in items.items():
        product_id = key
        line_total = value['line_total']
        quantity = value['quantity']
        cursor.execute(""" UPDATE order_detail SET line_total_price = %s, quantity = %s
                       WHERE order_hdr_id = %s AND product_id = %s """, 
                       (line_total, quantity, order_hdr_id, product_id))
    
    cursor.execute(""" UPDATE order_hdr SET total_price = %s WHERE order_hdr_id = %s AND user_id = %s """, 
                   (grandtotal, order_hdr_id, user_id))
    
    # Get new product_id and quantity from order_detail
    new_product_quantity = get_consumed_product_quantity(order_hdr_id, cursor)

    update_product_stock(old_product_quantity, new_product_quantity, cursor)
    cursor.close()


def get_payment_diff(grandtotal, order_hdr_id):
    cursor = getCursor()
    # Calculate payment difference
    cursor.execute("""SELECT SUM(amount) FROM payment WHERE order_hdr_id = %s""", (order_hdr_id,)) 
    result = cursor.fetchone()
    cursor.close()
    paid = result[0]
    payment_amount_diff = float(grandtotal) - float(paid)
    return payment_amount_diff


def update_product(product_id, new_price, new_quantity):
    cursor = getCursor()

    update_query = """
        UPDATE product
        SET orig_price = %s, stock_quantity = %s
        WHERE product_id = %s
    """
    cursor.execute(update_query, (new_price, new_quantity, product_id))
    cursor.close()


def get_order_hdr_and_user_id(depot_orderid):
    cursor = getCursor()

    cursor.execute("""SELECT order_hdr_id, user_id FROM order_hdr
                     WHERE order_hdr_id = (select order_hdr_id from depot_order
                        WHERE depot_orderid = %s)""", (depot_orderid,))
    result = cursor.fetchone()
    cursor.close()
    order_hdr_id = result[0]
    user_id = result[1]
    return order_hdr_id, user_id


def get_order_receipts():
    user_id = session['user_id']
    cursor = getCursor()
    cursor.execute(
        """SELECT oh.order_hdr_id, oh.order_date, oh.total_price, os.status_name, so.shipping_option_name, i.invoice_num, i.invoice_id
        FROM order_hdr oh 
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        LEFT JOIN invoice i ON oh.order_hdr_id = i.order_hdr_id
        WHERE oh.user_id = %s 
        ORDER BY oh.order_date DESC""", (user_id,))
    result = cursor.fetchall()
    cursor.close()
    return result


def get_order_status_by_id(order_hdr_id):
    cursor = getCursor()
    cursor.execute("""SELECT status_id FROM order_hdr WHERE order_hdr_id = %s""", (order_hdr_id,))
    result = cursor.fetchone()
    cursor.close()
    return int(result[0])


def get_local_manager_id_for_user_id(user_depot_id):
    cursor = getCursor()
    cursor.execute("""SELECT user_id FROM user WHERE depot_id = %s AND role_id = 4 AND is_active = 1""", (user_depot_id,))
    result = cursor.fetchall()
    cursor.close()
    return result[0]

def get_national_manager_id():
    cursor = getCursor()
    cursor.execute("""SELECT user_id FROM user WHERE role_id = 5 AND is_active = 1""")
    result = cursor.fetchall()
    cursor.close()
    return result[0]


def get_all_shipping_option_list():
    cursor = getCursor()
    # return all the shipping option to the caller based on the category id
    cursor.execute("""SELECT * FROM shipping_option """)
    shipping_option = cursor.fetchall()
    cursor.close()
    return shipping_option


def shipping_option_exists_check(shipping_option_name):
    cursor = getCursor()
    # Check if the category name is already in the db, if yes, return the row
    cursor.execute("""SELECT * FROM shipping_option where shipping_option_name = %s""", (shipping_option_name,))
    shipping_option = cursor.fetchall()
    cursor.close()
    return shipping_option

def insert_shipping_option(shipping_option_name, price, status):
    cursor = getCursor()
    cursor.execute(
    """INSERT INTO shipping_option (shipping_option_name, price, is_active) 
    VALUES (%s, %s, %s)""",
    (shipping_option_name, price, status))
    
    cursor.close()

def get_shipping_option_name_by_id(shipping_option_id):
    cursor = getCursor()
    # return the shipping option to the caller based on the category id
    cursor.execute("""SELECT * FROM shipping_option where shipping_option_id = %s""", (shipping_option_id,))
    category = cursor.fetchone()
    cursor.close()
    return category

def update_shipping_option(shipping_option_id, shipping_option_name, price, status):
    cursor = getCursor()
    # update the shipping option
    cursor.execute("""update shipping_option set shipping_option_name = %s, price = %s, is_active = %s
                         where shipping_option_id = %s""", (shipping_option_name, price, status, shipping_option_id,))

    cursor.close()

def delete_shipping_option_by_id(shipping_option_id):
    cursor = getCursor()
    # delete the shipping option
    cursor.execute("""delete from shipping_option where shipping_option_id = %s""", (shipping_option_id,))

    cursor.close()

def get_all_product():
    cursor = getCursor()
    query = """SELECT   pt.product_type_name, 
                        p.orig_price, 
                        p.stock_quantity,
                        CONCAT(pw.weight, ' ', pw.unit) AS weight_unit,
                        CASE 
                            WHEN p.stock_quantity = 0 THEN 'Unavailable'
                            WHEN p.stock_quantity <= 20 THEN 'Low'
                            ELSE 'Available'
                        END AS status,
                        p.product_id,
                        d.depot_name  -- Make sure to select the depot name
                    FROM product p
                    JOIN product_type pt ON p.product_type_id = pt.product_type_id
                    JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
                    JOIN depot d ON p.depot_id = d.depot_id  -- Join with depots table
                    WHERE p.is_active = 1"""

    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()

    return products


def add_new_product(orig_price, stock_quantity, depot_id, product_type_id, is_active):
    cursor = getCursor()
    cursor.execute("""INSERT INTO product (orig_price, stock_quantity, depot_id, product_type_id, promotion_type_id, is_active) VALUES
                       (%s, %s, %s, %s, NULL, %s)""", (orig_price, stock_quantity, depot_id, product_type_id, is_active))
    product_id = cursor.lastrowid
    cursor.close()
    return product_id

def get_box_price_by_box_size_id(box_size_id):
    cursor = getCursor()
    cursor.execute("""SELECT price FROM box_size WHERE box_size_id = %s """, (box_size_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def add_new_box(product_id, box_size_id, box_start_date, box_end_date, is_active):
    cursor = getCursor()
    cursor.execute("""INSERT INTO box (product_id, box_size_id, box_start_date, box_end_date, is_active) VALUES 
                   (%s, %s, %s, %s, %s)""", (product_id, box_size_id, box_start_date, box_end_date, is_active))
    box_id = cursor.lastrowid
    cursor.close()
    return box_id


def set_box_and_its_product_active(box_id):
    cursor = getCursor()
    cursor.execute("SELECT product_id FROM box WHERE box_id = %s", (box_id,))
    product_id = cursor.fetchone()[0]
    cursor.execute("UPDATE product SET is_active = 1 WHERE product_id = %s", (product_id,))
    cursor.execute("UPDATE box SET is_active = 1 WHERE box_id = %s", (box_id,))
    cursor.close()


def delete_inactive_product_box(box_id):
    cursor = getCursor()
    try:
        # Get the product_id associated with the box
        cursor.execute("SELECT product_id FROM box WHERE box_id = %s", (box_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No product found for box_id: {box_id}")
        product_id = result[0]
        
        # Get the product_type_id associated with the product
        cursor.execute("SELECT product_type_id FROM product WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No product type found for product_id: {product_id}")
        product_type_id = result[0]

        # Delete the product type
        cursor.execute("DELETE FROM product_type WHERE product_type_id = %s", (product_type_id,))
        # Delete the product
        cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
        # Delete the box
        cursor.execute("DELETE FROM box WHERE box_id = %s", (box_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()


def get_account_holder_info_by_userid(user_id):
    cursor = getCursor()
    cursor.execute("""
                SELECT ah.account_holder_id, ah.business_name, ah.business_address, ah.business_phone, ah.user_id, ah.credit_account_id, ca.credit_limit, u.depot_id
                FROM account_holder ah
                JOIN user u ON ah.user_id = u.user_id
                JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
                WHERE u.user_id = %s
            """, (user_id,))
    account_holder_info = cursor.fetchone()
    cursor.close()
    return account_holder_info


def get_current_credit_limit(user_id):
    cursor = getCursor()
    cursor.execute("""
            SELECT ca.credit_limit
            FROM account_holder ah
            JOIN user u ON ah.user_id = u.user_id
            JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
            WHERE u.user_id = %s
        """, (user_id,))
    current_credit_limit = cursor.fetchone()
    cursor.close()
    return current_credit_limit[0] if current_credit_limit else None


def apply_limit_increase_to_db(user_id, depot_id, current_limit, reason, requested_limit, requested_date):
    cursor = getCursor()
    cursor.execute("""INSERT INTO credit_limit_change_request (user_id, depot_id, current_limit, reason, requested_limit, requested_date) 
                   VALUES (%s, %s, %s, %s, %s, %s) """, (user_id, depot_id, current_limit, reason, requested_limit, requested_date))
    
    cursor.close()
    
    send_message(11, session['user_id'], "Thank you for submitting your application to increase your credit limit. We have received it successfully. Our team will now review your application thoroughly. You will receive a notification once the review process is complete. We appreciate your patience.", 1)

def get_products_by_ids(product_ids):
    cursor = getCursor()
    try:
        placeholders = ', '.join(['%s'] * len(product_ids))
        query = f"""
            SELECT p.product_id, pt.product_type_name, pt.product_image, pw.weight, pw.unit
            FROM product p 
            INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
            INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
            WHERE p.product_id IN ({placeholders})
        """
        cursor.execute(query, tuple(product_ids))
        results = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching products: {e}")
        results = []
    finally:
        cursor.close()
    
    return results


def get_current_credit_balance(user_id):
    cursor = getCursor()
    cursor.execute("""
            SELECT ca.current_balance
            FROM account_holder ah
            JOIN user u ON ah.user_id = u.user_id
            JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
            WHERE u.user_id = %s
        """, (user_id,))
    current_credit_balance = cursor.fetchone()
    cursor.close()
    return current_credit_balance[0] if current_credit_balance else None


def get_user_depot_id(user_id):
    cursor = getCursor()
    cursor.execute("SELECT depot_id FROM user WHERE user_id = %s", (user_id,))
    depot_id = cursor.fetchone()
    cursor.close()
    return depot_id[0] if depot_id else None


def get_customer_shipping_fee():
    cursor = getCursor()
    cursor.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (session['user_id'] ,))
    is_rural = cursor.fetchone()[0]

    if is_rural:
        cursor.execute("""SELECT price FROM shipping_option WHERE shipping_option_id = '2'""")
    else:
        cursor.execute("""SELECT price FROM shipping_option WHERE shipping_option_id = '1'""")

    shipping_fee = cursor.fetchone()[0]
    cursor.close()
    return shipping_fee


def check_low_stock_product_by_all():
    products = get_all_product()
    low_stock_depots = {product[-1] for product in products if product[2] < 20}  # Using a set to avoid duplicates
    return list(low_stock_depots)


def get_pending_requests(depot_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT ah.account_holder_id, CONCAT(up.first_name, ' ', up.last_name) AS user_name, ah.business_name, DATE_FORMAT(CURDATE(), '%Y-%m-%d') as date 
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN user u ON up.user_id = u.user_id
        WHERE ah.isApproved = FALSE AND u.depot_id = %s
    """, (depot_id,))
    requests = cursor.fetchall()
    cursor.close()
    return requests


def get_request_details(request_id):
    cursor = getCursor()
    cursor.execute("""
        SELECT ah.account_holder_id, CONCAT(up.first_name, ' ', up.last_name) AS user_name, 
               ah.business_name, ah.business_address, ah.business_phone, 
               ah.credit_account_id, ah.isApproved, d.depot_name as depot_name
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN user u ON up.user_id = u.user_id
        JOIN depot d ON u.depot_id = d.depot_id
        WHERE ah.account_holder_id = %s
    """, (request_id,))
    request = cursor.fetchone()
    cursor.close()
    return request



def get_credit_limit(credit_limit):
    cursor = getCursor()
    # Insert into credit_account table
    cursor.execute("INSERT INTO credit_account (credit_limit, current_balance) VALUES (%s, 0.00)", (credit_limit,))
    credit_account_id = cursor.lastrowid
    cursor.close()
    return credit_account_id


def update_account_holder(account_holder_id, credit_account_id):
    cursor = getCursor()
    cursor.execute("UPDATE account_holder SET credit_account_id = %s, isApproved = TRUE WHERE account_holder_id = %s", (credit_account_id, account_holder_id))
    cursor.close()

def update_account_holder_current_balance(current_balance, user_id):
    cursor = getCursor()
    cursor.execute("""UPDATE credit_account ca INNER JOIN account_holder ah ON ca.credit_account_id = ah.credit_account_id
                    SET ca.current_balance = %s WHERE ah.user_id = %s;""", (current_balance, user_id))
    cursor.close()

def get_user_id_from_account_holder(account_holder_id):
    cursor = getCursor()
    cursor.execute("SELECT user_id FROM account_holder WHERE account_holder_id = %s", (account_holder_id,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id


def update_user_role(user_id, new_role_id):
    cursor = getCursor()
    cursor.execute("UPDATE user SET role_id = %s WHERE user_id = %s", (new_role_id, user_id))
    cursor.close()


def reject_request(request_id):
    cursor = getCursor()
    cursor.execute("SELECT user_id FROM account_holder WHERE account_holder_id = %s", (request_id,))
    user_id = cursor.fetchone()[0]
    cursor.execute("DELETE FROM account_holder WHERE account_holder_id = %s", (request_id,))
    cursor.close()
    return get_user_full_name(user_id)


def check_low_stock_product_by_depot(depot_id):
    products = get_products_by_user_depot(depot_id)
    return any(product[2] < 20 for product in products)


def get_message_categories():
    cursor = getCursor()
    cursor.execute("select * from message_category where message_category_id != '1'")
    message_categories = cursor.fetchall()
    cursor.close()
    return message_categories

def get_message_by_id(message_id):
    cursor = getCursor()
    cursor.execute("""select * from message a
                        inner join message_category b on a.message_category_id = b.message_category_id
                        WHERE message_id =  %s order by sent_time asc""", (message_id,))
    message = cursor.fetchone()
    cursor.close()

    modified_messages = []

    if message:
        sender_id = message[1]
        if sender_id == 11:
            sender_full_name = "Administrator"
        else:
            sender_full_name = get_user_full_name(sender_id)

        message_list = list(message)
        message_list.append(sender_full_name)
        modified_message = tuple(message_list)

        return [modified_message]


def get_all_weekly_boxes(depot_id):
    cursor = getCursor()
    cursor.execute("""SELECT box.box_id, box.product_id, 
                   DATE_FORMAT(box_start_date, '%d-%m-%Y') as box_start_date, 
                   DATE_FORMAT(box_end_date, '%d-%m-%Y') as box_end_date, box_size.size_name, 
                      box_size.price, product_type.product_type_name
                      FROM box 
                      INNER JOIN box_size ON box.box_size_id = box_size.box_size_id 
                      INNER JOIN product ON box.product_id = product.product_id 
                      INNER JOIN product_type ON product.product_type_id = product_type.product_type_id
                      WHERE box.is_active = 1 
                      AND product.depot_id = %s
                      AND box_start_date <= CURDATE() 
                      AND box_end_date >= CURDATE() 
                      AND YEARWEEK(box_start_date, 1) = YEARWEEK(CURDATE(), 1) 
                      AND YEARWEEK(box_end_date, 1) = YEARWEEK(CURDATE(), 1);""", (depot_id,))
    results = cursor.fetchall()
    cursor.close()
    return results


def get_box_details_by_id(box_id):
    cursor = getCursor()
    # Query to get box content details and related product information
    cursor.execute("""
        SELECT p.product_id, pt.product_type_name, pt.product_image, pw.weight, pw.unit, bc.quantity FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        WHERE bc.box_id = %s""", (box_id,))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_box_product_quantity_by_id(box_id):
    cursor = getCursor()
    # Query to get product quantities in the box
    cursor.execute("""
        SELECT p.product_id, bc.quantity FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        WHERE bc.box_id = %s""", (box_id,))
    results = cursor.fetchall()
    cursor.close()

    # Create a dictionary with product_id as the key and quantity as the value
    product_quantities = {str(row[0]): row[1] for row in results}
    return product_quantities
   
def delete_single_content_from_box(item_product_id, box_id):
    cursor = getCursor()
    cursor.execute("DELETE FROM box_content WHERE product_id = %s AND box_id = %s", (item_product_id, box_id))
    cursor.close()


def delete_all_box_content_by_box_id(box_id):
    cursor = getCursor()
    cursor.execute("DELETE FROM box_content WHERE box_id = %s", (box_id,))
    cursor.close()


def get_box_product_name_by_box_id(box_id):
    cursor = getCursor()
    cursor.execute("""SELECT product_type_name FROM box b
                   INNER JOIN product p ON p.product_id = b.product_id
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id 
                   WHERE box_id = %s""", (box_id,))
    product_type_name = cursor.fetchone()[0]
    cursor.close()
    return product_type_name


def get_box_product_name_by_product_id(product_id):
    cursor = getCursor()
    cursor.execute("""SELECT product_type_name FROM product p
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id 
                   WHERE product_id = %s""", (product_id,))
    product_type_name = cursor.fetchone()[0]
    cursor.close()
    return product_type_name


def update_box_with_product_id(box_id, product_id, quantity):
    cursor = getCursor()
    cursor.execute("SELECT quantity FROM box_content WHERE box_id = %s AND product_id = %s", (box_id, product_id))
    existing_content = cursor.fetchone()

    if existing_content:
        new_quantity = quantity
        cursor.execute("UPDATE box_content SET quantity = %s WHERE box_id = %s AND product_id = %s", (new_quantity, box_id, product_id))
    else:
        cursor.execute("INSERT INTO box_content (box_id, product_id, quantity) VALUES (%s, %s, %s)", (box_id, product_id, quantity))
    cursor.close()

    
def set_box_product_to_inactive(box_id):
    cursor = getCursor()
    try:
        # Get the product_id associated with the box
        cursor.execute("SELECT product_id FROM box WHERE box_id = %s", (box_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No product found for box_id: {box_id}")
        product_id = result[0]
        
        # Get the product_type_id associated with the product
        cursor.execute("SELECT product_type_id FROM product WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No product type found for product_id: {product_id}")
        product_type_id = result[0]

        # UPDATE the product type
        cursor.execute("UPDATE product_type SET is_active = 0 WHERE product_type_id = %s", (product_type_id,))
        # UPDATE the product
        cursor.execute("UPDATE product SET is_active = 0 WHERE product_id = %s", (product_id,))
        # UPDATE the box
        cursor.execute("UPDATE box SET is_active = 0 WHERE box_id = %s", (box_id,))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()


def check_remaining_credit_low():
    user_id = session.get('user_id')
    current_limit = get_current_credit_limit(user_id)
    current_balance = get_current_credit_balance(user_id)
    remaining_credit = current_limit - current_balance
    return remaining_credit <= 100

def check_low_stock_product_by_depot(depot_id):
    products = get_products_by_user_depot(depot_id)
    return any(product[2] <= 20 for product in products)

def get_all_depots():
    cursor = getCursor()
    query = "SELECT depot_id AS id, depot_name AS name FROM depot"
    cursor.execute(query)
    depots = cursor.fetchall()
    cursor.close()
    return [{'id': row[0], 'name': row[1]} for row in depots]

def get_products_by_depot_and_status(depot_id=None, status='All', page=1, per_page=10):
    cursor = getCursor()
    offset = (page - 1) * per_page
    query = """
        SELECT pt.product_type_name, p.orig_price, p.stock_quantity,
               CONCAT(pw.weight, ' ', pw.unit) AS weight_unit,
               CASE 
                   WHEN p.stock_quantity = 0 THEN 'Unavailable'
                   WHEN p.stock_quantity <= 20 THEN 'Low'
                   ELSE 'Available'
               END AS status,
               p.product_id,
               d.depot_name
        FROM product p
        JOIN product_type pt ON p.product_type_id = pt.product_type_id
        JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        JOIN depot d ON p.depot_id = d.depot_id
        WHERE p.is_active = 1
    """
    params = []

    if depot_id is not None:
        if depot_id != 0:  # Filter by specific depot
            query += " AND p.depot_id = %s"
            params.append(depot_id)

    if status != 'All':
        query += " HAVING status = %s"
        params.append(status)

    query += """
        ORDER BY
            CASE 
                WHEN pt.product_type_id > 9 THEN pt.product_type_name
                ELSE NULL
            END ASC,
            pt.product_type_id
        LIMIT %s OFFSET %s
    """
    params.extend([per_page, offset])

    cursor.execute(query, params)  # Execute query with parameters

    products = cursor.fetchall()

    # Adjust count query to account for status filtering
    count_query = "SELECT COUNT(*) FROM (SELECT p.stock_quantity, CASE WHEN p.stock_quantity = 0 THEN 'Unavailable' WHEN p.stock_quantity <= 20 THEN 'Low' ELSE 'Available' END AS status FROM product p WHERE p.is_active = 1"
    if depot_id != 0:
        count_query += " AND p.depot_id = %s"
    if status != 'All':
        count_query += " HAVING status = %s"
    count_query += ") AS subquery"

    count_params = []
    if depot_id != 0:
        count_params.append(depot_id)
    if status != 'All':
        count_params.append(status)

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]

    cursor.close()

    return products, total

def get_box_contents_by_product_id(product_id):
    
    cursor = getCursor()
    cursor.execute("""
        SELECT bc.box_id, pt.product_type_name, pw.weight, pw.unit, bc.quantity
        FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        INNER JOIN box b ON bc.box_id = b.box_id WHERE b.product_id = %s""", (product_id,))
    contents = cursor.fetchall()
    cursor.close()
    return contents


def update_message_by_id(message_id, status):
    cursor = getCursor()

    cursor.execute("""UPDATE message set message_status_id = %s WHERE message_id =%s""",
                       (status, message_id,))
    cursor.close()

def get_customer_subscription():
    user_id = session.get('user_id')
    cursor = getCursor()
    cursor.execute("""
        select a.user_box_subscription_id, b.frequency, a.subscription_quantity, sent_quantity, c.category, d.size_name, subscription_date, is_active
        from user_box_subscription a
        inner join box_frequency b on a.box_frequency_id = b.box_frequency_id
        inner join box_category c on a.box_category_id = c.box_category_id
        inner join box_size d on a.box_size_id = d.box_size_id
        where a.is_active = true and user_id = %s""", (user_id,))
    subscriptions = cursor.fetchall()
    cursor.close()
    return subscriptions

def get_box_frequency():
    cursor = getCursor()
    cursor.execute("select * from box_frequency;")
    box_frequency = cursor.fetchall()
    cursor.close()
    return box_frequency

def get_box_category():
    cursor = getCursor()
    cursor.execute("select * from box_category;")
    box_category = cursor.fetchall()
    cursor.close()
    return box_category

def create_subscription(frequency, category, size, quantity):
    user_id = session['user_id']
    cursor = getCursor()
    cursor.execute("""INSERT INTO user_box_subscription (box_frequency_id, subscription_quantity, 
                        user_id, box_category_id, box_size_id, subscription_date, sent_quantity) 
                        VALUES (%s, %s, %s, %s, %s, CURDATE(), 0)""", 
                        (frequency, quantity, user_id, category, size))
    cursor.close()


def get_all_pending_requests():
    cursor = getCursor()
    cursor.execute("""
        SELECT ah.account_holder_id, CONCAT(up.first_name, ' ', up.last_name) AS user_name, 
               ah.business_name, DATE_FORMAT(CURDATE(), '%Y-%m-%d') as date, d.depot_name 
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN user u ON up.user_id = u.user_id
        JOIN depot d ON u.depot_id = d.depot_id
        WHERE ah.isApproved = FALSE
    """)
    requests = cursor.fetchall()
    cursor.close()
    return requests

