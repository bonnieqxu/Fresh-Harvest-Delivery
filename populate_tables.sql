USE fhd;


INSERT INTO user_role (role_name) VALUES 
('Customer'),
('Credit Account Holder'),
('Staff'), 
('Local Manager'),
('National Manager');


INSERT INTO depot (location_name, address) VALUES 
('Christchurch', '101 Christchurch Road, Christchurch'), 
('Invercargill', '202 Invercargill Street, Invercargill'), 
('Wellington', '303 Wellington Boulevard, Wellington'), 
('Hamilton', '404 Hamilton Avenue, Hamilton'), 
('Auckland', '505 Auckland Lane, Auckland');


INSERT INTO user (email, password, role_id, is_active, depot_id) VALUES 
('james.holden@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 3, TRUE, 1),  -- Christchurch staff
('naomi.nagata@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 4, TRUE, 1),  -- Christchurch manager
('amos.burton@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 3, TRUE, 2),    -- Invercargill staff
('chrisjen.avasarala@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 4, TRUE, 2),  -- Invercargill manager
('alex.kamal@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 3, TRUE, 3),      -- Wellington staff
('bobbie.draper@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 4, TRUE, 3),  -- Wellington manager
('fred.johnson@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 3, TRUE, 4),  -- Hamilton staff
('julie.yao@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 4, TRUE, 4),        -- Hamilton manager
('joe.miller@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 3, TRUE, 5),      -- Auckland staff
('clarissa.mao@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 4, TRUE, 5),  -- Auckland manager
('michael.ang@freshharvest.co.nz', '5f4dcc3b5aa765d61d8327deb882cf99', 5, TRUE, 5),  -- National manager 
('alice.johnson@gmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 1),  -- Customer 1 at Christchurch
('bob.smith@hotmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 1),        -- Customer 2 at Christchurch
('carol.taylor@gmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 2),    -- Customer 1 at Invercargill
('david.brown@hotmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 2),    -- Customer 2 at Invercargill
('eve.white@gmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 3),          -- Customer 1 at Wellington
('frank.jones@hotmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 3),    -- Customer 2 at Wellington
('grace.lee@gmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 4),          -- Customer 1 at Hamilton
('henry.wilson@hotmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 4),  -- Customer 2 at Hamilton
('ivy.morris@gmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 5),        -- Customer 1 at Auckland
('jack.clark@hotmail.com', '5f4dcc3b5aa765d61d8327deb882cf99', 1, TRUE, 5),     -- Customer 2 at Auckland
('samantha.carter@fruitexpress.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 1),  -- Christchurch account holder 1
('daniel.jackson@newworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 1),  -- Christchurch account holder 2
('jack.oneill@fruitexpress.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 2),        -- Invercargill account holder 1
('teal.c@freshworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 2),                  -- Invercargill account holder 2
('vala.maldoran@freshworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 3),     -- Wellington account holder 1
('jonas.quinn@freshworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 3),        -- Wellington account holder 2
('george.hammond@freshworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 4),    -- Hamilton account holder 1
('janet.fraiser@newworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 4),    -- Hamilton account holder 2
('cameron.mitchell@fruitexpress.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 5),-- Auckland account holder 1
('carolyn.lam@newworld.com', '5f4dcc3b5aa765d61d8327deb882cf99', 2, TRUE, 5);        -- Auckland account holder 2


INSERT INTO user_profile (user_id, first_name, last_name, address, phone_number, date_of_birth) VALUES 
(1, 'James', 'Holden', '123 Main St, Christchurch', '021665323', DATE('1988-02-15')),          -- Christchurch staff
(2, 'Naomi', 'Nagata', '456 Elm St, Christchurch', '021445778', DATE('1985-07-22')),          -- Christchurch manager
(3, 'Amos', 'Burton', '789 Oak St, Invercargill', '021778945', DATE('1990-11-30')),            -- Invercargill staff
(4, 'Chrisjen', 'Avasarala', '101 Pine St, Invercargill', '021998877', DATE('1982-04-05')),    -- Invercargill manager
(5, 'Alex', 'Kamal', '111 Cedar St, Wellington', '021112233', DATE('1987-09-12')),            -- Wellington staff
(6, 'Bobbie', 'Draper', '222 Maple St, Wellington', '021335588', DATE('1984-01-18')),        -- Wellington manager
(7, 'Fred', 'Johnson', '333 Walnut St, Hamilton', '021554499', DATE('1989-06-25')),          -- Hamilton staff
(8, 'Julie', 'Yao', '444 Cherry St, Hamilton', '021778822', DATE('1983-10-08')),            -- Hamilton manager
(9, 'Joe', 'Miller', '555 Orange St, Auckland', '021998877', DATE('1986-03-20')),            -- Auckland staff
(10, 'Clarissa', 'Mao', '666 Grape St, Auckland', '021665544', DATE('1992-08-03')),        -- Auckland manager
(11, 'Michael', 'Ang', '123 Oak St, National City', '02788779966', DATE('1975-03-10')),          -- National manager 
(12, 'Alice', 'Johnson', '678 Maple Ave, Christchurch', '0214579986', DATE('1989-07-25')),       -- Customer 1 at Christchurch
(13, 'Bob', 'Smith', '123 Poplar Lane, Christchurch', '0276598881', DATE('1991-11-18')),         -- Customer 2 at Christchurch
(14, 'Carol', 'Taylor', '456 Birch Rd, Invercargill', '021443212', DATE('1980-05-03')),         -- Customer 1 at Invercargill
(15, 'David', 'Brown', '789 Pine St, Invercargill', '0214579986', DATE('1987-09-12')),          -- Customer 2 at Invercargill
(16, 'Eve', 'White', '222 Spruce Dr, Wellington', '021443212', DATE('1978-12-30')),             -- Customer 1 at Wellington
(17, 'Frank', 'Jones', '333 Fir St, Wellington', '027659888', DATE('1985-04-17')),              -- Customer 2 at Wellington
(18, 'Grace', 'Lee', '444 Oak Ave, Hamilton', '021443212', DATE('1983-10-08')),                 -- Customer 1 at Hamilton
(19, 'Henry', 'Wilson', '555 Cedar Pl, Hamilton', '0214579986', DATE('1979-06-25')),            -- Customer 2 at Hamilton
(20, 'Ivy', 'Morris', '666 Lime St, Auckland', '0276598882', DATE('1984-08-20')),                -- Customer 1 at Auckland
(21, 'Jack', 'Clark', '777 Peach Rd, Auckland', '021443212', DATE('1990-02-15'));               -- Customer 2 at Auckland


INSERT INTO credit_account (credit_limit, current_balance) VALUES 
(500.00, 0.00), 
(800.00, 0.00),
(1000.00, 0.00), 
(1500.00, 0.00),
(2000.00, 0.00), 
(3000.00, 0.00),
(500.00, 0.00), 
(800.00, 0.00),
(1000.00, 0.00), 
(1500.00, 0.00);

-- Populate account holder table with real street names and local phone numbers
INSERT INTO account_holder (business_name, business_address, business_phone, user_id, credit_account_id) VALUES 
('Fruit Express', '123 Cashel St, Christchurch', '0212233445', 22, 1),       -- Christchurch account holder 1
('New World', '456 Colombo St, Christchurch', '036562233', 23, 2),          -- Christchurch account holder 2
('Fruit Express', '789 Dee St, Invercargill', '0274455667', 24, 3),                -- Invercargill account holder 1
('Fresh World', '101 Esk St, Invercargill', '0275566778', 25, 4),                            -- Invercargill account holder 2
('Fresh World', '222 Lambton Quay, Wellington', '042255636', 26, 5),            -- Wellington account holder 1
('Fresh World', '333 Cuba St, Wellington', '0217788990', 27, 5),                   -- Wellington account holder 2
('Fresh World', '444 Victoria St, Hamilton', '072255464', 28, 7),          -- Hamilton account holder 1
('New World', '555 Hood St, Hamilton', '0219900112', 29, 8),              -- Hamilton account holder 2
('Fruit Express', '666 Queen St, Auckland', '093032266', 30, 9),       -- Auckland account holder 1
('New World', '777 Ponsonby Rd, Auckland', '096365566', 31, 10);                       -- Auckland account holder 2
    
INSERT INTO promotion_type (description, discount_rate, start_date, end_date, is_active) VALUES 
('Friend and Family Discount', 0.15, '2024-05-01', '2023-04-30', TRUE),
('Seasonal Special', 0.10, '2024-05-07', '2025-05-09', TRUE),
('Summer Sale', 0.10, '2024-06-01', '2025-06-30', TRUE);
    
    
INSERT INTO product_weight (weight, unit) VALUES
(0.1, 'kg'),   -- for smaller quantities like herbs or specialty items.
(0.25, 'kg'),  -- for smaller packaged items or produce sold in bunches.
(0.5, 'kg'),   -- for many produce items and suitable for individual use.
(1, 'kg'),     -- Standard for typical consumer purchases.
(2, 'kg'),     -- Useful for larger quantity retail packages.
(5, 'kg'),     -- Small box
(10, 'kg'),    -- Medium box
(15, 'kg');    -- Large box
    
    
INSERT INTO product_category (category_name) VALUES
('Fruits'),
('Vegetables'),
('Herbs'),
('Salads'),
('Eggs'),
('Honey'),
('Permade Box');
    
-- Populate product type 
-- Fruits
INSERT INTO product_type (product_type_name, product_weight_id, description, category_id) VALUES
-- premade box
-- Vegetable Boxes
('Veggie Delight Box - Small', 6, 'A small box containing up to 5 kg of fresh vegetables, tailored for individuals or small families.', 7),
('Veggie Delight Box - Medium', 7, 'A medium box containing up to 10 kg of a variety of fresh vegetables, perfect for medium-sized families.',  7),
('Veggie Delight Box - Large',  8, 'A large box containing up to 15 kg of assorted fresh vegetables, ideal for large families or gatherings.', 7),
-- Fruit Boxes
('Fruit Blast Box - Small', 6, 'A small box containing up to 5 kg of seasonal fruits, curated to provide a delightful mix.',  7),
('Fruit Blast Box - Medium', 7, 'A medium box containing up to 10 kg of the finest seasonal fruits, ensuring variety and taste.', 7),
('Fruit Blast Box - Large', 8, 'A large box containing up to 15 kg of premium, seasonal fruits, great for fruit lovers and large gatherings.', 7),    
-- Mixed Fruit and Veggie Boxes   
('Mixed Harvest Box - Small', 6, 'A small box maxed out with up to 5 kg of a balanced mix of fruits and vegetables, ideal for individuals or small families.', 7),
('Mixed Harvest Box - Medium',  7, 'A medium box maxed out with up to 10 kg of a generous assortment of fruits and vegetables, perfect for medium-sized families.', 7),
('Mixed Harvest Box - Large', 8, 'A large box filled to the brim with up to 15 kg of a diverse range of fruits and vegetables, great for large families or gatherings.', 7), 
-- Fruits
('Apple', 4, 'Fresh red apples, sold in 1 kg bags.', 1),
('Banana', 4, 'Organic bananas, sold in 1 kg batches.', 1),
('Orange', 5, 'Juicy oranges, sold in 2 kg nets.', 1),
('Kiwi', 1, 'Green kiwifruit, sold in 1 kg packs.', 1),
('Blueberry', 1, 'Fresh blueberries, sold in 250 g packs.', 1),
('Strawberry', 2, 'Sweet strawberries, sold in 500 g punnets.', 1),
('Pear', 4, 'Crisp pears, sold in 1 kg packs.', 1),
('Mango', 5, 'Ripe mangoes, sold in packs estimated around 2 kg total.', 1),
('Grapes', 2, 'Seedless grapes, sold in 500 g bunches.', 1),
('Cherry', 2, 'Fresh cherries, sold in 500 g packs.', 1),
-- Vegetables
('Potato', 5, 'Organic potatoes, sold in 2 kg bags.', 2),
('Carrot', 4, 'Crunchy carrots, sold in 1 kg packs.', 2),
('Tomato', 3, 'Ripe tomatoes, sold in 500 g packs.', 2),
('Cucumber', 3, 'Fresh cucumbers, sold per piece, estimated at 500 g each.', 2),
('Pepper', 3, 'Bell peppers, sold in 500 g packs.', 2),
('Broccoli', 3, 'Green broccoli, sold per head, approximately 500 g.', 2),
('Lettuce', 3, 'Crisp lettuce, sold per head, approximately 500 g.', 2),
('Mushroom', 2, 'Fresh mushrooms, sold in 250 g packs.', 2),
('Spinach', 2, 'Organic spinach, sold in 250 g packs.', 2),
('Onion', 4, 'Yellow onions, sold in 1 kg packs.', 2),
-- Herbs
('Basil', 1, 'Organic basil leaves, sold in 100 g packs.', 3),
('Mint', 1, 'Fresh mint leaves, sold in 100 g packs.', 3),
('Parsley', 1, 'Curly parsley, sold in 100 g bunches.', 3),
('Rosemary', 1, 'Fragrant rosemary, sold in 100 g packs.', 3),
('Thyme', 1, 'Fresh thyme, sold in 100 g packs.', 3),
('Oregano', 1, 'Dried oregano, sold in 100 g packs.', 3),
('Cilantro', 1, 'Fresh cilantro, sold in 100 g bunches.', 3),
('Sage', 1, 'Culinary sage, sold in 100 g packs.', 3),
('Dill', 1, 'Fresh dill, sold in 100 g bunches.', 3),
('Chives', 1, 'Garden chives, sold in 100 g bunches.', 3),
-- Salads
('Mixed Salad', 3, 'Pre-mixed green salad, sold in 500 g bags.', 4),
('Caesar Salad', 3, 'Caesar salad mix, sold in 500 g kits.', 4),
('Greek Salad', 3, 'Greek salad kit, sold in 500 g kits.', 4),
('Caprese', 3, 'Caprese salad ingredients, sold in kits totaling around 500 g.', 4),
('Arugula Salad', 2, 'Arugula leaf salad, sold in 250 g packs.', 4),
('Kale Salad', 3, 'Baby kale mix, sold in 500 g bags.', 4),
('Spinach Salad', 2, 'Spinach salad mix, sold in 250 g bags.', 4),
('Cobb Salad', 3, 'Cobb salad ingredients, sold in 500 g kits.', 4),
('Asian Salad', 3, 'Asian style salad mix, sold in 500 g kits.', 4),
('Fruit Salad', 3, 'Mixed fruit salad, sold in 500 g containers.', 4),
-- Egg
-- Half dozen entries
('Jumbo Cage-Free Eggs - Half Dozen', 3, 'Cage-free eggs, sold in packs of half a dozen, Jumbo size (size 8).', 5),
('Large Cage-Free Eggs - Half Dozen', 3, 'Cage-free eggs, sold in packs of half a dozen, Large size (size 7).', 5),
('Standard Cage-Free Eggs - Half Dozen', 3, 'Cage-free eggs, sold in packs of half a dozen, Standard size (size 6).', 5),
('Mixed Grade Cage-Free Eggs - Half Dozen', 3, 'Cage-free eggs, sold in packs of half a dozen, Mixed sizes.', 5),

('Jumbo Free-Range Eggs - Half Dozen', 3, 'Free-range eggs, sold in packs of half a dozen, Jumbo size (size 8).', 5),
('Large Free-Range Eggs - Half Dozen', 3, 'Free-range eggs, sold in packs of half a dozen, Large size (size 7).', 5),
('Standard Free-Range Eggs - Half Dozen', 3, 'Free-range eggs, sold in packs of half a dozen, Standard size (size 6).', 5),
('Mixed Grade Free-Range Eggs - Half Dozen', 3, 'Free-range eggs, sold in packs of half a dozen, Mixed sizes.', 5),

-- Dozen entries
('Jumbo Cage-Free Eggs', 4, 'Cage-free eggs, sold by the dozen, Jumbo size (size 8).', 5),
('Large Cage-Free Eggs', 4, 'Cage-free eggs, sold by the dozen, Large size (size 7).', 5),
('Standard Cage-Free Eggs', 4, 'Cage-free eggs, sold by the dozen, Standard size (size 6).', 5),
('Mixed Grade Cage-Free Eggs', 4, 'Cage-free eggs, sold by the dozen, Mixed sizes.', 5),

('Jumbo Free-Range Eggs', 4, 'Free-range eggs, sold by the dozen, Jumbo size (size 8).', 5),
('Large Free-Range Eggs', 4, 'Free-range eggs, sold by the dozen, Large size (size 7).', 5),
('Standard Free-Range Eggs', 4, 'Free-range eggs, sold by the dozen, Standard size (size 6).', 5),
('Mixed Grade Free-Range Eggs', 4, 'Free-range eggs, sold by the dozen, Mixed sizes.', 5),
-- Honey
('Manuka Honey', 3, 'Premium Manuka honey with unique antibacterial properties (Net weight: 500g).', 6),
('Clover Honey', 3, 'Light and sweet clover honey, perfect for teas and baking (Net weight: 500g)', 6),
('Wildflower Honey', 3, 'Rich and aromatic wildflower honey, great for all-purpose use (Net weight: 500g)', 6),
('Kamahi Honey', 3, 'Distinctive Kamahi honey, sourced from New Zealand’s native Kamahi trees (Net weight: 500g)', 6),
('Beechwood Honeydew', 3, 'Dark and rich Beechwood Honeydew honey, with a unique malty flavor (Net weight: 500g)', 6);
    
    
-- Christchurch Depot 
INSERT INTO product (orig_price, stock_quantity, depot_id, product_type_id, promotion_type_id) VALUES
(3.99, 150, 1, 1, 1),   -- Apple without promotion
(2.70, 180, 1, 6, 1),   -- Pear without promotion
(6.80, 100, 1, 7, 3),   -- Mango with Summer Sale
(3.10, 120, 1, 11, 1),  -- Potato without promotion
(4.99, 130, 1, 31, 1),  -- Mixed Salad without promotion
(9.99, 200, 1, 41, 1),  -- Cage-Free Eggs without promotion
(24.99, 150, 1, 43, 2), -- Manuka Honey with Seasonal Special
(5.99, 160, 1, 12, 3),  -- Carrot with Summer Sale
(2.50, 140, 1, 13, 1),  -- Tomato without promotion
(2.55, 150, 1, 15, 1),  -- Pepper without promotion
(1.50, 80, 1, 21, 1),   -- Basil without promotion
(2.75, 90, 1, 23, 1),   -- Parsley without promotion
(5.45, 90, 1, 25, 2),   -- Thyme with Seasonal Special
(4.25, 100, 1, 35, 3),  -- Arugula Salad with Summer Sale
(7.45, 85, 1, 8, 1),    -- Grapes without promotion
(6.20, 95, 1, 10, 1),   -- Strawberry without promotion
(8.50, 90, 1, 14, 1),   -- Cucumber without promotion
(7.75, 110, 1, 20, 2),  -- Lettuce with Seasonal Special
(7.99, 150, 1, 17, 1),  -- Onion without promotion
(3.75, 120, 1, 16, 3), -- Mushroom with Summer Sale
(9.99, 200, 1, 41, 1),  -- Cage-Free Eggs without promotion
(24.99, 150, 1, 43, 2), -- Manuka Honey with Seasonal Special
-- Invercargill Depot 
(2.50, 200, 2, 2, 2),   -- Banana with Seasonal Special
(1.95, 140, 2, 12, 2),  -- Carrot with Seasonal Special
(1.75, 70, 2, 22, 2),   -- Mint with Seasonal Special
(3.89, 140, 2, 32, 2),  -- Caesar Salad with Seasonal Special
(15.49, 160, 2, 44, 1), -- Clover Honey without promotion
(3.60, 170, 2, 8, 1),   -- Grapes without promotion
(7.20, 85, 2, 9, 1),    -- Cherry without promotion
(3.45, 90, 2, 1, 1),    -- Apple without promotion
(4.75, 100, 2, 7, 1),   -- Mango without promotion
(5.55, 95, 2, 4, 3),    -- Kiwi with Summer Sale
(6.50, 110, 2, 34, 1),  -- Caprese without promotion
(8.25, 120, 2, 33, 1),  -- Greek Salad without promotion
(7.99, 85, 2, 5, 1),    -- Blueberry without promotion
(6.85, 95, 2, 3, 1),    -- Orange without promotion
(5.20, 150, 2, 11, 1),  -- Potato without promotion
(6.75, 180, 2, 13, 1),  -- Tomato without promotion
(1.80, 160, 2, 23, 1),  -- Parsley without promotion
(2.00, 170, 2, 24, 1),  -- Rosemary without promotion
(4.55, 145, 2, 31, 1),  -- Mixed Salad without promotion
(8.95, 150, 2, 41, 1),  -- Cage-Free Eggs without promotion
(19.99, 120, 2, 45, 3), -- Wildflower Honey with Summer Sale    
(8.95, 150, 2, 41, 1),  -- Cage-Free Eggs without promotion
(15.49, 160, 2, 44, 1),  -- Clover Honey without promotion
-- Wellington Depot
(4.20, 180, 3, 3, 1),  -- Orange without promotion
(2.50, 150, 3, 13, 1), -- Tomato without promotion
(1.20, 85, 3, 23, 1),  -- Parsley without promotion
(5.99, 120, 3, 33, 1), -- Greek Salad without promotion
(18.99, 155, 3, 45, 3),-- Wildflower Honey with Summer Sale
(2.95, 160, 3, 10, 1), -- Strawberry without promotion
(4.40, 90, 3, 14, 3),  -- Cucumber with Summer Sale
(3.75, 130, 3, 2, 1),  -- Banana without promotion
(6.95, 95, 3, 1, 2),   -- Apple with Seasonal Special
(5.55, 110, 3, 15, 1), -- Pepper without promotion
(4.45, 100, 3, 25, 1), -- Thyme without promotion
(7.99, 140, 3, 31, 1), -- Mixed Salad without promotion
(9.50, 180, 3, 41, 1), -- Cage-Free Eggs without promotion
(3.95, 120, 3, 44, 1), -- Clover Honey without promotion
(6.50, 85, 3, 5, 1),   -- Blueberry without promotion
(7.25, 110, 3, 8, 1),  -- Grapes without promotion
(3.30, 150, 3, 11, 1), -- Potato without promotion
(2.55, 160, 3, 22, 1), -- Mint without promotion
(1.95, 140, 3, 24, 1), -- Rosemary without promotion
(8.15, 105, 3, 32, 2), -- Caesar Salad with Seasonal Special
(9.50, 180, 3, 41, 1),  -- Cage-Free Eggs without promotion
(18.99, 155, 3, 45, 3),  -- Wildflower Honey with Summer Sale
-- Hamilton Depot
(5.55, 165, 4, 4, 3),  -- Kiwi with Summer Sale
(2.30, 160, 4, 14, 1), -- Cucumber without promotion
(2.00, 90, 4, 24, 1),  -- Rosemary without promotion
(6.50, 110, 4, 34, 1), -- Caprese without promotion
(7.75, 95, 4, 20, 2),  -- Lettuce with Seasonal Special
(8.50, 180, 4, 19, 1), -- Broccoli without promotion
(5.25, 110, 4, 15, 3), -- Pepper with Summer Sale
(3.40, 170, 4, 1, 1),  -- Apple without promotion
(4.75, 150, 4, 6, 1),  -- Pear without promotion
(2.65, 120, 4, 13, 1), -- Tomato without promotion
(1.90, 80, 4, 21, 1),  -- Basil without promotion
(4.20, 140, 4, 31, 1), -- Mixed Salad without promotion
(7.90, 200, 4, 41, 1), -- Cage-Free Eggs without promotion
(24.95, 90, 4, 43, 3), -- Manuka Honey with Summer Sale
(6.15, 95, 4, 8, 1),   -- Grapes without promotion
(7.35, 150, 4, 2, 2),  -- Banana with Seasonal Special
(2.99, 165, 4, 12, 1), -- Carrot without promotion
(1.85, 75, 4, 23, 1),  -- Parsley without promotion
(6.99, 110, 4, 5, 1),  -- Blueberry without promotion
(8.25, 105, 4, 25, 3), -- Thyme with Summer Sale
(7.45, 120, 4, 3, 1),  -- Orange without promotion
(3.55, 100, 4, 11, 1), -- Potato without promotion
(7.90, 200, 4, 41, 1),  -- Cage-Free Eggs without promotion
(24.95, 90, 4, 43, 3),  -- Manuka Honey with Summer Sale
-- Auckland Depot
(5.55, 165, 5, 4, 3),  -- Kiwi with Summer Sale
(2.30, 160, 5, 14, 1), -- Cucumber without promotion
(2.00, 90, 5, 24, 1),  -- Rosemary without promotion
(6.50, 110, 5, 34, 1), -- Caprese without promotion
(7.75, 95, 5, 20, 2),  -- Lettuce with Seasonal Special
(8.50, 180, 5, 19, 1), -- Broccoli without promotion
(5.25, 110, 5, 15, 3), -- Pepper with Summer Sale
(3.40, 170, 5, 1, 1),  -- Apple without promotion
(4.75, 150, 5, 6, 1),  -- Pear without promotion
(2.65, 120, 5, 13, 1), -- Tomato without promotion
(1.90, 80, 5, 21, 1),  -- Basil without promotion
(4.20, 140, 5, 31, 1), -- Mixed Salad without promotion
(7.90, 200, 5, 41, 1), -- Cage-Free Eggs without promotion
(24.95, 90, 5, 43, 3), -- Manuka Honey with Summer Sale
(6.15, 95, 5, 8, 1),   -- Grapes without promotion
(7.35, 150, 5, 2, 2),  -- Banana with Seasonal Special
(2.99, 165, 5, 12, 1), -- Carrot without promotion
(1.85, 75, 5, 23, 1),  -- Parsley without promotion
(6.99, 110, 5, 5, 1),  -- Blueberry without promotion
(8.25, 105, 5, 25, 3), -- Thyme with Summer Sale
(7.45, 120, 5, 3, 1),  -- Orange without promotion
(3.55, 100, 5, 11, 1), -- Potato without promotion    
(7.90, 200, 5, 41, 1),  -- Cage-Free Eggs without promotion
(24.95, 90, 5, 43, 3);  -- Manuka Honey with Summer Sale
    
    
INSERT INTO box_subscription (frequency) VALUES
('Weekly'),
('Fortnightly'),
('Monthly');     


INSERT INTO box_size (size_name, max_num, price, description) VALUES
('small', 5, 19.99, 'Small box containing up to 5 kg, suitable for individuals or small families'),
('medium', 10, 39.99, 'Medium box containing up to 10 kg, suitable for medium-sized families or groups'),
('large', 15, 59.99, 'Large box containing up to 15 kg, suitable for large families or gatherings');


INSERT INTO box (box_name, box_description, box_size_id, is_active) VALUES
-- Vegetable Boxes
('Veggie Delight Box - Small', 'A small box containing up to 5 kg of fresh vegetables, tailored for individuals or small families.', 1, TRUE),
('Veggie Delight Box - Medium', 'A medium box containing up to 10 kg of a variety of fresh vegetables, perfect for medium-sized families.', 2, TRUE),
('Veggie Delight Box - Large', 'A large box containing up to 15 kg of assorted fresh vegetables, ideal for large families or gatherings.', 3, TRUE),
-- Fruit Boxes
('Fruit Blast Box - Small', 'A small box containing up to 5 kg of seasonal fruits, curated to provide a delightful mix.', 1, TRUE),
('Fruit Blast Box - Medium', 'A medium box containing up to 10 kg of the finest seasonal fruits, ensuring variety and taste.', 2, TRUE),
('Fruit Blast Box - Large', 'A large box containing up to 15 kg of premium, seasonal fruits, great for fruit lovers and large gatherings.', 3, TRUE),    
-- Mixed Fruit and Veggie Boxes   
('Mixed Harvest Box - Small', 'A small box maxed out with up to 5 kg of a balanced mix of fruits and vegetables, ideal for individuals or small families.', 1, TRUE),
('Mixed Harvest Box - Medium', 'A medium box maxed out with up to 10 kg of a generous assortment of fruits and vegetables, perfect for medium-sized families.', 2, TRUE),
('Mixed Harvest Box - Large', 'A large box filled to the brim with up to 15 kg of a diverse range of fruits and vegetables, great for large families or gatherings.', 3, TRUE);  
    
 INSERT INTO box_content (box_id, product_id, quantity) VALUES
-- Veggie Delight Box - Small
(1, 11, 2),  -- Potato x2
(1, 12, 1),  -- Carrot x1
(1, 13, 1),  -- Tomato x1
(1, 14, 1),  -- Cucumber x1
(1, 15, 1),  -- Pepper x1
-- Veggie Delight Box - Medium
(2, 11, 4),  -- Potato x4
(2, 12, 3),  -- Carrot x3
(2, 13, 2),  -- Tomato x2
(2, 14, 2),  -- Cucumber x2
(2, 15, 2),  -- Pepper x2
-- Veggie Delight Box - Large
(3, 11, 6),  -- Potato x6
(3, 12, 4),  -- Carrot x4
(3, 13, 3),  -- Tomato x3
(3, 14, 3),  -- Cucumber x3
(3, 15, 3),  -- Pepper x3
-- Fruit Blast Box - Small
(4, 6, 1),   -- Strawberry x1
(4, 7, 2),   -- Pear x2
(4, 8, 1),   -- Mango x1
(4, 9, 2),   -- Grapes x2
(4, 10, 1),  -- Blueberry x1
-- Fruit Blast Box - Medium
(5, 6, 2),   -- Strawberry x2
(5, 7, 3),   -- Pear x3
(5, 8, 2),   -- Mango x2
(5, 9, 3),   -- Grapes x3
(5, 10, 2),  -- Blueberry x2
-- Fruit Blast Box - Large
(6, 6, 3),   -- Strawberry x3
(6, 7, 4),   -- Pear x4
(6, 8, 3),   -- Mango x3
(6, 9, 4),   -- Grapes x4
(6, 10, 3),  -- Blueberry x3   
 -- Mixed Harvest Box - Small   
(7, 1, 2),   -- Apple x2
(7, 2, 1),   -- Banana x1
(7, 6, 1),   -- Strawberry x1
(7, 11, 1),  -- Potato x1
(7, 12, 1),  -- Carrot x1    
-- Mixed Harvest Box - Medium
(8, 1, 3),   -- Apple x3
(8, 2, 2),   -- Banana x2
(8, 6, 2),   -- Strawberry x2
(8, 11, 2),  -- Potato x2
(8, 12, 2),  -- Carrot x2
-- Mixed Harvest Box - Large
(9, 1, 4),   -- Apple x4
(9, 2, 3),   -- Banana x3
(9, 6, 3),   -- Strawberry x3
(9, 11, 3),  -- Potato x3
(9, 12, 3);  -- Carrot x3    
    
    
INSERT INTO order_status (status_name, description) VALUES
('Confirmed', 'The order has been confirmed by the customer.'),
('Processing', 'The order is being processed and packed.'),
('Shipped', 'The order has been shipped and is on its way to the customer.'),
('Delivered', 'The order has been delivered to the customer.'),
('On Hold', 'The order is on hold.'),
('Cancelled', 'The order has been cancelled.');    
    
    
INSERT INTO shipping_option (shipping_option_name, price, is_active) VALUES
('Standard', 6.00, TRUE),  -- Standard shipping typically takes longer but costs less
('Express', 15.00, TRUE),  -- Express shipping is faster and costs more
('Free Shipping', 0.00, TRUE);  -- An option for promotional or threshold-based free shipping    
    
    
INSERT INTO payment_method (method_description) VALUES
('Credit Card'),  -- Widely accepted, includes Visa, MasterCard, American Express, etc.
('Gift Card'),    -- Prepaid card issued by the business.
('Voucher from Points');  -- Payment made using loyalty points earned in customer reward programs.
    
 
INSERT INTO gst_rate (percentage, description) VALUES
(15.00, 'NZ GST 15%');  -- Standard GST rate in New Zealand
    

INSERT INTO gift_card_option (price, is_active) VALUES
(20.00, TRUE),  -- $20 gift card
(50.00, TRUE),  -- $50 gift card
(100.00, TRUE),  -- $100 gift card
(150.00, TRUE),  -- $150 gift card
(200.00, TRUE);  -- $200 gift card    
    
    
    
    
    
    
    