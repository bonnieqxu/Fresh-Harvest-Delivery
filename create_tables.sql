DROP SCHEMA IF EXISTS fhd;
CREATE SCHEMA fhd;
USE fhd;

CREATE TABLE user_role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE depot (
    depot_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(40) NOT NULL,
    role_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
	depot_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES user_role(role_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (depot_id) REFERENCES depot(depot_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE user_profile (
    user_profile_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    phone_number VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE credit_account (
    credit_account_id INT AUTO_INCREMENT PRIMARY KEY,
    credit_limit DECIMAL(10,2) NOT NULL,
    current_balance DECIMAL(10,2) DEFAULT 0.00 -- Total outstanding balance to be paid
);

CREATE TABLE account_holder (
    account_holder_id INT AUTO_INCREMENT PRIMARY KEY,
    business_name VARCHAR(50) NOT NULL,
    business_address VARCHAR(255) NOT NULL,
	business_phone VARCHAR(20) NOT NULL,
    user_id INT NOT NULL,
    credit_account_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (credit_account_id) REFERENCES credit_account(credit_account_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE promotion_type (
    promotion_type_id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255),
	discount_rate DECIMAL(10,2) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE product_weight (
    product_weight_id INT AUTO_INCREMENT PRIMARY KEY,
    weight DECIMAL(10, 2) NOT NULL,  -- The weight amount, e.g., 0.5 for 500 grams, 1 for 1 kilogram
    unit VARCHAR(10) NOT NULL,     -- Unit of weight, e.g., 'kg', 'lb'
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- veges, fruits
CREATE TABLE product_category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- potato, apple
CREATE TABLE product_type(
	product_type_id INT AUTO_INCREMENT PRIMARY KEY,
    product_type_name VARCHAR(50) NOT NULL,
    product_weight_id INT NOT NULL,
    product_image LONGBLOB,
    description VARCHAR(255),
    category_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
	FOREIGN KEY (category_id) REFERENCES product_category(category_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (product_weight_id) REFERENCES product_weight(product_weight_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    orig_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL,
    depot_id INT NOT NULL,
    product_type_id INT NOT NULL,
    promotion_type_id INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (depot_id) REFERENCES depot(depot_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (product_type_id) REFERENCES product_type(product_type_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (promotion_type_id) REFERENCES promotion_type(promotion_type_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE box_subscription (
    box_subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    frequency ENUM('weekly', 'fortnightly', 'monthly') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE box_size (
    box_size_id INT AUTO_INCREMENT PRIMARY KEY,
    size_name ENUM('small', 'medium', 'large') UNIQUE NOT NULL,
    max_num INT NOT NULL,
	price DECIMAL(10,2) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE box (
    box_id INT AUTO_INCREMENT PRIMARY KEY,
    box_name VARCHAR(80) NOT NULL,
    box_description VARCHAR(255),
    box_size_id INT NOT NULL,
    box_subscription_id INT,  -- Optional link to a subscription plan, NULL if no subscription is associated
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (box_size_id) REFERENCES box_size(box_size_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (box_subscription_id) REFERENCES box_subscription(box_subscription_id)
	ON UPDATE CASCADE
	ON DELETE SET NULL  -- Set to NULL if the subscription is deleted
);

CREATE TABLE box_content (
    box_content_id INT AUTO_INCREMENT PRIMARY KEY,
    box_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (box_id) REFERENCES box(box_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE order_status (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(100) NOT NULL,  -- confirmed, processing, shipped, delivered, cancelled
    description VARCHAR(255)
);

CREATE TABLE shipping_option (
    shipping_option_id INT AUTO_INCREMENT PRIMARY KEY,
    shipping_option_name VARCHAR(50) NOT NULL,  -- Description of the shipping option, e.g., "Standard", "Express"
    price DECIMAL(6,2) NOT NULL,       -- Shipping price
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE order_hdr (
    order_hdr_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status_id INT NOT NULL,
    shipping_option_id INT NOT NULL, 
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES order_status(status_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY (shipping_option_id) REFERENCES shipping_option(shipping_option_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE order_detail (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_hdr_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    line_total_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_hdr_id) REFERENCES order_hdr(order_hdr_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE credit_account_order (
    credit_account_order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_hdr_id INT NOT NULL,
	credit_account_id INT NOT NULL,
    FOREIGN KEY (order_hdr_id) REFERENCES order_hdr(order_hdr_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY (credit_account_id) REFERENCES credit_account(credit_account_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE depot_order (
    depot_orderid INT AUTO_INCREMENT PRIMARY KEY,
    order_hdr_id INT NOT NULL,
	depot_id INT NOT NULL,
    FOREIGN KEY (order_hdr_id) REFERENCES order_hdr(order_hdr_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
    FOREIGN KEY (depot_id) REFERENCES depot(depot_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE payment_method (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    method_description VARCHAR(255) -- "credit card", "gift card", "voucher from points"
);

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_hdr_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INT NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (order_hdr_id) REFERENCES order_hdr(order_hdr_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_method(payment_method_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE gst_rate (
	gst_rate_id INT AUTO_INCREMENT PRIMARY KEY,
    percentage DECIMAL(4,2) NOT NULL,
    description VARCHAR(255)  -- NZ GST 15%
);

CREATE TABLE invoice (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    order_hdr_id INT NOT NULL,
    payment_id INT NOT NULL,
    date_issued DATE NOT NULL,
    subtotal_amount DECIMAL(10,2) NOT NULL,
    gst_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    gst_rate_id INT NOT NULL,
    FOREIGN KEY (order_hdr_id) REFERENCES order_hdr(order_hdr_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (gst_rate_id) REFERENCES gst_rate(gst_rate_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE customer_points (
	customer_points_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points_balance INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE points_transaction (
    p_transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points_used INT NOT NULL,
    transaction_date DATE NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE gift_card_option (
    gift_card_option_id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(6,2) DEFAULT 20.00,   -- gift card price
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE gift_card (
    gift_card_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    gift_card_option_id INT NOT NULL,
    current_value DECIMAL(6,2) NOT NULL,
    expiration_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (gift_card_option_id) REFERENCES gift_card_option(gift_card_option_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE gift_card_transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    gift_card_id INT NOT NULL,
    transaction_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(50),
    FOREIGN KEY (gift_card_id) REFERENCES gift_card(gift_card_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE message_status (
    message_status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL, -- "Sent", "Processing", "Processed"
    description VARCHAR(255)
);

CREATE TABLE message_category (
    message_category_id INT AUTO_INCREMENT PRIMARY KEY,
    message_category_name VARCHAR(50) NOT NULL, -- "order", "credit limit"
    description VARCHAR(255)
);

CREATE TABLE message (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    sent_time DATETIME NOT NULL,
    message_status_id INT NOT NULL,
    message_category_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (message_status_id) REFERENCES message_status(message_status_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
    FOREIGN KEY (message_category_id) REFERENCES message_category(message_category_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE message_processed (
    message_processed_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    processed_time DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE news (
    news_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    posted_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE 
);