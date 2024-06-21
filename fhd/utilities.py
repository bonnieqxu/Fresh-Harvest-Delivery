from fhd.dbconnection import getCursor
from flask import flash, session, redirect, url_for
import base64, mysql.connector
from decimal import Decimal
import datetime
from datetime import date, timedelta
from calendar import monthrange

# Contains all the shared and db methods



def check_auth(user_role):
    # Check if the user is logged in
    if not session.get('loggedin', False):
        # If not logged in, flash a message and redirect to the login page
        flash("Please login first.", "danger")
        return redirect(url_for('auth.login'))

    # Check if the user role matches the expected role for the action
    if session['user_role_id'] != user_role:
        # If the user role does not match, flash a message and redirect to the home page
        flash("Invalid action! Back to home page.", "danger")
        return redirect(url_for('main.home'))
    
    return None




def flash_form_errors(form):
    # Check if there are any form validation errors
    if form.errors:
        # Iterate over each field's error messages
        for error_messages in form.errors.values():
            # Iterate over each error message and flash it as a danger message
            for error in error_messages:
                flash(f"{error}", "danger")




def list_with_decoded_image(object_tuple, image_index):
    # Convert a tuple into a list and decode the image at the specified index.
    object_list = list(object_tuple)
    # Check if the image at the specified index exists
    if object_list[image_index]:
        # Decode the image and replace it in the list
        object_list[image_index] = base64.b64encode(
            object_list[image_index]).decode('utf-8')
    return object_list



def user_exists_with_email(email):
    # Check if a user exists with the given email
    if get_user_by_email(email):
        return True
    else:
        return False

    

# region lookup tables
def get_product_category(include_all=True):
    # Retrieve product categories from the database.
    cursor = getCursor()
    # Execute SQL query to select active product categories
    cursor.execute("""SELECT category_id, category_name FROM product_category WHERE is_active = 1""")
    categories = []
    
    # If include_all is True, add an 'All' option to the categories list
    if include_all:
        categories.append((0, 'All'))
    # Iterate over the fetched rows and append them to the categories list
    for row in cursor.fetchall():
        categories.append(row)
    cursor.close()
    return categories



def get_product_category_without_box(include_all=True):
    #  Retrieve product categories from the database excluding the 'Box' category.
    cursor = getCursor()
    # Execute SQL query to select active product categories excluding the 'Box' category
    cursor.execute("""SELECT category_id, category_name FROM product_category WHERE is_active = 1 AND category_id != 7""")
    categories = []
    # If include_all is True, add an 'All' option to the categories list
    if include_all:
        categories.append((0, 'All'))
    # Iterate over the fetched rows and append them to the categories list
    for row in cursor.fetchall():
        categories.append(row)
    cursor.close()
    return categories



def get_box_size():
    # Retrieve box sizes from the database.
    # Returns: A list of box size names.
    cursor = getCursor()
    # Execute SQL query to select box sizes
    cursor.execute("""SELECT size_name FROM box_size""")
    results = cursor.fetchall()
    cursor.close() 
    return results



def get_box_size_name_by_id(box_size_id):
    # Retrieve box size name for a box size id from the database.
    cursor = getCursor()
    # Execute SQL query to select box size name
    cursor.execute("""SELECT size_name FROM box_size WHERE box_size_id = %s""", (box_size_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0]



def get_box_size_full():
    """
    Retrieve all details of box sizes from the database.
    Returns: A list of tuples containing details of box sizes.
    """
    cursor = getCursor()
    cursor.execute("""SELECT * FROM box_size""")
    results = cursor.fetchall()
    cursor.close()
    return results



def get_gst_rate():
    """
    Retrieve the GST (Goods and Services Tax) rate from the database.
    Returns: (int) The GST rate as a percentage.
    """
    cursor = getCursor()
    cursor.execute("""SELECT percentage FROM gst_rate""")
    gst_rate = cursor.fetchone()
    cursor.close()
    # Convert the GST rate to an integer and return
    return int(gst_rate[0])



def get_product_weight(product_weight_id=None):
    """
    Retrieve product weights from the database.
    Returns:
        list: A list of tuples containing product weight details.
    """
    cursor = getCursor()
    if product_weight_id is not None:
        # If a product weight ID is provided, retrieve the specific product weight
        cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit 
                          FROM product_weight 
                          WHERE product_weight_id = %s AND is_active = 1""", (product_weight_id,))
    else:
        # If no product weight ID is provided, retrieve all active product weights
        cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit 
                          FROM product_weight 
                          WHERE is_active = 1 
                          ORDER BY unit ASC""")
    # Fetch the product weights from the database
    product_weight = cursor.fetchall()
    cursor.close()
    return product_weight



def get_product_weight_kilo_only():
    """
    Retrieve product weights measured in kilograms from the database.
    Returns: A list of tuples containing product weight details measured in kilograms.
    """
    cursor = getCursor()
    # Execute SQL query to select product weights measured in kilograms
    cursor.execute("""SELECT product_weight_id, COALESCE(weight, '') AS weight, unit 
                   FROM product_weight WHERE weight IS NOT NULL AND is_active = 1""")
    # Fetch the product weights from the database
    product_weight = cursor.fetchall()
    cursor.close()
    return product_weight



def query_depot_names():
    """
    Retrieve names of all depots from the database.
    Returns: A list of depot names.
    """
    cursor = getCursor()
    # Execute SQL query to select depot names
    cursor.execute("SELECT depot_name FROM depot")
    # Fetch the depot names from the database
    depot_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return depot_names



def depots():
    """
    Retrieve information about all depots from the database.
    Returns: A list of dictionaries containing depot IDs and names.
    """
    cursor = getCursor()
    # Execute SQL query to select depot IDs and names
    cursor.execute("SELECT depot_id, depot_name FROM depot")
    # Fetch the depots' information from the database
    depots = [{'depot_id': row[0], 'depot_name': row[1]} for row in cursor.fetchall()]
    cursor.close()
    return depots



def get_depot_name_by_id(depot_id):
    """
    Retrieve the name of a depot by its ID from the database.
    Returns: The name of the depot.
    """
    cursor = getCursor()
    # Execute SQL query to select the name of the depot by its ID
    cursor.execute("SELECT depot_name from depot WHERE depot_id = %s", (depot_id,))
    # Fetch the result from the database
    result = cursor.fetchone()
    cursor.close()

    return result[0]



def get_status_choices():
    """
    Retrieve choices for order statuses from the database.
    Returns: A list of tuples containing status IDs and names.
    """
    cursor = getCursor()
    # Execute SQL query to select status IDs and names from the order_status table
    cursor.execute("SELECT status_id, status_name FROM order_status")
    # Fetch the status choices from the database and create a list of tuples
    status_choices = [(row[0], row[1]) for row in cursor.fetchall()]
    cursor.close()
    return status_choices



def get_all_category_List():
    """
    Retrieve information about all product categories from the database.
    Returns:A list of tuples containing information about product categories.
    """
    cursor = getCursor()
    # Execute SQL query to select all product categories
    cursor.execute("""SELECT * FROM product_category;""")
    # Fetch all product categories from the database
    categories = cursor.fetchall()
    cursor.close()
    return categories



def get_product_type_by_name(product_name):
    """
    Retrieve information about a product type by its name from the database.
    Returns:A list of tuples containing information about the product type.
    """
    conn = getCursor()
    # Execute SQL query to select product type information by name
    conn.execute('SELECT * FROM product_type WHERE is_active = 1 AND product_type_name = %s', (product_name,))

    product = conn.fetchall()
    conn.close()
    return product




def get_user_by_email(email):
    """
    Retrieve information about a user by their email address from the database.
    Returns:A tuple containing information about the user.
    """
    conn = getCursor()
    # Execute SQL query to select user information by email
    conn.execute('SELECT * FROM user WHERE email = %s', (email,))

    user = conn.fetchone()
    conn.close()

    return user



def get_basic_product_info_by_id(product_id):
    """
    Retrieve basic information about a product by its ID from the database.
    Returns:A list containing basic information about the product.
    """
    cursor = getCursor()

    # Fetch product information from the product ID
    cursor.execute("""SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description 
                    FROM product p
                    INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
                    WHERE p.product_id = %s""", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    # Decode the product image and return the product information as a list
    return list_with_decoded_image(product, 2)



def get_full_product_info_by_id(product_id):
    """
    Retrieve full information about a product by its ID from the database.
    Returns:A list containing full information about the product.
    """
    cursor = getCursor()

    # Fetch full product information from the product ID, including category name
    cursor.execute("""
        SELECT pt.product_type_name, p.orig_price, pt.product_image, pt.description, d.depot_name, 
               pw.weight, pw.unit, pc.category_name, stock_quantity
        FROM product p 
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN depot d ON p.depot_id = d.depot_id
        INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
        INNER JOIN product_category pc ON pt.category_id = pc.category_id
        WHERE p.product_id = %s
    """, (product_id,))
    
    product = cursor.fetchone()
    cursor.close()
    # Decode the product image and return the product information as a list
    return list_with_decoded_image(product, 2)



def get_all_products(page_num, item_num_per_page, depot_name, category_id, size, category_name, filter_out_boxes=False):
    cursor = getCursor()

    # Calculate the offset for pagination
    offset = (page_num - 1) * item_num_per_page

    # Base SELECT clause for querying products
    select = """
    SELECT p.product_id, pt.product_type_name, p.orig_price, pt.product_image, pt.description, pw.weight, pw.unit, stock_quantity, pt.category_id
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
            box_inner_join = """ INNER JOIN box b ON b.product_id = p.product_id 
            INNER JOIN box_size bs ON b.box_size_id = bs.box_size_id
            INNER JOIN (
                SELECT DISTINCT b.product_id, b.box_size_id FROM box b INNER JOIN box_content bc ON b.box_id = bc.box_id 
                WHERE EXISTS (SELECT 1 FROM box_content bc_inner WHERE bc_inner.box_id = b.box_id)) unique_boxes 
                ON p.product_id = unique_boxes.product_id"""
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
        product_list.append(True)
        products.append(product_list)
    cursor.close()

    if category_name == "Premade Box" or category_name == "All":
        #filter out the boxes which we don't have enough stock
        for product in products:
            # product is a pre_made box
            if str(product[8]) == '7': 
                # Check stock for each box content
                id_quantity_dict = get_box_content_quantity_by_product_id(product[0])
                for key, value in id_quantity_dict.items():
                    if get_product_quantity_by_id(key) < int(value):
                        product[-1] = False

    return products, total




def get_product_quantity_by_id(product_id):
    """
    Retrieve the quantity of a product by its ID from the database.
    Returns:The quantity of the product.
    """
    cursor = getCursor()
    # Execute SQL query to select the stock quantity of the product by its ID
    cursor.execute("SELECT stock_quantity FROM product WHERE product_id = %s", (product_id,))

    result = cursor.fetchone()
    cursor.close()
    # Return the quantity of the product
    return result[0]




def add_new_product_type(image_data, product_name, product_unit, product_description, product_category):
    """
    Add a new product type to the database.
    Returns:The ID of the newly added product type.
    """
    cursor = getCursor()
    # Execute SQL query to insert a new product type into the database
    cursor.execute("""INSERT INTO product_type (product_type_name, product_weight_id, description, category_id, product_image) VALUES
                       (%s, %s, %s, %s, %s)""", 
                       (product_name, product_unit, product_description, product_category, image_data))
    # Get the ID of the newly inserted product type
    product_type_id = cursor.lastrowid
    cursor.close()

    if str(product_category) != '7':

        orig_price = 0
        stock_quantity = 0
        is_active = True

        add_new_product(orig_price, stock_quantity, 1, product_type_id, is_active)
        add_new_product(orig_price, stock_quantity, 2, product_type_id, is_active)
        add_new_product(orig_price, stock_quantity, 3, product_type_id, is_active)
        add_new_product(orig_price, stock_quantity, 4, product_type_id, is_active)
        add_new_product(orig_price, stock_quantity, 5, product_type_id, is_active)
    
    return product_type_id




def update_product_type(product_type_id, image_data, product_name, product_unit, product_description, product_category):
    # Update a product type in the database.
    cursor = getCursor()
    # Check if image data is provided
    if image_data is None:
        # Execute SQL query to update product type without changing image
        cursor.execute("""UPDATE product_type 
                          SET product_type_name=%s, product_weight_id=%s, 
                              description=%s, category_id=%s 
                          WHERE product_type_id=%s""", 
                       (product_name, product_unit, product_description, product_category, product_type_id))
    else:
        # Execute SQL query to update product type including image
        cursor.execute("""UPDATE product_type 
                          SET product_type_name=%s, product_weight_id=%s, 
                              description=%s, category_id=%s, product_image=%s 
                          WHERE product_type_id=%s""", 
                       (product_name, product_unit, product_description, product_category, image_data, product_type_id))
        
    cursor.close()




def delete_product_type_by_id(product_type_id):
    # Delete a product type from the database by its ID.
    cursor = getCursor()
    # Execute SQL query to delete the product type by its ID
    cursor.execute("""DELETE FROM product_type WHERE product_type_id=%s""", 
                       (product_type_id,))
    
    cursor.execute("""DELETE FROM product WHERE product_type_id=%s""", 
                       (product_type_id,))

    cursor.close()




def get_all_product_type(page_num, item_num_per_page, category_id = "0", product_name=""):
    """
    Retrieve a list of product types based on the provided page number, number of items per page,
    category ID, and optional product name.

    Returns: A tuple containing a list of product types and the total number of product types.
    """
    cursor = getCursor()

    if product_name is None:
        product_name = ""

    # Calculate the offset
    offset = (page_num - 1) * item_num_per_page
    if category_id == "0" and len(product_name) == 0:
        cursor.execute("""
            SELECT product_type_id, product_type_name, product_image, description
            FROM product_type WHERE is_active = 1
            ORDER BY product_type_name 
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
                WHERE pt.is_active = 1 AND pt.product_type_name LIKE  %s
                ORDER BY pt.product_type_name
                LIMIT %s OFFSET %s""", ('%' + product_name + '%', item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pt.is_active = 1 AND 
                            pt.product_type_name = %s""", ('%' + product_name + '%',))
            total = cursor.fetchone()[0]

        elif len(product_name) > 0 and category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.is_active = 1 AND pc.category_id = %s and pt.product_type_name LIKE %s
                ORDER BY pt.product_type_name
                LIMIT %s OFFSET %s""", (category_id, '%' + product_name + '%', item_num_per_page, offset))     
            
            results = cursor.fetchall()
            cursor.execute("""SELECT COUNT(*) FROM product_type pt INNER JOIN product_category pc 
                            ON pt.category_id = pc.category_id WHERE pt.is_active = 1 AND pc.category_id = %s
                           and pt.product_type_name LIKE %s""", (category_id, '%' + product_name + '%',))
            total = cursor.fetchone()[0]
        
        elif category_id != "0":
            cursor.execute("""
                SELECT pt.product_type_id, pt.product_type_name, pt.product_image, pt.description
                FROM product_type pt 
                INNER JOIN product_category pc ON pt.category_id = pc.category_id
                WHERE pt.is_active = 1 AND pc.category_id = %s
                ORDER BY pt.product_type_name
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
    """
    Retrieve product type information by its ID.
    Returns: A list containing product type information.
    """
    cursor = getCursor()

    # Fetch product information from the productid
    cursor.execute("""SELECT product_type_id, product_type_name, product_image, description, product_weight_id, category_id
                        FROM product_type pt 
                        WHERE product_type_id =  %s""", (product_type_id,))
    product = cursor.fetchone()
    cursor.close()

    return list_with_decoded_image(product, 2)




def User (email, password, depot_id,first_name, last_name, address, phone, dob, isrural):
    """
    Create a new user and insert their information into the database.
    Returns:A message indicating the result of the operation.
    """
    cursor = getCursor()
    # Check if the email already exists in the database
    cursor.execute("""
            SELECT email FROM user WHERE email = %s
        """, (email,))
    if cursor.fetchone():
            return "Email already exists."  # Exit the function and inform the user

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
    # Get the user info from the database
    conn.execute('SELECT first_name, last_name FROM user_profile WHERE user_id = %s', (user_id,))
    user = conn.fetchone()
    # Format the full name
    name = f'{user[0]} {user[1]}'
    conn.close()
    
    return name if name else None



def insert_payment(order_hdr_id, grandtotal, payment_method_id, payment_date, user_id=None):
    # If user_id is not provided, get it from the session
    if user_id is None:
        user_id = session['user_id']

    cursor = getCursor()
    
    # Insert payment details into the payment table
    cursor.execute("INSERT INTO payment (order_hdr_id, amount, payment_method_id, payment_date) VALUES (%s, %s, %s, %s)",
                   (order_hdr_id, grandtotal, payment_method_id, payment_date))
    
    # Get the ID of the last inserted row
    payment_id = cursor.lastrowid

    # Get the product_id and the quantity consumed in the order
    product_quantity_dict = get_consumed_product_quantity(order_hdr_id, cursor)
    
    update_product_stock_db(product_quantity_dict, cursor)

    adjust_box_content_product_stock(order_hdr_id, cursor)
    
    # Insert order details into the depot_order table
    cursor.execute("INSERT INTO depot_order (order_hdr_id, depot_id) VALUES (%s, %s)", (order_hdr_id, session['user_depot']))    
    
    cursor.close()

    return payment_id




def get_box_content_consumed_product_quantity(order_hdr_id, cursor):
    # Retrieve the quantity of products in the order that are categorized as boxes
    cursor.execute("""SELECT od.product_id, od.quantity FROM order_hdr oh 
                      INNER JOIN order_detail od ON oh.order_hdr_id = od.order_hdr_id 
                      INNER JOIN product p ON p.product_id = od.product_id
                      INNER JOIN product_type pt ON pt.product_type_id = p.product_type_id
                      WHERE pt.category_id = 7 AND oh.order_hdr_id = %s""", (order_hdr_id,))
    
    order_box_products = cursor.fetchall()
    
    if order_box_products:
        # Convert the results to a dictionary
        product_quantity_dict = {box_product_id: box_product_quantity for box_product_id, box_product_quantity in order_box_products}

        # Initialize a dictionary to hold the quantities of the consumed box content products
        consumed_box_detail_product_quantity_dict = {}
        
        for box_product_id, box_product_quantity in product_quantity_dict.items():
            # Retrieve the contents of each box
            cursor.execute("""SELECT bc.product_id, bc.quantity FROM box b 
                              INNER JOIN box_content bc ON b.box_id = bc.box_id 
                              WHERE b.product_id = %s""", (box_product_id,))
            
            box_contents = cursor.fetchall()
            
            for box_content in box_contents:
                box_detail_product_id = box_content[0]
                consumed_box_detail_product_quantity = int(box_content[1]) * int(box_product_quantity)
                consumed_box_detail_product_quantity_dict[box_detail_product_id] = consumed_box_detail_product_quantity
        
        # Return the dictionary containing the consumed quantities of box content products
        return consumed_box_detail_product_quantity_dict
    
    return None




def adjust_box_content_product_stock(order_hdr_id, cursor, decrease=True):
    # Get the quantities of the products consumed from the box content
    consumed_box_detail_product_quantity_dict = get_box_content_consumed_product_quantity(order_hdr_id, cursor)
    
    if consumed_box_detail_product_quantity_dict is not None:
        # Adjust the stock for the consumed box content products
        update_product_stock_db(consumed_box_detail_product_quantity_dict, cursor, decrease)



def update_payment(order_hdr_id, grandtotal, payment_date):
    user_id = session['user_id']

    cursor = getCursor()
    
    # Initialize payment_id
    payment_id = 0
    
    # Check if a payment record exists for the given order_hdr_id
    cursor.execute("""SELECT payment_id FROM payment WHERE order_hdr_id = %s""", (order_hdr_id,))
    result = cursor.fetchone()
    
    if result:
        # Get the payment_id from the result
        payment_id = result[0]
        
        # Update the payment details in the payment table
        cursor.execute("""UPDATE payment SET amount = %s, payment_date = %s WHERE payment_id = %s""", (grandtotal, payment_date, payment_id))

        cursor.close()
        
        # Send a confirmation message to the user
        send_message(11, user_id, "Your order #{} is confirmed. We know you are eager to receive your new purchase and we will do our best to process your order as soon as possible.".format(order_hdr_id), 1)
    
    return payment_id



def generate_invoice_db(invoice_num, order_hdr_id, payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee):
    cursor = getCursor()
    
    # Check if there's an existing invoice associated with the order_hdr_id
    cursor.execute("""SELECT invoice_id FROM invoice WHERE order_hdr_id = %s""", (order_hdr_id,))
    result = cursor.fetchone()
    
    if result:
        # If an invoice exists, update the existing invoice record
        invoice_id = result[0]
        cursor.execute("""UPDATE invoice SET payment_id = %s, date_issued = CURDATE(), subtotal_amount = %s, gst_amount = %s, 
                          total_amount = %s, shipping_fee = %s WHERE invoice_id = %s""",
                       (payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee, invoice_id))
    else:
        # If no invoice exists, insert a new invoice record
        # Note that gst_rate_id is hard coded to 1 as it's a local NZ business for now
        cursor.execute(
            """INSERT INTO invoice (invoice_num, order_hdr_id, payment_id, date_issued, subtotal_amount, gst_amount, total_amount, gst_rate_id, shipping_fee)
               VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, 1, %s)""",
            (invoice_num, order_hdr_id, payment_id, subtotal_amount, gst_amount, total_amount, shipping_fee))
        
        # Get the ID of the last inserted invoice record
        invoice_id = cursor.lastrowid
    
    cursor.close()
    
    return invoice_id




def create_order(grandtotal, cart_items, user_id=None, purpose=None):
    conn = getCursor()

    # Default to standard shipping
    shipping_option_id = 1 
    
    # Check if user_id is provided, if not, get it from the session
    if user_id is not None:
        conn.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (user_id,))
    else:
        user_id = session['user_id']
        conn.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (session['user_id'],))

    # Determine if the user is in a rural area
    is_rural = conn.fetchone()[0]

    # Set the shipping option to rural if the user is in a rural area
    if is_rural:
        shipping_option_id = 2 

    # Insert a new order into the order_hdr table
    conn.execute(
        """INSERT INTO order_hdr (user_id, order_date, total_price, status_id, shipping_option_id, purpose) 
           VALUES (%s, CURDATE(), %s, %s, %s, %s)""",
        (user_id, grandtotal, 1, shipping_option_id, purpose))
    
    # Get the ID of the last inserted order_hdr record
    order_hdr_id = conn.lastrowid

    # Insert each item in the cart into the order_detail table
    if cart_items or cart_items is not None:
        for product_id, details in cart_items.items():
            item_info = details['item_info']
            quantity = item_info['quantity']
            line_total = details['line_total']
            conn.execute(
                """INSERT INTO order_detail (order_hdr_id, product_id, quantity, line_total_price) 
                   VALUES (%s, %s, %s, %s)""",
                (order_hdr_id, product_id, quantity, line_total))
    
    conn.close()
    
    return order_hdr_id




def add_product_weight_by_id(weight, unit):
    cursor = getCursor()
    # Insert the weight and unit into the product_weight table
    cursor.execute("""INSERT INTO product_weight (weight, unit) VALUES (%s, %s)""", (weight, unit))
    
    cursor.close()



def unit_exists_check(weight, unit):
    cursor = getCursor()
    try:
        # Check if the weight and unit already exist in the product_weight table
        if weight is None:
            cursor.execute("""
                SELECT product_weight_id FROM product_weight WHERE weight IS NULL AND unit = %s
            """, (unit,))
        else:
            # Check for matching weight and unit
            cursor.execute("""
                SELECT product_weight_id FROM product_weight WHERE weight = %s AND unit = %s
            """, (weight, unit))
        
        # If a matching record is found, return True
        if cursor.fetchone():
            return True
        
        # If no matching record is found, return False
        return False
    
    finally:
        cursor.close()



def delete_product_weight_by_id(product_weight_id):
    cursor = getCursor()
    # Delete the product weight record by product_weight_id
    cursor.execute("""DELETE FROM product_weight WHERE product_weight_id=%s""", (product_weight_id,))
    
    cursor.close()



def update_product_weight(product_weight_id, weight, unit):
    cursor = getCursor()
    # Update the product weight record with the given product_weight_id
    cursor.execute("""UPDATE product_weight SET weight=%s, unit=%s WHERE product_weight_id=%s""",
                   (weight, unit, product_weight_id))
    
    cursor.close()



def get_all_messages_by_user_id():
    # Get user_id and user_role_id from session
    user_id = session['user_id']
    user_role_id = session['user_role_id']

    cursor = getCursor()

    # Fetch all messages based on user_role
    #if the user is a customer, return all messages 
    if user_role_id in (1, 2):
        cursor.execute("""SELECT * from message a
                            INNER JOIN message_category b on a.message_category_id = b.message_category_id
                            WHERE receiver_id =  %s order by sent_time desc""", (user_id,))
    # if user is staff, return all the messages for the staff group
    #  within the same depot
    elif user_role_id == 3:
        cursor.execute("""SELECT * FROM message a
                            INNER JOIN message_category b on a.message_category_id = b.message_category_id
                            INNER JOIN message_status c on a.message_status_id = c.message_status_id 
                            WHERE receiver_id in ('3','4') 
                            and depot_id = %s
                            order by sent_time desc;""", (session['user_depot'],))
    # if user is local manager,  return all the messages for the staff group
    #  within the same depot
    elif user_role_id == 4:
        cursor.execute("""SELECT * FROM message a
                            INNER JOIN message_category b on a.message_category_id = b.message_category_id
                            INNER JOIN message_status c on a.message_status_id = c.message_status_id     
                             WHERE receiver_id in ('3','4') 
                            AND depot_id = %s
                            ORDER BY sent_time desc;""", (session['user_depot'],))
    # if user is national manager,  return all the messages for the staff group
    elif user_role_id == 5:
        cursor.execute("""SELECT * FROM message a
                            INNER JOIN message_category b on a.message_category_id = b.message_category_id
                            INNER JOIN message_status c on a.message_status_id = c.message_status_id    
                             INNER JOIN depot d on a.depot_id = d.depot_id 
                             WHERE receiver_id in ('3','4') 
                            ORDER BY sent_time desc;""")
        
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
    # If user_depot is not provided, get it from the session
    if user_depot == "":
        user_depot = session['user_depot']
    
    cursor = getCursor()

    # Insert the message into the message table
    cursor.execute(
        """INSERT INTO message (sender_user_id, receiver_id, content, sent_time, message_status_id, message_category_id, depot_id) 
           VALUES (%s, %s, %s, Now(), 1, %s, %s)""",
        (sender_id, receiver_id, content, message_category_id, user_depot))

    cursor.close()



def delete_message_by_id(message_id):
    cursor = getCursor()

    # Delete the message by message_id
    cursor.execute("""DELETE FROM message WHERE message_id = %s""",
                   (message_id,))
    
    cursor.close()



def get_products_by_user_depot(user_depot, page=None, per_page=None, status_filter=''):
    cursor = getCursor()
    
    # Get the user_depot from the session if not provided
    user_depot = session.get('user_depot')
    
    # Initial query to retrieve product information
    query = """
        SELECT   pt.product_type_name, 
                 p.orig_price, 
                 p.stock_quantity,
                 CONCAT(pw.weight, ' ', pw.unit) AS weight_unit,
                 CASE 
                     WHEN p.stock_quantity = 0 THEN 'Unavailable'
                     WHEN p.stock_quantity <= 20 THEN 'Low'
                     ELSE 'Available'
                 END AS status,
                 p.product_id,
                 p.is_active,
                 pc.category_name
        FROM product p
        JOIN product_type pt ON p.product_type_id = pt.product_type_id
        JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        JOIN product_category pc ON pt.category_id = pc.category_id
        WHERE p.is_active = True and p.depot_id = %s
    """
    
    # Parameters for the query
    params = [user_depot]

    # Add status_filter condition to the query if provided
    if status_filter:
        query += " AND CASE WHEN p.stock_quantity = 0 THEN 'Unavailable' WHEN p.stock_quantity <= 20 THEN 'Low' ELSE 'Available' END = %s"
        params.append(status_filter)
    
    # Append additional conditions and ordering to the query
    query += """
        ORDER BY
            CASE 
                WHEN pc.category_name = 'Premade Box' THEN 1
                ELSE 2
            END,
            CASE 
                WHEN pc.category_name = 'Premade Box' THEN pt.product_type_name
                ELSE NULL
            END,
            pt.product_type_name ASC
    """

    # Add pagination if page and per_page are provided
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
    
    try:
        # Execute the query
        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
    except mysql.connector.Error as err:
        # Handle any errors
        print(f"Error: {err}")
        return [], 0
    
    # If pagination is applied, calculate total products count
    if page is not None and per_page is not None:
        count_query = "SELECT COUNT(*) FROM product WHERE depot_id = %s"
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
    # Establish a database connection
    cursor = getCursor()
    
    # Query to retrieve product information for editing
    query = """
        SELECT  p.product_id, 
                pt.product_type_name, 
                p.orig_price, 
                p.stock_quantity,
                p.is_active,
                CASE WHEN p.stock_quantity > 0 THEN 'Available' ELSE 'Unavailable' END AS status
        FROM product p
        JOIN product_type pt ON p.product_type_id = pt.product_type_id
        WHERE p.product_id = %s
    """
    
    # Execute the query with product_id as parameter
    cursor.execute(query, (product_id,))
    
    # Fetch the product details
    product = cursor.fetchone()
    


    cursor.close()
    
    # Return the product details
    return product



def get_order_details_by_invoice_id(invoice_id):
    # Establish a database connection
    cursor = getCursor()
    
    # Initialize an empty list to store order details
    order_details = []
    
    try:
        # Query to retrieve order details based on invoice_id
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
        
        # Execute the query with invoice_id as parameter
        cursor.execute(query, (invoice_id,))
        
        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Iterate over each row and extract order details
        for row in rows:
            product_name = row[6]
            price = row[5]
            quantity = row[2]
            subtotal = price * quantity
            unit = row[7]

            # Create a dictionary to store order detail information
            order_detail = {
                'product_name': product_name,
                'unit': unit,
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            }

            # Append the order detail dictionary to the order_details list
            order_details.append(order_detail)

    except Exception as e:
        # Print any exceptions that occur
        print(e)
    
    finally:


        cursor.close()



    return order_details



def get_depot_addr_by_name(name):
    # Establish a database connection
    cursor = getCursor()
    
    # Query to retrieve the address of the depot by its name
    query = "SELECT address FROM depot WHERE depot_name = %s"
    
    # Execute the query with the name parameter
    cursor.execute(query, (name,))
    
    # Fetch the address from the result
    address = cursor.fetchone()[0]
    


    return address



def get_user_addr_by_id(id):
    # Establish a database connection
    cursor = getCursor()
    
    # Query to retrieve the address of the user by their user_id
    query = "SELECT address FROM user_profile WHERE user_id = %s"
    
    # Execute the query with the id parameter
    cursor.execute(query, (id,))
    
    # Fetch the address from the result
    address = cursor.fetchone()[0]
    


    return address


 
def insert_account_holder(business_name, business_address, business_phone):
    # Establish a database connection
    cursor = getCursor()

    # Insert the account holder information into the database
    cursor.execute(
        """INSERT INTO account_holder (business_name, business_address, business_phone, user_id, credit_account_id, isApproved) 
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (business_name, business_address, business_phone, session['user_id'], 1, False))
    


    cursor.close()
    
    # Send a confirmation message to the user
    send_message(11, session['user_id'], "Thank you for submitting your application to become an account holder. We have received it successfully. Our team will now review your application thoroughly. You will receive a notification once the review process is complete. We appreciate your patience.", 1)



def account_holder_exists_check():
    # Establish a database connection
    cursor = getCursor()
    
    # Retrieve the user's account holder information from the database
    cursor.execute('SELECT * FROM account_holder WHERE user_id = %s', (session['user_id'],))
    
    # Fetch the user's account holder information
    user = cursor.fetchone()
    


    cursor.close()
    


    return user



def get_user_orders():
    # Get the user's ID from the session
    user_id = session['user_id']
    


    cursor = getCursor()
    
    # Retrieve distinct order information for the user from the database
    cursor.execute(
        """SELECT DISTINCT oh.order_hdr_id, oh.order_date, oh.total_price, os.status_name, so.shipping_option_name, oh.status_id, oh.purpose
        FROM order_hdr oh 
        INNER JOIN order_detail od ON oh.order_hdr_id = od.order_hdr_id 
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        WHERE user_id = %s AND oh.is_active = 1 AND (oh.purpose="order" OR oh.purpose="subscription_order")
        ORDER BY oh.status_id ASC, oh.order_date DESC, oh.order_hdr_id DESC""", (user_id,))



    result = cursor.fetchall()
    


    cursor.close()
    


    return result




def get_order_details_by_id(order_id):


    cursor = getCursor()
    
    # Retrieve order details and product information for the given order_id
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
    
    # Decode image and create a list of items
    for item in results:
        item_list = list_with_decoded_image(item, 0)
        items.append(item_list)

    # Check if modification and cancellation are allowed based on order status
    # We can check any of the last element of the item in the list, should be the same as status_id in order_hdr table
    if int(items[0][-1]) > 1:
        can_modify = False
    
    if int(items[0][-1]) > 2:
        can_cancel = False 

    # Retrieve invoice information for the order
    cursor.execute("""SELECT total_amount, gst_amount, subtotal_amount, purpose FROM order_hdr oh
                    INNER JOIN invoice i ON i.order_hdr_id = oh.order_hdr_id 
                   WHERE oh.order_hdr_id = %s""", (order_id,))
    invoice_info = cursor.fetchone()
    


    cursor.close()
    
    # Return the order items, invoice information, and modification/cancellation flags
    return items, invoice_info, can_modify, can_cancel



def category_exists_check(category_name):
    # Establish a database connection
    cursor = getCursor()
    
    # Check if the category name already exists in the database, if yes, return the row
    cursor.execute("""SELECT * FROM product_category where category_name = %s""", (category_name,))
    
    # Fetch all matching categories
    categories = cursor.fetchall()
    


    cursor.close()
    
    # Return the list of categories with the same name
    return categories



def insert_product_category(category_name, status):


    cursor = getCursor()
    
    # Insert the new product category into the database
    cursor.execute(
    """INSERT INTO product_category (category_name, is_active) 
    VALUES (%s, %s)""",
    (category_name, status))
    


    cursor.close()



def get_product_category_by_id(category_id):


    cursor = getCursor()
    
    # Retrieve the category details based on the category_id
    cursor.execute("""SELECT * FROM product_category where category_id = %s""", (category_id,))
    
    # Fetch the category details
    category = cursor.fetchone()
    


    cursor.close()



    return category



def update_product_category(category_id, category_name, status):


    cursor = getCursor()
    
    # Update the product category in the database
    cursor.execute("""UPDATE product_category 
                      SET category_name = %s, is_active = %s
                      WHERE category_id = %s""", (category_name, status, category_id))



    cursor.close()



def delete_product_category(category_id):


    cursor = getCursor()
    
    # Delete the product category from the database
    cursor.execute("""DELETE FROM product_category WHERE category_id = %s""", (category_id,))



    cursor.close()



def get_invoice_date_and_num(invoice_id):


    cursor = getCursor()
    
    # Query to retrieve the date issued and invoice number based on invoice_id
    query = "SELECT date_issued, invoice_num FROM invoice WHERE invoice_id = %s"
    
    # Execute the query with the invoice_id parameter
    cursor.execute(query, (invoice_id,))
    


    result = cursor.fetchone()
    


    cursor.close()
    
    # Extract date issued and invoice number from the result
    date_issued = result[0]
    invoice_num = result[1]
    
    # Return date issued and invoice number
    return date_issued, invoice_num



def cancel_order_by_id(order_hdr_id):
    cursor = getCursor()
    # Set order_hdr to inactive
    cursor.execute("UPDATE order_hdr SET is_active = 0, status_id = 5 WHERE order_hdr_id = %s", (order_hdr_id,))

    # Get the product_id and the quantity, we need to add the stock back
    product_quantity_dict = get_consumed_product_quantity(order_hdr_id, cursor)
    # Adjust product quantity
    update_product_stock_db(product_quantity_dict, cursor, decrease=False)

    # If any product is a box, we also need to adjust the box content product stock
    adjust_box_content_product_stock(order_hdr_id, cursor, decrease=False)

    # Delete payment and invoice associated with the canceled order
    cursor.execute("SELECT invoice_id FROM invoice WHERE order_hdr_id = %s", (order_hdr_id,))
    invoice_id = cursor.fetchone()
    if invoice_id:
        cursor.execute("DELETE FROM invoice WHERE order_hdr_id = %s", (order_hdr_id,))
        cursor.execute("DELETE FROM payment WHERE order_hdr_id = %s", (order_hdr_id,))
    


    cursor.close()



def get_consumed_product_quantity(order_hdr_id, cursor):
    # Retrieve product IDs and quantities for the given order_hdr_id
    cursor.execute("""SELECT product_id, quantity FROM order_detail WHERE order_hdr_id = %s""", (order_hdr_id,))
    results = cursor.fetchall()
    
    # Convert the results to a dictionary where product_id is the key and quantity is the value
    product_quantity_dict = {product_id: quantity for product_id, quantity in results}
    
    return product_quantity_dict



def get_all_orders(depot_id=None, status_id=None):


    cursor = getCursor()
    
    # Define the base query to retrieve order information
    query = """
        SELECT do.depot_orderid, oh.order_hdr_id, up.first_name, up.last_name, oh.order_date, oh.total_price, oh.status_id, os.status_name, so.shipping_option_name, d.depot_name
        FROM order_hdr oh
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        INNER JOIN user_profile up ON oh.user_id = up.user_id
        INNER JOIN depot_order do ON oh.order_hdr_id = do.order_hdr_id
        INNER JOIN depot d ON do.depot_id = d.depot_id
        WHERE oh.purpose = "order"
    """
    
    # Add conditions based on provided parameters
    conditions = []
    params = []
    if depot_id:
        conditions.append("do.depot_id = %s")
        params.append(depot_id)
    if status_id:
        conditions.append("oh.status_id = %s")
        params.append(status_id)
    
    # Append conditions to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    # Define the order by clause to sort the results
    query += " ORDER BY oh.order_date DESC, up.first_name, up.last_name"
    
    # Execute the query with parameters
    cursor.execute(query, params)
    
    # Fetch all orders
    orders = cursor.fetchall()
    


    cursor.close()
    


    return orders


def update_order_status_by_depot_orderid(depot_orderid, status_id):


    cursor = getCursor()
    
    # Define the SQL query to update the order status based on depot_orderid
    query = """
        UPDATE order_hdr
        SET status_id = %s
        WHERE order_hdr_id = (SELECT order_hdr_id FROM depot_order WHERE depot_orderid = %s)
    """
    
    # Execute the query with the provided status_id and depot_orderid
    cursor.execute(query, (status_id, depot_orderid))
    


    cursor.close()



def get_order_details(order_hdr_id):


    cursor = getCursor()
    
    # Define the SQL query to retrieve order details for the given order_hdr_id
    query = """
        SELECT od.order_detail_id, pt.product_type_name, CONCAT(pw.weight, ' ', pw.unit) AS product_weight, od.quantity, od.line_total_price, p.orig_price
        FROM order_detail od
        INNER JOIN product p ON od.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        WHERE od.order_hdr_id = %s
    """
    
    # Execute the query with the provided order_hdr_id
    cursor.execute(query, (order_hdr_id,))
    
    # Fetch all order details
    order_details = cursor.fetchall()
    


    cursor.close()
    


    return order_details



def get_customer_info(order_hdr_id):


    cursor = getCursor()
    
    # Define the SQL query to retrieve customer information for the given order_hdr_id
    query = """
        SELECT up.first_name, up.last_name, up.phone_number, up.address, oh.order_date, oh.total_price, so.shipping_option_name
        FROM order_hdr oh
        INNER JOIN user_profile up ON oh.user_id = up.user_id
        INNER JOIN shipping_option so ON oh.shipping_option_id = so.shipping_option_id
        WHERE oh.order_hdr_id = %s
    """
    
    # Execute the query with the provided order_hdr_id
    cursor.execute(query, (order_hdr_id,))
    
    # Fetch customer information
    customer_info = cursor.fetchone()
    


    cursor.close()
    
    # Return the customer information
    return customer_info



# Actually goes to db and updates the product quantity
# quantity_diffs is a collection in dict format with product_id as key and quantity as value
def update_product_stock_db(quantity_diffs, cursor, decrease=True):
    # Determine the symbol for the SQL query based on whether it's a decrease or increase in stock
    symbol = "-" if decrease else "+"
    
    # Define the base SQL query to update the product stock quantity
    update_product_query = f"UPDATE product SET stock_quantity = stock_quantity {symbol} %s WHERE product_id = %s"
    
    # Iterate over the quantity_diffs dictionary
    for key, value in quantity_diffs.items():
        product_id = int(key)
        quantity_diff = int(value)
        # Execute the SQL query to update the product stock quantity
        cursor.execute(update_product_query, (quantity_diff, product_id))


# Calculated the quantity diff and then update in db
def update_product_stock(old_dict, new_dict, cursor):

    # Get a set of all product IDs from both dictionaries
    all_product_ids = set(old_dict.keys()).union(set(new_dict.keys()))
    
    # Calculate the quantity differences
    # On UI when modify the order, you can only increase the quantity so we know new_quantity is already larger than old_quantity
    quantity_diffs = {}
    for product_id in all_product_ids:
        old_quantity = old_dict.get(product_id, 0)
        new_quantity = new_dict.get(product_id, 0)
        quantity_diffs[product_id] = int(new_quantity - old_quantity)

    # Update product stock accordingly
    update_product_stock_db(quantity_diffs, cursor)
  

def get_current_user_depot_id():


    cursor = getCursor()
    
    # Execute the SQL query to retrieve the depot_id of the current user
    cursor.execute("SELECT depot_id FROM user WHERE user_id = %s", (session['user_id'],))
    
    # Fetch the depot_id
    depot_id = cursor.fetchone()[0]
    


    cursor.close()
    
    # Return the depot_id
    return depot_id



def modify_order_by_id(items, order_hdr_id, grandtotal):
    user_id = session['user_id']
    cursor = getCursor()

    # Get old product_id and quantity from order_detail
    old_product_quantity = get_consumed_product_quantity(order_hdr_id, cursor)

    # Get old box content quantity if any purchases product is box
    old_box_content_product_quantity_dict = get_box_content_consumed_product_quantity(order_hdr_id, cursor)

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

    if old_box_content_product_quantity_dict is not None:
        # the order customer modifies has box as product, let's get the modified quantity and adjust the stock
        new_box_content_product_quantity_dict = get_box_content_consumed_product_quantity(order_hdr_id, cursor)
        update_product_stock(old_box_content_product_quantity_dict, new_box_content_product_quantity_dict, cursor)

    update_product_stock(old_product_quantity, new_product_quantity, cursor)
    cursor.close()




def get_payment_diff(grandtotal, order_hdr_id):
    # Establish a database connection
    cursor = getCursor()
    
    # Calculate payment difference
    cursor.execute("""SELECT SUM(amount) FROM payment WHERE order_hdr_id = %s""", (order_hdr_id,))
    
    # Fetch the result
    result = cursor.fetchone()
    
    cursor.close()
    
    # Extract the sum of payment amounts
    paid = result[0]
    
    # Calculate the payment amount difference
    payment_amount_diff = float(grandtotal) - float(paid)
    
    return payment_amount_diff



def update_product(product_id, new_price, new_quantity, is_discontinued):
    cursor = getCursor()

    # Define the SQL query to update the product information
    update_query = """
        UPDATE product
        SET orig_price = %s, stock_quantity = %s, is_active = %s
        WHERE product_id = %s
    """
    # Determine the value of is_active based on whether the product is discontinued or not
    is_active = 0 if is_discontinued else 1
    
    # Execute the update query with the provided parameters
    cursor.execute(update_query, (new_price, new_quantity, is_active, product_id))

    # If the product is discontinued, log it to the discontinued_products table
    if is_discontinued:
        # Retrieve the name of the product for logging
        product_query = """
            SELECT product_type.product_type_name 
            FROM product
            JOIN product_type ON product.product_type_id = product_type.product_type_id
            WHERE product.product_id = %s
        """
        cursor.execute(product_query, (product_id,))
        product_name = cursor.fetchone()[0]

        # Insert a record into the discontinued_products table
        log_query = """
            INSERT INTO discontinued_products (product_id, product_name)
            VALUES (%s, %s)
        """
        cursor.execute(log_query, (product_id, product_name))
    else:
        # If the product is not discontinued, delete its entry from the discontinued_products table
        delete_query = "DELETE FROM discontinued_products WHERE product_id = %s"
        cursor.execute(delete_query, (product_id,))
        
    cursor.close()



def get_order_hdr_and_user_id(depot_orderid):
    cursor = getCursor()

    # Retrieve the order_hdr_id and user_id associated with the given depot_orderid
    cursor.execute("""SELECT order_hdr_id, user_id FROM order_hdr
                     WHERE order_hdr_id = (SELECT order_hdr_id FROM depot_order
                        WHERE depot_orderid = %s)""", (depot_orderid,))
    
    # Fetch the result
    result = cursor.fetchone()
    



    cursor.close()
    
    # Extract order_hdr_id and user_id from the result
    order_hdr_id = result[0]
    user_id = result[1]
    
    return order_hdr_id, user_id



def get_order_receipts():
    user_id = session['user_id']
    cursor = getCursor()

    # Retrieve order receipts for the current user
    cursor.execute(
        """SELECT oh.order_hdr_id, oh.order_date, oh.total_price, os.status_name, so.shipping_option_name, i.invoice_num, i.invoice_id
        FROM order_hdr oh 
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON so.shipping_option_id = oh.shipping_option_id
        LEFT JOIN invoice i ON oh.order_hdr_id = i.order_hdr_id
        WHERE oh.user_id = %s AND oh.is_active = 1 AND oh.purpose != "subscription_order"
        ORDER BY oh.order_date DESC""", (user_id,))
    
    # Fetch all the order receipts
    result = cursor.fetchall()

    cursor.close()
    
    return result



def get_order_status_by_id(order_hdr_id):
    cursor = getCursor()

    # Retrieve the status ID of the order with the given order_hdr_id
    cursor.execute("""SELECT status_id FROM order_hdr WHERE order_hdr_id = %s""", (order_hdr_id,))
    


    result = cursor.fetchone()
    
    cursor.close()
    
    # Return the status ID as an integer
    return int(result[0])



def get_local_manager_id_for_user_id(user_depot_id):
    cursor = getCursor()

    # Retrieve the user ID of the local manager associated with the given user_depot_id
    cursor.execute("""SELECT user_id FROM user WHERE depot_id = %s AND role_id = 4 AND is_active = 1""", (user_depot_id,))
    
    # Fetch all the results
    result = cursor.fetchall()
    
    cursor.close()
    
    return result[0]



def get_national_manager_id():
    cursor = getCursor()

    # Retrieve the user ID of the national manager
    cursor.execute("""SELECT user_id FROM user WHERE role_id = 5 AND is_active = 1""")
    
    # Fetch all the results
    result = cursor.fetchall()

    cursor.close()
    
    return result[0]



def get_all_shipping_option_list():
    cursor = getCursor()

    # Retrieve all shipping options from the database
    cursor.execute("""SELECT * FROM shipping_option """)
    
    # Fetch all the results
    shipping_option = cursor.fetchall()

    cursor.close()
    
    # Return the list of shipping options
    return shipping_option



def shipping_option_exists_check(shipping_option_name):
    cursor = getCursor()

    # Check if the shipping option name already exists in the database,  if yes, return the row
    cursor.execute("""SELECT * FROM shipping_option where shipping_option_name = %s""", (shipping_option_name,))
    
    # Fetch all the results
    shipping_option = cursor.fetchall()
    
    cursor.close()
    
    # Return the shipping option (if found)
    return shipping_option




def insert_shipping_option(shipping_option_name, price):
    cursor = getCursor()

    # Insert a new shipping option into the database
    cursor.execute(
        """INSERT INTO shipping_option (shipping_option_name, price) 
        VALUES (%s, %s, %s)""",
        (shipping_option_name, price))

    cursor.close()



def get_shipping_option_name_by_id(shipping_option_id):
    cursor = getCursor()
    # return the shipping option to the caller based on the category id
    cursor.execute("""SELECT * FROM shipping_option where shipping_option_id = %s""", (shipping_option_id,))
    category = cursor.fetchone()
    cursor.close()
    return category



def update_shipping_option(shipping_option_id, shipping_option_name, price):
    cursor = getCursor()
    # update the shipping option
    cursor.execute("""UPDATE shipping_option SET shipping_option_name = %s, price = %s
                         WHERE shipping_option_id = %s""", (shipping_option_name, price, shipping_option_id,))
    cursor.close()



def delete_shipping_option_by_id(shipping_option_id):
    cursor = getCursor()
    # delete the shipping option
    cursor.execute("""DELETE FROM shipping_option WHERE shipping_option_id = %s""", (shipping_option_id,))
    cursor.close()



def get_all_product():

    cursor = getCursor()



    # SQL query to retrieve product information
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
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to insert a new product into the database
    cursor.execute("""INSERT INTO product (orig_price, stock_quantity, depot_id, product_type_id, promotion_type_id, is_active) VALUES
                       (%s, %s, %s, %s, NULL, %s)""", (orig_price, stock_quantity, depot_id, product_type_id, is_active))

    # Get the ID of the newly inserted product
    product_id = cursor.lastrowid



    cursor.close()

    # Return the ID of the newly inserted product
    return product_id



def get_box_price_by_box_size_id(box_size_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the price of the box by its size ID
    cursor.execute("""SELECT price FROM box_size WHERE box_size_id = %s """, (box_size_id,))

    # Fetch the result
    result = cursor.fetchone()[0]



    cursor.close()

    # Return the price
    return result


def add_new_box(product_id, box_size_id, box_start_date, box_end_date, box_category_id, is_active):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to insert a new box into the database
    cursor.execute("""INSERT INTO box (product_id, box_size_id, box_start_date, box_end_date, box_category_id, is_active) VALUES 
                   (%s, %s, %s, %s, %s, %s)""", (product_id, box_size_id, box_start_date, box_end_date, box_category_id, is_active))

    # Get the ID of the newly inserted box
    box_id = cursor.lastrowid



    cursor.close()

    # Return the ID of the newly inserted box
    return box_id



def set_box_and_its_product_active(box_id):
    # Get the cursor
    cursor = getCursor()

    # Retrieve the product ID associated with the given box ID
    cursor.execute("SELECT product_id FROM box WHERE box_id = %s", (box_id,))
    product_id = cursor.fetchone()[0]

    # Update the product's active status to 1 (active) in the database
    cursor.execute("UPDATE product SET is_active = 1 WHERE product_id = %s", (product_id,))

    # Update the box's active status to 1 (active) in the database
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
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve account holder information based on user ID
    cursor.execute("""
                SELECT ah.account_holder_id, ah.business_name, ah.business_address, ah.business_phone, ah.user_id, ah.credit_account_id, ca.credit_limit, u.depot_id
                FROM account_holder ah
                JOIN user u ON ah.user_id = u.user_id
                JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
                WHERE u.user_id = %s
            """, (user_id,))
    
    # Fetch the account holder information
    account_holder_info = cursor.fetchone()



    cursor.close()

    # Return the account holder information
    return account_holder_info



def get_current_credit_limit(user_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the current credit limit based on user ID
    cursor.execute("""
            SELECT ca.credit_limit
            FROM account_holder ah
            JOIN user u ON ah.user_id = u.user_id
            JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
            WHERE u.user_id = %s
        """, (user_id,))
    
    # Fetch the current credit limit
    current_credit_limit = cursor.fetchone()



    cursor.close()

    # Return the current credit limit, if available, otherwise return None
    return current_credit_limit[0] if current_credit_limit else None



def apply_limit_increase_to_db(user_id, depot_id, current_limit, reason, requested_limit, requested_date):
    # Get the cursor
    cursor = getCursor()

    # Insert the credit limit change request into the database
    cursor.execute("""INSERT INTO credit_limit_change_request (user_id, depot_id, current_limit, reason, requested_limit, requested_date) 
                   VALUES (%s, %s, %s, %s, %s, %s) """, (user_id, depot_id, current_limit, reason, requested_limit, requested_date))
    


    cursor.close()
    
    # Send a message to the user confirming the submission of the application
    send_message(11, session['user_id'], "Thank you for submitting your application to increase your credit limit. We have received it successfully. Our team will now review your application thoroughly. You will receive a notification once the review process is complete. We appreciate your patience.", 1)



def get_products_by_ids(product_ids):
    # Get the cursor
    cursor = getCursor()
    try:
        # Prepare placeholders for the product IDs in the SQL query
        placeholders = ', '.join(['%s'] * len(product_ids))
        # Construct the SQL query to retrieve product information by IDs
        query = f"""
            SELECT p.product_id, pt.product_type_name, pt.product_image, pw.weight, pw.unit
            FROM product p 
            INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
            INNER JOIN product_weight pw ON pw.product_weight_id = pt.product_weight_id
            WHERE p.product_id IN ({placeholders})
        """
        # Execute the SQL query with the product IDs
        cursor.execute(query, tuple(product_ids))
        # Fetch all results
        results = cursor.fetchall()
    except Exception as e:
        # Handle any errors that may occur during fetching
        print(f"Error fetching products: {e}")
        results = []
    finally:


        cursor.close()
    
    # Initialize an empty list to store decoded products
    products = []
    # Decode image and create a list of products
    for product in results:
        # Decode the image and create a list with decoded image
        product_list = list_with_decoded_image(product, 2)
        products.append(product_list)
    
    # Return the list of products
    return products



def get_current_credit_balance(user_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the current credit balance based on user ID
    cursor.execute("""
            SELECT ca.current_balance
            FROM account_holder ah
            JOIN user u ON ah.user_id = u.user_id
            JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
            WHERE u.user_id = %s
        """, (user_id,))
    
    # Fetch the current credit balance
    current_credit_balance = cursor.fetchone()



    cursor.close()

    # Return the current credit balance, if available, otherwise return None
    return current_credit_balance[0] if current_credit_balance else None



def get_user_depot_id(user_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the depot ID based on user ID
    cursor.execute("SELECT depot_id FROM user WHERE user_id = %s", (user_id,))
    
    # Fetch the depot ID
    depot_id = cursor.fetchone()



    cursor.close()

    # Return the depot ID, if available, otherwise return None
    return depot_id[0] if depot_id else None



def get_customer_shipping_fee(user_id=None):
    # Get the cursor
    cursor = getCursor()

    # Check if a specific user ID is provided
    if (user_id is not None):
        # If a user ID is provided, execute SQL query to check if the user is rural
        cursor.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (user_id,))
    else:
        # If no user ID is provided, use the session user ID to check if the user is rural
        cursor.execute("""SELECT is_rural FROM user_profile WHERE user_id = %s """, (session['user_id'] ,))
    
    # Fetch the value indicating if the user is rural
    is_rural = cursor.fetchone()[0]

    # Based on whether the user is rural or not, retrieve the appropriate shipping fee
    if is_rural:
        cursor.execute("""SELECT price FROM shipping_option WHERE shipping_option_id = '2'""")
    else:
        cursor.execute("""SELECT price FROM shipping_option WHERE shipping_option_id = '1'""")

    # Fetch the shipping fee
    shipping_fee = cursor.fetchone()[0]



    cursor.close()

    # Return the shipping fee
    return shipping_fee



def check_low_stock_product_by_all():
    # Get all products
    products = get_all_product()
    
    # Extract depot IDs with low stock products
    low_stock_depots = {product[-1] for product in products if product[2] < 20}  # Using a set to avoid duplicates
    
    # Convert the set to a list and return
    return list(low_stock_depots)



def get_pending_requests(depot_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve pending requests for the given depot ID
    cursor.execute("""
        SELECT ah.account_holder_id, CONCAT(up.first_name, ' ', up.last_name) AS user_name, ah.business_name, DATE_FORMAT(CURDATE(), '%Y-%m-%d') as date 
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN user u ON up.user_id = u.user_id
        WHERE ah.isApproved = FALSE AND u.depot_id = %s
    """, (depot_id,))
    
    # Fetch all pending requests
    requests = cursor.fetchall()



    cursor.close()

    # Return the pending requests
    return requests



def get_request_details(request_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve details of the request by request ID
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
    
    # Fetch the request details
    request = cursor.fetchone()



    cursor.close()

    # Return the request details
    return request




def get_credit_limit(credit_limit):
    # Get the cursor
    cursor = getCursor()
    
    # Insert the credit limit into the credit_account table
    cursor.execute("INSERT INTO credit_account (credit_limit, current_balance) VALUES (%s, 0.00)", (credit_limit,))
    
    # Get the ID of the newly inserted credit account
    credit_account_id = cursor.lastrowid
    


    cursor.close()
    
    # Return the ID of the newly inserted credit account
    return credit_account_id



def update_account_holder(account_holder_id, credit_account_id):
    # Get the cursor
    cursor = getCursor()
    
    # Update the account holder's credit account ID and approval status in the database
    cursor.execute("UPDATE account_holder SET credit_account_id = %s, isApproved = TRUE WHERE account_holder_id = %s", (credit_account_id, account_holder_id))
    


    cursor.close()




def update_account_holder_current_balance(current_balance, user_id):
    # Get the cursor
    cursor = getCursor()

    # Update the current balance in the credit_account table for the specified user ID
    cursor.execute("""UPDATE credit_account ca INNER JOIN account_holder ah ON ca.credit_account_id = ah.credit_account_id
                    SET ca.current_balance = %s WHERE ah.user_id = %s;""", (current_balance, user_id))



    cursor.close()


def get_user_id_from_account_holder(account_holder_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the user ID associated with the account holder ID
    cursor.execute("SELECT user_id FROM account_holder WHERE account_holder_id = %s", (account_holder_id,))
    
    # Fetch the user ID
    user_id = cursor.fetchone()[0]



    cursor.close()

    # Return the user ID
    return user_id



def update_user_role(user_id, new_role_id):
    # Get the cursor
    cursor = getCursor()

    # Update the user's role ID in the user table
    cursor.execute("UPDATE user SET role_id = %s WHERE user_id = %s", (new_role_id, user_id))



    cursor.close()



def reject_request(request_id):
    # Get the cursor
    cursor = getCursor()

    # Retrieve the user ID associated with the request ID
    cursor.execute("SELECT user_id FROM account_holder WHERE account_holder_id = %s", (request_id,))
    user_id = cursor.fetchone()[0]

    # Delete the account holder entry corresponding to the request ID
    cursor.execute("DELETE FROM account_holder WHERE account_holder_id = %s", (request_id,))



    cursor.close()

    return get_user_full_name(user_id)



def check_low_stock_product_by_depot(depot_id):
    # Get products associated with the specified depot ID
    products = get_products_by_user_depot(depot_id)
    
    # Check if any product in the depot has a stock quantity less than 20
    return any(product[2] < 20 for product in products)



def get_message_categories():
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve message categories excluding the default category
    cursor.execute("SELECT * FROM message_category where message_category_id != '1'")
    
    # Fetch all message categories
    message_categories = cursor.fetchall()



    cursor.close()

    # Return the message categories
    return message_categories



def get_message_by_id(message_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the message by message ID and join with the message category table
    cursor.execute("""SELECT * FROM message a
                        INNER JOIN message_category b on a.message_category_id = b.message_category_id
                        WHERE message_id =  %s order by sent_time asc""", (message_id,))
    
    # Fetch the message
    message = cursor.fetchone()



    cursor.close()

    # Initialize a list to store modified messages
    modified_messages = []

    if message:
        sender_id = message[1]
        # Determine sender's full name based on sender's ID
        if sender_id == 11:
            sender_full_name = "Administrator"
        else:
            sender_full_name = get_user_full_name(sender_id)

        # Convert message to list and append sender's full name
        message_list = list(message)
        message_list.append(sender_full_name)
        modified_message = tuple(message_list)

        # Append modified message to the list of modified messages
        return [modified_message]



def get_all_weekly_boxes(depot_id):
    # Get the cursor
    cursor = getCursor()

    query = """SELECT box.box_id, box.product_id, 
                   DATE_FORMAT(box_start_date, '%d-%m-%Y') as box_start_date, 
                   DATE_FORMAT(box_end_date, '%d-%m-%Y') as box_end_date, box_size.size_name, 
                      box_size.price, product_type.product_type_name, depot.depot_name
                      FROM box 
                      INNER JOIN box_size ON box.box_size_id = box_size.box_size_id 
                      INNER JOIN product ON box.product_id = product.product_id 
                      INNER JOIN product_type ON product.product_type_id = product_type.product_type_id
                      INNER JOIN depot ON depot.depot_id = product.depot_id
                      WHERE box.is_active = 1 
                      AND box_start_date <= CURDATE() 
                      AND box_end_date >= CURDATE() 
                      AND YEARWEEK(box_start_date, 1) = YEARWEEK(CURDATE(), 1) 
                      AND YEARWEEK(box_end_date, 1) = YEARWEEK(CURDATE(), 1)"""
    and_depot_query = " AND product.depot_id = %s"

    if str(session['user_role_id']) == '5':
        cursor.execute(query)
    else:
        query += and_depot_query
        # Execute the SQL query to retrieve all weekly boxes for the specified depot ID
        cursor.execute(query, (depot_id,))        
    # Fetch all results
    results = cursor.fetchall()



    cursor.close()

    # Return the results
    return results



def get_box_details_by_id(box_id):
    # Get the cursor
    cursor = getCursor()

    # Query to get box content details and related product information
    cursor.execute("""
        SELECT p.product_id, pt.product_type_name, pt.product_image, pw.weight, pw.unit, bc.quantity FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        WHERE bc.box_id = %s""", (box_id,))
    
    # Fetch all results
    results = cursor.fetchall()



    cursor.close()

    # Initialize a list to store products
    products = []

    # Decode image and create a list of products
    for product in results:
        # Decode the image and create a list with decoded image
        product_list = list_with_decoded_image(product, 2)
        products.append(product_list)

    # Return the list of products
    return products




def get_box_product_quantity_by_id(box_id):
    # Get the cursor
    cursor = getCursor()

    # Query to get product quantities in the box
    cursor.execute("""
        SELECT p.product_id, bc.quantity FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        WHERE bc.box_id = %s""", (box_id,))
    
    # Fetch all results
    results = cursor.fetchall()



    cursor.close()

    # Create a dictionary with product_id as the key and quantity as the value
    product_quantities = {str(row[0]): row[1] for row in results}

    # Return the dictionary of product quantities
    return product_quantities



def get_box_content_quantity_by_product_id(product_id):
    cursor = getCursor()
    # Query to get product quantities in the box
    cursor.execute("""
        SELECT bc.product_id, bc.quantity FROM product p 
        INNER JOIN box b ON b.product_id = p.product_id
        INNER JOIN box_content bc ON bc.box_id = b.box_id
        WHERE p.product_id = %s""", (product_id,))
    results = cursor.fetchall()

    cursor.close()
    
    # Create a dictionary with product_id as the key and quantity as the value
    product_quantities = {str(row[0]): row[1] for row in results}
    return product_quantities


def delete_single_content_from_box(item_product_id, box_id):
    cursor = getCursor()
    # Delete a single item from the box based on item product ID and box ID
    cursor.execute("DELETE FROM box_content WHERE product_id = %s AND box_id = %s", (item_product_id, box_id))
    
    cursor.close()



def delete_all_box_content_by_box_id(box_id):
    cursor = getCursor()
    # Delete all box content associated with a given box ID
    cursor.execute("DELETE FROM box_content WHERE box_id = %s", (box_id,))
    
    cursor.close()



def get_box_product_name_by_box_id(box_id):
    cursor = getCursor()
    # Retrieve the product type name associated with the box ID
    cursor.execute("""SELECT product_type_name FROM box b
                   INNER JOIN product p ON p.product_id = b.product_id
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id 
                   WHERE box_id = %s""", (box_id,))
    product_type_name = cursor.fetchone()[0]
    cursor.close()
    
    return product_type_name



def get_box_product_name_by_product_id(product_id):
    cursor = getCursor()
    # Retrieve the product type name associated with the product ID
    cursor.execute("""SELECT product_type_name FROM product p
                   INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id 
                   WHERE product_id = %s""", (product_id,))
    product_type_name = cursor.fetchone()[0]
    cursor.close()
    
    return product_type_name



def update_box_with_product_id(box_id, product_id, quantity):
    cursor = getCursor()
    # Check if there is existing content for the provided box and product ID
    cursor.execute("SELECT quantity FROM box_content WHERE box_id = %s AND product_id = %s", (box_id, product_id))
    existing_content = cursor.fetchone()

    if existing_content:
        # Update the quantity if content already exists
        new_quantity = quantity
        cursor.execute("UPDATE box_content SET quantity = %s WHERE box_id = %s AND product_id = %s", (new_quantity, box_id, product_id))
    else:
        # Insert new content if it doesn't exist
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



# the threshold of $100 can be changed
def check_remaining_credit_low():
    # Retrieve the user ID from the session
    user_id = session.get('user_id')
    # Get the current credit limit for the user
    current_limit = get_current_credit_limit(user_id)
    # Get the current credit balance for the user
    current_balance = get_current_credit_balance(user_id)
    # Calculate the remaining credit by subtracting the balance from the limit
    remaining_credit = current_limit - current_balance
    # Check if the remaining credit is less than or equal to 100
    return remaining_credit <= 100



def check_low_stock_product_by_depot(depot_id):
    # Retrieve products associated with the given depot ID
    products = get_products_by_user_depot(depot_id)
    # Check if any product in the list has a stock level less than or equal to 20
    return any(product[2] <= 20 for product in products)



def get_all_depots():
    # Get database cursor
    cursor = getCursor()
    # SQL query to retrieve depot IDs and names for dropdown menu
    query = "SELECT depot_id, depot_name FROM depot"
    # Execute the query
    cursor.execute(query)
    # Fetch all results
    depots = cursor.fetchall()


    cursor.close()
    # Transform the results into a list of dictionaries with 'id' and 'name' keys
    return [{'id': depot[0], 'name': depot[1]} for depot in depots]



def get_products_by_depot_and_status(depot_id=None, status='All', page=1, per_page=10):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Calculate the offset for pagination
    offset = (page - 1) * per_page
    # Initial query to retrieve product information
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

    # Check if depot_id is provided and not None
    if depot_id is not None:
        if depot_id != 0:  # Filter by specific depot
            query += " AND p.depot_id = %s"
            params.append(depot_id)

    # Check if status filter is applied
    if status != 'All':
        query += " HAVING status = %s"
        params.append(status)

    # Add pagination and ordering to the query
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

    # Execute the query with parameters
    cursor.execute(query, params)

    # Fetch all products
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

    # Execute count query to get total number of records
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]

    cursor.close()

    # Return products and total count
    return products, total




def get_box_contents_by_product_id(product_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve box contents for a given product_id
    cursor.execute("""
        SELECT bc.box_id, pt.product_type_name, pw.weight, pw.unit, bc.quantity
        FROM box_content bc
        INNER JOIN product p ON bc.product_id = p.product_id
        INNER JOIN product_type pt ON p.product_type_id = pt.product_type_id
        INNER JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        INNER JOIN box b ON bc.box_id = b.box_id WHERE b.product_id = %s""", (product_id,))
    # Fetch all box contents
    contents = cursor.fetchall()

    cursor.close()
    # Return box contents
    return contents



def update_message_by_id(message_id, status):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to update message status by message_id
    cursor.execute("""UPDATE message set message_status_id = %s WHERE message_id =%s""",
                       (status, message_id,))

    cursor.close()


def get_customer_subscription():
    # Retrieve user_id from session
    user_id = session.get('user_id')
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve customer subscriptions
    cursor.execute("""
        select a.user_box_subscription_id, b.frequency, a.subscription_quantity, sent_quantity, c.category, d.size_name, subscription_date, is_active, last_order_date
        FROM user_box_subscription a
        INNER JOIN box_frequency b on a.box_frequency_id = b.box_frequency_id
        INNER JOIN box_category c on a.box_category_id = c.box_category_id
        INNER JOIN box_size d on a.box_size_id = d.box_size_id
        where a.is_active = true and user_id = %s""", (user_id,))
    # Fetch all customer subscriptions
    subscriptions = cursor.fetchall()

    cursor.close()
    # Return customer subscriptions
    return subscriptions


def get_box_frequency():
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve box frequencies
    cursor.execute("SELECT * FROM box_frequency;")
    # Fetch all box frequencies
    box_frequency = cursor.fetchall()

    cursor.close()
    # Return box frequencies
    return box_frequency



def get_box_category():
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve box categories
    cursor.execute("SELECT * FROM box_category;")
    # Fetch all box categories
    box_category = cursor.fetchall()

    cursor.close()
    # Return box categories
    return box_category



def get_box_category_name_by_id(box_category_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve box category name by box_category_id
    cursor.execute("SELECT category FROM box_category WHERE box_category_id = %s;", (box_category_id,))
    # Fetch the box category name
    box_category = cursor.fetchone()

    cursor.close()
    # Return the box category name
    return box_category[0]



def get_box_category_by_id(box_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve box category ID by box_id
    cursor.execute("SELECT box_category_id FROM box WHERE box_id = %s;", (box_id,))
    # Fetch the box category ID
    box_category_id = cursor.fetchone()

    cursor.close()
    # Return the box category ID
    return box_category_id[0]



def create_subscription(frequency, category, size, quantity):
    # Retrieve user_id from session
    user_id = session['user_id']
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to insert subscription details into the database
    cursor.execute("""INSERT INTO user_box_subscription (box_frequency_id, subscription_quantity, 
                        user_id, box_category_id, box_size_id, subscription_date, sent_quantity,is_active) 
                        VALUES (%s, %s, %s, %s, %s, CURDATE(), 0, False)""", 
                        (frequency, quantity, user_id, category, size))
    # Get the ID of the newly created subscription
    user_box_subscription_id = cursor.lastrowid

    cursor.close()
    # Return the ID of the newly created subscription
    return user_box_subscription_id



def get_all_pending_requests():
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve all pending requests
    cursor.execute("""
        SELECT ah.account_holder_id, CONCAT(up.first_name, ' ', up.last_name) AS user_name, 
               ah.business_name, DATE_FORMAT(CURDATE(), '%Y-%m-%d') as date, d.depot_name 
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN user u ON up.user_id = u.user_id
        JOIN depot d ON u.depot_id = d.depot_id
        WHERE ah.isApproved = FALSE
    """)
    # Fetch all pending requests
    requests = cursor.fetchall()

    cursor.close()
    # Return all pending requests
    return requests



# the following query works for both local and national managers
# it will only return the requests that have not been processed
def get_credit_limit_increase_requests(depot_id=None):
    cursor = getCursor()

    # Base query
    base_query = """
    SELECT clcr.*, 
           CONCAT(up.first_name, ' ', up.last_name) AS full_name, 
           ah.business_name, ah.business_address, ah.business_phone
    FROM credit_limit_change_request clcr
    JOIN user_profile up ON clcr.user_id = up.user_id
    JOIN account_holder ah ON clcr.user_id = ah.user_id
    WHERE clcr.is_actioned = 0
    """

    # Add condition for depot_id if provided
    if depot_id is not None:
        query = base_query + " AND clcr.depot_id = %s ORDER BY clcr.requested_date DESC"
        cursor.execute(query, (depot_id,))
    else:
        query = base_query + " ORDER BY clcr.requested_date DESC"
        cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    return results



def get_credit_limit_increase_request_info(request_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve credit limit increase request information
    query = """
         SELECT clcr.*, 
           CONCAT(up.first_name, ' ', up.last_name) AS full_name, 
           ah.business_name, ah.business_address, ah.business_phone
        FROM credit_limit_change_request clcr
        JOIN user_profile up ON clcr.user_id = up.user_id
        JOIN account_holder ah ON clcr.user_id = ah.user_id
        WHERE clcr.request_id = %s
        """
    # Execute the query with the provided request_id
    cursor.execute(query, (request_id,))
    # Fetch the result of the query
    result = cursor.fetchone()

    cursor.close()
    # Return the result
    return result




def get_filtered_orders(depot_id=None, order_date=None, status=None, customer_name=None):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the base query to retrieve filtered orders
    query = """
        SELECT DISTINCT do.depot_orderid, oh.order_hdr_id, up.first_name, up.last_name, oh.order_date, oh.total_price, os.status_name, so.shipping_option_name, d.depot_name
        FROM order_hdr oh
        INNER JOIN order_detail  od ON oh.order_hdr_id = od.order_hdr_id 
        INNER JOIN user_profile up ON oh.user_id = up.user_id
        INNER JOIN order_status os ON oh.status_id = os.status_id
        INNER JOIN shipping_option so ON oh.shipping_option_id = so.shipping_option_id
        INNER JOIN depot_order do ON oh.order_hdr_id = do.order_hdr_id
        INNER JOIN depot d ON do.depot_id = d.depot_id
        WHERE 1=1 and oh.purpose = "order"
    """
    params = []
    # Add conditions based on the provided parameters
    if depot_id:
        query += " AND do.depot_id = %s"
        params.append(depot_id)
    if order_date:
        query += " AND DATE(oh.order_date) = %s"
        params.append(order_date)
    if status:
        query += " AND os.status_id = %s"
        params.append(status)
    if customer_name:
        query += " AND (up.first_name LIKE %s OR up.last_name LIKE %s)"
        like_pattern = f"%{customer_name}%"
        params.append(like_pattern)
        params.append(like_pattern)

    # Add ordering to the query
    query += " ORDER BY oh.order_date DESC"

    # Execute the query with parameters
    cursor.execute(query, tuple(params))
    # Fetch all filtered orders
    rows = cursor.fetchall()

    cursor.close()

    # Convert the result to a list of dictionaries for better readability
    orders = []
    for row in rows:
        order = {
            'depot_order_id': row[0],
            'order_hdr_id': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'order_date': row[4],
            'total_price': row[5],
            'status_name': row[6],
            'shipping_option_name': row[7],
            'depot_name': row[8]
        }
        orders.append(order)
    
    return orders



def get_subscription_details_by_invoice_id(invoice_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Initialize variables
    order_details = []
    grand_total = ""
    shipping_fee = ""
    gst = ""

    try:
        # Define the query to retrieve subscription details based on invoice_id
        query = """
                SELECT DISTINCT b.frequency, a.subscription_quantity, c.category, d.size_name, d.price, total_amount, shipping_fee, gst_amount
                FROM user_box_subscription a
                INNER JOIN box_frequency b ON a.box_frequency_id = b.box_frequency_id
                INNER JOIN box_category c ON a.box_category_id = c.box_category_id
                INNER JOIN box_size d ON a.box_size_id = d.box_size_id
                INNER JOIN order_hdr e ON a.user_id = e.user_id
                INNER JOIN invoice f ON e.order_hdr_id = f.order_hdr_id WHERE a.is_active = 1 AND invoice_id = %s
            """
        # Execute the query with the provided invoice_id
        cursor.execute(query, (invoice_id,))
        
        # Fetch the subscription details
        subscription = cursor.fetchone()

        if subscription:
            # Extract subscription details
            product_name = subscription[0] + " " + subscription[2] + " Box Subscription"
            price = subscription[4]
            quantity = subscription[1]
            subtotal = price * quantity
            unit = subscription[3]

            # Create dictionary for order detail
            order_detail = {
                'product_name': product_name,
                'unit': unit,
                'price': price,
                'quantity': quantity,
                'subtotal': subtotal
            }

            # Append order detail to the list
            order_details.append(order_detail)

            # Extract other details
            grand_total = subscription[5]
            shipping_fee = subscription[6]
            gst = subscription[7].quantize(Decimal('0.01'))

    except Exception as e:
        print(e)
    finally:

        cursor.close()

    # Return order details, grand total, shipping fee, and GST
    return order_details, grand_total, shipping_fee, gst



def get_all_active_subscription(depot_id=None):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the base query to retrieve all active subscriptions
    base_query = """
        SELECT a.user_id, user_box_subscription_id, box_frequency_id, a.box_category_id, a.box_size_id,
        (subscription_quantity - sent_quantity) AS quantity, c.product_id, d.price, last_order_date
        FROM user_box_subscription a
        INNER JOIN user b ON a.user_id = b.user_id 
        INNER JOIN box c ON a.box_category_id = c.box_category_id AND a.box_size_id = c.box_size_id
		INNER JOIN product p on p.product_id = c.product_id  
        INNER JOIN box_size d ON a.box_size_id = d.box_size_id
        WHERE a.is_active = True 
        AND subscription_quantity > sent_quantity AND subscription_quantity > 0
        AND box_end_date >= curdate() and p.depot_id = b.depot_id and c.is_active = True
    """
    # Add condition for depot_id if provided
    if depot_id is not None:
        query = base_query + " AND b.depot_id = %s"
        cursor.execute(query, (depot_id,))
    else:
        cursor.execute(base_query)

    # Fetch all results
    results = cursor.fetchall()

    cursor.close()

    # Return results
    return results




def update_subscription_quantity(user_box_subscription_id):
    # Establish database connection and create cursor
    cursor = getCursor()

    # Update sent quantity and last order date for the specified subscription
    cursor.execute("""UPDATE user_box_subscription 
                        SET 
                            sent_quantity = sent_quantity + 1, 
                            last_order_date = CURDATE()
                        WHERE 
                            user_box_subscription_id = %s;""",
                       (user_box_subscription_id,))
    
    # Update the is_active status based on whether the sent quantity matches the subscription quantity
    cursor.execute("""UPDATE user_box_subscription 
                        SET 
                            is_active = CASE 
                                            WHEN subscription_quantity = sent_quantity THEN FALSE 
                                            ELSE is_active 
                                        END 
                        WHERE 
                            user_box_subscription_id = %s;""",
                       (user_box_subscription_id,))

    cursor.close()



def activate_subscription(user_box_subscription_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    
    # Update the is_active status to True for the specified subscription
    cursor.execute("""UPDATE user_box_subscription 
                        SET 
                            is_active = True
                        WHERE 
                            user_box_subscription_id = %s;""",
                       (user_box_subscription_id,))
    
    cursor.close()



def update_product_quantity(product_id, new_quantity):
    # Establish database connection and create cursor
    cursor = getCursor()

    # Define the update query to update the stock quantity of the specified product
    update_query = """
        UPDATE product
        SET stock_quantity = %s
        WHERE product_id = %s
    """
    
    # Execute the update query with the new quantity and product ID as parameters
    cursor.execute(update_query, (new_quantity, product_id))
    
    cursor.close()



def log_perished_product_removal(product_id, product_name, units_removed):
    # Establish database connection and create cursor
    cursor = getCursor()

    # Define the query to insert the log of perished product removal
    log_query = """
        INSERT INTO perished_product_log (product_id, product_name, units_removed)
        VALUES (%s, %s, %s)
    """
    
    # Execute the query with the provided parameters
    cursor.execute(log_query, (product_id, product_name, units_removed))
    
    cursor.close()



def get_perished_product_logs(page, per_page):
    # Calculate the offset for pagination
    offset = (page - 1) * per_page
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve perished product logs with pagination
    query = """
        SELECT product_name, units_removed, removal_date
        FROM perished_product_log
        ORDER BY removal_date DESC
        LIMIT %s OFFSET %s
    """
    # Execute the query with per_page and offset as parameters
    cursor.execute(query, (per_page, offset))
    # Fetch perished product logs
    logs = cursor.fetchall()

    # Define the query to count the total number of logs
    count_query = "SELECT COUNT(*) FROM perished_product_log"
    cursor.execute(count_query)
    # Fetch the total number of logs
    total_logs = cursor.fetchone()[0]

    cursor.close()
    # Return perished product logs and total number of logs
    return logs, total_logs




def get_all_account_holders():
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve all account holders with related information
    query = """
        SELECT ah.account_holder_id, ah.business_name, ca.credit_limit, ca.current_balance, u.first_name, u.last_name, d.depot_name
        FROM account_holder ah
        INNER JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
        INNER JOIN user_profile u ON ah.user_id = u.user_id
        INNER JOIN user us ON u.user_id = us.user_id
        INNER JOIN depot d ON us.depot_id = d.depot_id
    """
    # Execute the query
    cursor.execute(query)
    # Fetch all account holders
    account_holders = cursor.fetchall()

    cursor.close()
    # Return account holders
    return account_holders




def update_credit_limit(account_holder_id, new_credit_limit):
    # Establish database connection and create cursor
    cursor = getCursor()
    
    # Define the query to update the credit limit for the specified account holder
    query = """
        UPDATE credit_account
        SET credit_limit = %s
        WHERE credit_account_id = (
            SELECT credit_account_id
            FROM account_holder
            WHERE account_holder_id = %s
        )
    """
    # Execute the update query with the new credit limit and account holder ID as parameters
    cursor.execute(query, (new_credit_limit, account_holder_id))

    # Define the query to fetch the business name of the account holder
    query = """
        SELECT business_name
        FROM account_holder
        WHERE account_holder_id = %s
    """
    # Execute the query to fetch the business name
    cursor.execute(query, (account_holder_id,))
    # Fetch the business name
    business_name = cursor.fetchone()[0]
 
    cursor.close()
    
    # Return account holder ID and business name
    return account_holder_id, business_name



def get_account_holders_by_depot(depot_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    
    # Define the query to retrieve account holders by depot
    query = """
        SELECT ah.account_holder_id, ah.business_name, ca.credit_limit, ca.current_balance, u.first_name, u.last_name, d.depot_name
        FROM account_holder ah
        INNER JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
        INNER JOIN user_profile u ON ah.user_id = u.user_id
        INNER JOIN user us ON u.user_id = us.user_id
        INNER JOIN depot d ON us.depot_id = d.depot_id
        WHERE d.depot_id = %s
    """
    # Execute the query with depot_id as parameter
    cursor.execute(query, (depot_id,))
    # Fetch account holders for the specified depot
    account_holders = cursor.fetchall()

    cursor.close()
    # Return account holders
    return account_holders




def cancel_customer_subscription(user_box_subscription_id, grandtotal):
    # Establish database connection and create cursor
    cursor = getCursor()

    # Query to retrieve order ID associated with the subscription
    query = """
            SELECT b.order_hdr_id
            FROM user_box_subscription a
            INNER JOIN order_hdr b ON a.user_id = b.user_id 
            WHERE b.purpose = "subscription_payment" AND a.is_active = True 
            AND b.is_active = True AND a.user_box_subscription_id  = %s
            """
    cursor.execute(query, (user_box_subscription_id,))
    row = cursor.fetchone()

    # If the order ID is found, cancel the subscription order
    if row:
        cursor.execute("UPDATE order_hdr SET is_active = 0, status_id = 5, total_price = %s WHERE order_hdr_id = %s", (grandtotal, row[0],))

    # Query to retrieve remaining quantity, box size, and user ID
    query = """
        SELECT (subscription_quantity - sent_quantity) AS Quantity, box_size_id, user_id
        FROM user_box_subscription
        WHERE user_box_subscription_id = %s
    """
    cursor.execute(query, (user_box_subscription_id,))
    row = cursor.fetchone()

    # If details are found, extract remaining quantity, box size, and user ID
    if row:
        remaining_quantity = row[0]
        box_size = row[1]
        user_id = row[2]

    # Query to retrieve price of the box size
    query = """
        SELECT price
        FROM box_size
        WHERE box_size_id = %s
    """
    cursor.execute(query, (box_size,))
    price = cursor.fetchone()[0]

    # Update the subscription status to inactive and set subscription quantity to sent quantity
    query = """
        UPDATE user_box_subscription SET is_active = False, subscription_quantity = sent_quantity
        WHERE user_box_subscription_id = %s
    """
    cursor.execute(query, (user_box_subscription_id,))

    cursor.close()

    # Calculate refund amount based on remaining quantity, box size price, and shipping fee
    shipping_fee = get_customer_shipping_fee(user_id)
    refund_amount = int(remaining_quantity) * Decimal(shipping_fee)
    refund_amount += int(remaining_quantity) * Decimal(price)
    return refund_amount





def get_current_user_id():
    # Retrieve the current user ID from the session
    return session.get('user_id')


def update_account_holder_balance_after_payment(amount, user_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    try:
        # Define the update query to deduct the payment amount from the current balance of the account holder
        update_query = """
            UPDATE credit_account
            SET current_balance = current_balance - %s
            WHERE credit_account_id = (SELECT credit_account_id FROM account_holder WHERE user_id = %s)
        """
        # Execute the update query with the amount and user ID as parameters
        cursor.execute(update_query, (amount, user_id))
    except Exception as e:
        # Print error message if an exception occurs during the update
        print(f"Error updating account holder balance: {e}")
    finally:

        cursor.close()


        
def get_credit_limit_and_due_date(user_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Query to retrieve credit limit for the user
    query = "SELECT credit_limit FROM credit_account WHERE account_holder_id = %s"
    cursor.execute(query, (user_id,))
    # Fetch the result
    result = cursor.fetchone()

    cursor.close()
    
    # If the result is found
    if result:
        # Extract credit limit from the result
        credit_limit = result[0]
        # Get the current date
        today = datetime.date.today()
        # Find the last day of the current month
        last_day_of_month = monthrange(today.year, today.month)[1]
        # Calculate the due date as the last day of the current month
        due_date = datetime.date(today.year, today.month, last_day_of_month)
        # Return credit limit and due date as a dictionary
        return {'credit_limit': credit_limit, 'due_date': due_date}
    # If no result is found, return None
    return None


        
def view_payment_history(user_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve payment history for the user
    query = """
        SELECT payment_id, amount, payment_date, status 
        FROM payment_history 
        WHERE user_id = %s
        ORDER BY payment_date DESC
    """
    # Execute the query with the user ID as parameter
    cursor.execute(query, (user_id,))
    # Fetch all results
    results = cursor.fetchall()

    cursor.close()
    # Return payment history results
    return results


def get_payment_history_by_user_id(user_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve payment history for the user
    query = """
        SELECT p.payment_id, p.amount, p.payment_date, pm.method_description
        FROM payment p
        JOIN order_hdr oh ON p.order_hdr_id = oh.order_hdr_id
        JOIN payment_method pm ON p.payment_method_id = pm.payment_method_id
        WHERE oh.user_id = %s
        ORDER BY p.payment_date DESC
    """
    # Execute the query with the user ID as parameter
    cursor.execute(query, (user_id,))
    # Fetch all results
    results = cursor.fetchall()

    cursor.close()
    # Return payment history results
    return results




def retrieve_subscription(user_box_subscription_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Define the query to retrieve subscription details
    query = """
        SELECT b.order_hdr_id, invoice_num, payment_id, box_size_id, sent_quantity
        FROM user_box_subscription a
        INNER JOIN order_hdr b ON a.user_id = b.user_id 
        INNER JOIN invoice c ON b.order_hdr_id = c.order_hdr_id
        WHERE b.purpose = "subscription_payment" AND a.is_active = True 
        AND b.is_active = True AND a.user_box_subscription_id = %s
    """
    # Execute the query with the user_box_subscription_id as parameter
    cursor.execute(query, (user_box_subscription_id,))
    # Fetch the result
    row = cursor.fetchone()

    # If the result is found
    if row:
        # Extract subscription details from the row
        order_hdr_id = row[0]
        invoice_num = row[1]
        payment_id = row[2]
        box_size = row[3]
        quantity_sent = row[4]
        
        # Return subscription details
        return order_hdr_id, invoice_num, payment_id, box_size, quantity_sent



def get_payment_due_date():
    # Get the current date
    today = datetime.date.today()
    # Calculate the first day of the next month by adding 32 days to the current date
    # (ensuring it passes the end of the current month)
    next_month_first_day = datetime.date(today.year, today.month, 1) + datetime.timedelta(days=32)
    # Calculate the last day of the current month by replacing the day with 1 and subtracting 1 day
    last_day_of_month = next_month_first_day.replace(day=1) - datetime.timedelta(days=1)
    # Format the last day of the month as a string in 'dd-mm-YYYY' format and return
    return last_day_of_month.strftime('%d-%m-%Y')



def get_outstanding_balances_for_depot(depot_id):
    cursor = getCursor()

    # Get the current date and calculate the last day of the month
    today = datetime.date.today()
    last_day_of_month = monthrange(today.year, today.month)[1]
    end_of_month_date = datetime.date(today.year, today.month, last_day_of_month)
    
    # Define the query to retrieve outstanding balances for account holders of the given depot
    query = """
        SELECT ah.account_holder_id, ah.business_name, ca.credit_limit, ca.current_balance, 
               DATE_FORMAT(%s, '%d-%m-%Y') AS due_date, 
               CASE 
                   WHEN ca.current_balance > 0 AND %s < CURDATE() THEN ca.current_balance 
                   ELSE 0 
               END AS overdue_amount
        FROM account_holder ah
        JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
        JOIN user u ON ah.user_id = u.user_id
        WHERE u.depot_id = %s
        ORDER BY overdue_amount DESC, ca.current_balance DESC
    """
    # Execute the query with the end_of_month_date and depot_id as parameters
    cursor.execute(query, (end_of_month_date, end_of_month_date, depot_id))
    # Fetch all results
    results = cursor.fetchall()



    cursor.close()
    # Return outstanding balances results
    return results




def get_all_active_subscription_display(depot_id=None):
    cursor = getCursor()
    base_query = """
        SELECT DISTINCT depot_name, a.user_id, user_box_subscription_id, frequency, category, size_name,
        (subscription_quantity - sent_quantity) AS quantity, 
        b.first_name, b.last_name, a.box_frequency_id, last_order_date
        FROM user_box_subscription a
        INNER JOIN user y ON a.user_id = y.user_id
        INNER JOIN user_profile b ON a.user_id = b.user_id
        INNER JOIN box_category c ON a.box_category_id = c.box_category_id 
        INNER JOIN box_frequency f ON a.box_frequency_id = f.box_frequency_id
        INNER JOIN box_size d ON a.box_size_id = d.box_size_id
        INNER JOIN box x ON a.box_category_id = x.box_category_id AND a.box_size_id = x.box_size_id
        INNER JOIN depot ON y.depot_id = depot.depot_id
        WHERE a.is_active = True and x.is_active = 1 
        AND subscription_quantity > sent_quantity AND subscription_quantity > 0
        AND box_end_date >= CURDATE()
    """
    # Add condition for depot_id if provided
    if depot_id is not None:
        query = base_query + " AND y.depot_id = %s"
        cursor.execute(query, (depot_id,))
    else:
        cursor.execute(base_query)

    # Fetch all results
    results = cursor.fetchall()



    cursor.close()

    # Return subscription results
    return results


def get_customer_subscription_details(depot_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Execute query to retrieve all subscriptions
    cursor.execute("""
        SELECT depot_name, up.first_name, up.last_name, b.frequency, c.category, d.size_name
        FROM user_box_subscription a
        INNER JOIN box_frequency b on a.box_frequency_id = b.box_frequency_id
        INNER JOIN box_category c on a.box_category_id = c.box_category_id
        INNER JOIN box_size d on a.box_size_id = d.box_size_id
        INNER JOIN user u on u.user_id = a.user_id
        INNER JOIN user_profile up ON u.user_id = up.user_id
        INNER JOIN depot ON u.depot_id = depot.depot_id
        WHERE a.is_active = true AND u.depot_id = %s""", (depot_id,))
    
    # Fetch all
    subscriptions = cursor.fetchall()



    cursor.close()
    # Return customer subscriptions
    return subscriptions    

def get_account_holder_details(account_holder_id, selected_month=None):
    cursor = getCursor()
    
    # Query to retrieve basic account holder details
    query = """
        SELECT up.first_name, up.last_name, ah.business_name, ah.business_address, ah.business_phone, 
               ca.credit_limit, ca.current_balance,
               (ca.credit_limit - ca.current_balance) AS remaining_balance
        FROM account_holder ah
        JOIN user_profile up ON ah.user_id = up.user_id
        JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
        WHERE ah.account_holder_id = %s
    """
    cursor.execute(query, (account_holder_id,))
    account_holder_details = cursor.fetchone()
    
    # Calculate payment due date and overdue amount
    today = date.today()
    last_day_of_month = monthrange(today.year, today.month)[1]
    payment_due_date = date(today.year, today.month, last_day_of_month)
    
    overdue_amount = 0
    if today > payment_due_date:
        overdue_amount = account_holder_details[6]
    
    payment_due_date_str = payment_due_date.strftime('%d/%m/%Y')
    
    # Append payment due date and overdue amount to account holder details
    account_holder_details += (payment_due_date_str, overdue_amount)
    
    # Query to retrieve purchase records
    purchase_query = """
        SELECT oh.order_hdr_id, DATE_FORMAT(oh.order_date, '%d-%m-%Y'), oh.total_price, pm.method_description, os.status_name, so.shipping_option_name
        FROM order_hdr oh
        JOIN payment p ON oh.order_hdr_id = p.order_hdr_id
        JOIN payment_method pm ON p.payment_method_id = pm.payment_method_id
        JOIN order_status os ON oh.status_id = os.status_id
        JOIN shipping_option so ON oh.shipping_option_id = so.shipping_option_id
        WHERE oh.user_id = (SELECT user_id FROM account_holder WHERE account_holder_id = %s)
    """
    
    # Add condition for selected_month if provided
    if selected_month:
        # Define start and end dates for the selected month
        start_date = f"{selected_month}-01"
        year, month = map(int, selected_month.split('-'))
        end_date = f"{selected_month}-{monthrange(year, month)[1]}"
        # Add condition to the purchase query for orders within the selected month
        purchase_query += " AND oh.order_date BETWEEN %s AND %s"
        cursor.execute(purchase_query, (account_holder_id, start_date, end_date))
    else:
        cursor.execute(purchase_query, (account_holder_id,))
    
    # Fetch purchase records
    purchase_records = cursor.fetchall()
    cursor.close()
    
    # Return account holder details and purchase records
    return account_holder_details, purchase_records




def generate_months_list():
    today = date.today()
    months = []
    # Iterate over the past 12 months
    for i in range(12):
        # Calculate the first day of the month i months ago
        first_day_of_month = today.replace(day=1) - timedelta(days=i*30)
        # Format the month as 'YYYY-MM' and add it to the list
        month = first_day_of_month.strftime('%Y-%m')
        months.append(month)
    # Convert the list to a set to remove duplicates, then back to a sorted list
    return sorted(list(set(months)))



def get_all_staff_members():
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve all staff member details
    query = """
        SELECT u.user_id, u.email, up.first_name, up.last_name, ur.role_name, d.depot_name
        FROM user u
        JOIN user_profile up ON u.user_id = up.user_id
        JOIN user_role ur ON u.role_id = ur.role_id
        JOIN depot d ON u.depot_id = d.depot_id
        WHERE u.role_id IN (3, 4, 5)  -- Filter by role IDs 3 (Manager) and 4 (Staff)
    """
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results
    staff_members = cursor.fetchall()
    
    # Close the cursor
    cursor.close()
    
    # Return the retrieved staff members
    return staff_members




def get_staff_by_depot(depot_id):
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve staff members by depot ID
    cursor.execute("""
        SELECT u.user_id, u.email, up.first_name, up.last_name, ur.role_name, d.depot_name
        FROM user u
        JOIN user_profile up ON u.user_id = up.user_id
        JOIN user_role ur ON u.role_id = ur.role_id
        JOIN depot d ON u.depot_id = d.depot_id
        WHERE u.depot_id = %s AND u.role_id IN (3, 4)  -- Only include staff and managers
    """, (depot_id,))
    
    # Fetch all results
    staff_members = cursor.fetchall()
    
    # Close the cursor
    cursor.close()
    
    # Return the retrieved staff members
    return staff_members




def get_staff_by_id(staff_id):
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve staff information by ID
    query = """
        SELECT u.user_id, u.email, up.first_name, up.last_name, up.address, up.phone_number, up.date_of_birth, u.role_id, u.depot_id
        FROM user u
        JOIN user_profile up ON u.user_id = up.user_id
        WHERE u.user_id = %s
    """
    
    # Execute the query with the provided staff ID
    cursor.execute(query, (staff_id,))
    
    # Fetch the first result
    staff_member = cursor.fetchone()
    
    # Close the cursor
    cursor.close()
    
    # Return the retrieved staff member
    return staff_member



def get_all_roles():
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve all roles
    cursor.execute("""
        SELECT role_id, role_name 
        FROM user_role 
        WHERE role_name IN ('Staff', 'Local Manager', 'National Manager')
    """)
    
    # Fetch all results
    roles = cursor.fetchall()
    
    # Close the cursor
    cursor.close()
    
    # Return the retrieved roles
    return roles



def update_staff(staff_id, email, first_name, last_name, address, phone_number, date_of_birth, role_id, depot_id, hashed_password):
    # Get database cursor
    cursor = getCursor()
    
    # Get database connection
    connection = cursor._cnx  
    
    try:
        # Update user table with new email, role ID, and depot ID
        cursor.execute("""
            UPDATE user SET email = %s, role_id = %s, depot_id = %s WHERE user_id = %s
        """, (email, role_id, depot_id, staff_id))
        
        # Update user_profile table with new first name, last name, address, phone number, and date of birth
        cursor.execute("""
            UPDATE user_profile SET first_name = %s, last_name = %s, address = %s, phone_number = %s, date_of_birth = %s WHERE user_id = %s
        """, (first_name, last_name, address, phone_number, date_of_birth, staff_id))
        
        # Update password if hashed_password is provided
        if hashed_password:
            cursor.execute("""
                UPDATE user SET password = %s WHERE user_id = %s
            """, (hashed_password, staff_id))
        
        # Commit the changes to the database
        connection.commit()
    except Exception as e:
        # Rollback in case of error
        connection.rollback()  
        # Raise the exception
        raise e
    finally:
        # Close the cursor
        cursor.close()
        # Close the connection
        connection.close()  




def delete_staff_member(staff_id):
    # Get database cursor
    cursor = getCursor()
    
    # Get database connection
    connection = cursor._cnx 
    
    try:
        # Delete staff member's profile from user_profile table
        cursor.execute("DELETE FROM user_profile WHERE user_id = %s", (staff_id,))
        
        # Delete staff member from user table
        cursor.execute("DELETE FROM user WHERE user_id = %s", (staff_id,))
        
        # Commit the changes to the database
        connection.commit()  
    except Exception as e:
        # Rollback in case of error
        connection.rollback()  
        # Raise the exception
        raise e
    finally:
        # Close the cursor
        cursor.close()
        # Close the connection
        connection.close()  



def add_new_staff(email, first_name, last_name, address, phone_number, date_of_birth, role_id, depot_id, password):
    # Get database cursor
    cursor = getCursor()
    
    # Get database connection
    connection = cursor._cnx
    
    try:
        # Insert new staff member into user table
        cursor.execute("""
            INSERT INTO user (email, password, role_id, depot_id) VALUES (%s, %s, %s, %s)
        """, (email, password, role_id, depot_id))
        
        # Get the user_id of the newly inserted user
        user_id = cursor.lastrowid
        
        # Insert user profile for the new staff member into user_profile table
        cursor.execute("""
            INSERT INTO user_profile (user_id, first_name, last_name, address, phone_number, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, first_name, last_name, address, phone_number, date_of_birth))
        
        # Commit the changes to the database
        connection.commit()  
    except Exception as e:
        # Rollback in case of error
        connection.rollback()  
        # Raise the exception
        raise e
    finally:
        # Close the cursor
        cursor.close()
        # Close the connection
        connection.close()  



def get_discontinued_products():
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve discontinued products along with their details
    query = """
        SELECT product.product_id, product_type.product_type_name, discontinued_date 
        FROM discontinued_products
        JOIN product ON discontinued_products.product_id = product.product_id
        JOIN product_type ON product.product_type_id = product_type.product_type_id
    """
    
    # Execute the query
    cursor.execute(query)
    
    # Fetch all results
    discontinued_products_list = cursor.fetchall()
    
    # Close the cursor
    cursor.close()
    
    # Return the list of discontinued products
    return discontinued_products_list



def get_credit_account_id(user_id):
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve credit account ID for a given user ID
    cursor.execute("SELECT credit_account_id FROM account_holder WHERE user_id = %s", (user_id,))
    
    # Fetch the credit account ID
    credit_account_id = cursor.fetchone()[0]
    
    # Return the credit account ID
    return credit_account_id




def approve_credit_limit_request(new_limit, request_id):
    # Get database cursor
    cursor = getCursor()
    
    # Update the credit limit request with the approved limit and mark it as actioned
    cursor.execute("UPDATE credit_limit_change_request SET approved_limit = %s, is_actioned = 1 WHERE request_id = %s", (new_limit, request_id))



def reject_credit_limit_request(request_id):
    # Get database cursor
    cursor = getCursor()
    
    # Mark the credit limit request as actioned (rejected)
    cursor.execute("UPDATE credit_limit_change_request SET is_actioned = 1 WHERE request_id = %s", (request_id,))



def credit_limit_request_exists_check(user_id):
    # Get database cursor
    cursor = getCursor()
    
    # Check the database if there is already a pending credit limit request from the same account holder
    cursor.execute('SELECT * FROM credit_limit_change_request WHERE user_id = %s AND is_actioned = 0', (user_id,))
    
    # Fetch the credit limit request, if any
    user_request = cursor.fetchone()
    
    # Close the cursor
    cursor.close()
    
    # Return the credit limit request, if it exists
    return user_request



def get_user_id_from_credit_limit_request(request_id):
    # Get database cursor
    cursor = getCursor()
    
    # Retrieve the user ID associated with the given credit limit request ID
    cursor.execute('SELECT user_id FROM credit_limit_change_request WHERE request_id = %s', (request_id,))
    
    # Fetch the user ID
    user_id = cursor.fetchone()
    
    # Close the cursor
    cursor.close()
    
    # Return the user ID
    return user_id[0]



def update_credit_limit_after_processing_request(new_limit, credit_account_id):
    # Get database cursor
    cursor = getCursor()
    
    # Update the credit limit in the credit_account table
    cursor.execute("UPDATE credit_account SET credit_limit = %s WHERE credit_account_id = %s", (new_limit, credit_account_id))




def get_depot_name_by_id(depot_id):
    # Get database cursor
    cursor = getCursor()
    
    # SQL query to retrieve depot name by depot ID
    query = "SELECT depot_name FROM depot WHERE depot_id = %s"
    
    # Execute the query with the provided depot ID
    cursor.execute(query, (depot_id,))
    
    # Fetch the result
    depot = cursor.fetchone()
    
    # Close the cursor
    cursor.close()
    
    # Return the depot name if found, otherwise return a default value
    return depot[0] if depot else "All Depots"

def get_account_holder_current_credit_balance(account_holder_id):
    # Get the cursor
    cursor = getCursor()

    # Execute the SQL query to retrieve the current credit balance based on account_holder_id
    cursor.execute("""
            SELECT ca.current_balance
            FROM account_holder ah
            JOIN credit_account ca ON ah.credit_account_id = ca.credit_account_id
            WHERE ah.account_holder_id = %s
        """, (account_holder_id,))
    
    # Fetch the current credit balance
    current_credit_balance = cursor.fetchone()

    # Close the cursor
    cursor.close()

    # Return the current credit balance, if available, otherwise return 0
    return current_credit_balance[0] if current_credit_balance and current_credit_balance[0] is not None else 0

def update_account_holder_balance(amount, account_holder_id):
    # Establish database connection and create cursor
    cursor = getCursor()
    try:
        # Define the update query to deduct the payment amount from the current balance of the account holder
        update_query = """
            UPDATE credit_account
            SET current_balance = current_balance - %s
            WHERE credit_account_id = (SELECT credit_account_id FROM account_holder WHERE account_holder_id = %s)
        """
        # Execute the update query with the amount and account_holder_id as parameters
        cursor.execute(update_query, (amount, account_holder_id))
        cursor.connection.commit()
    except Exception as e:
        # Print error message if an exception occurs during the update
        print(f"Error updating account holder balance: {e}")
    finally:


        cursor.close()


def can_edit_box_items(box_id):
    cursor = getCursor()
    # Retrieve the count of order details with the box ID
    cursor.execute("""SELECT COUNT(*) FROM box b 
                   INNER JOIN order_detail od ON b.product_id = od.product_id WHERE b.box_id = %s""", (box_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    if count > 0:
        return False
    else:
        return True


def get_products_by_depot_status_search(depot_id=None, status='All', search='', page=1, per_page=10):
    # Establish database connection and create cursor
    cursor = getCursor()
    # Calculate the offset for pagination
    offset = (page - 1) * per_page
    # Initial query to retrieve product information
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

    # Check if depot_id is provided and not None
    if depot_id is not None:
        if depot_id != 0:  # Filter by specific depot
            query += " AND p.depot_id = %s"
            params.append(depot_id)

    # Check if status filter is applied
    if status != 'All':
        query += " HAVING status = %s"
        params.append(status)

    # Check if search query is provided
    if search:
        query += " AND pt.product_type_name LIKE %s"
        params.append(f"%{search}%")

    # Add pagination and ordering to the query
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

    # Execute the query with parameters
    cursor.execute(query, params)

    # Fetch all products
    products = cursor.fetchall()

    # Adjust count query to account for status filtering and search query
    count_query = """
        SELECT COUNT(*)
        FROM product p
        JOIN product_type pt ON p.product_type_id = pt.product_type_id
        JOIN product_weight pw ON pt.product_weight_id = pw.product_weight_id
        WHERE p.is_active = 1
    """
    count_params = []

    if depot_id != 0:
        count_query += " AND p.depot_id = %s"
        count_params.append(depot_id)
    if status != 'All':
        count_query += " HAVING status = %s"
        count_params.append(status)
    if search:
        count_query += " AND pt.product_type_name LIKE %s" # search prodcut name by key word
        count_params.append(f"%{search}%")

    # Execute count query to get total number of records
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]




    cursor.close()

    # Return products and total count
    return products, total