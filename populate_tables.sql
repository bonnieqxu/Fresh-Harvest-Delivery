USE fhd;


INSERT INTO user_role (role_name) VALUES 
('Customer'),
('Credit Account Holder'),
('Staff'), 
('Local Manager'),
('National Manager');


INSERT INTO depot (depot_name, address) VALUES 
('Christchurch', '101 Christchurch Road, Christchurch'), 
('Invercargill', '202 Invercargill Street, Invercargill'), 
('Wellington', '303 Wellington Boulevard, Wellington'), 
('Hamilton', '404 Hamilton Avenue, Hamilton'), 
('Auckland', '505 Auckland Lane, Auckland');


INSERT INTO user (email, password, role_id, is_active, depot_id) VALUES 
('james.holden@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 3, TRUE, 1),  -- Christchurch staff
('naomi.nagata@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 4, TRUE, 1),  -- Christchurch manager
('amos.burton@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 3, TRUE, 2),    -- Invercargill staff
('chrisjen.avasarala@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 4, TRUE, 2),  -- Invercargill manager
('alex.kamal@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 3, TRUE, 3),      -- Wellington staff
('bobbie.draper@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 4, TRUE, 3),  -- Wellington manager
('fred.johnson@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 3, TRUE, 4),  -- Hamilton staff
('julie.yao@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 4, TRUE, 4),        -- Hamilton manager
('joe.miller@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 3, TRUE, 5),      -- Auckland staff
('clarissa.mao@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 4, TRUE, 5),  -- Auckland manager
('michael.ang@freshharvest.co.nz', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 5, TRUE, 5),  -- National manager 
('alice.johnson@gmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 1),  -- Customer 1 at Christchurch
('bob.smith@hotmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 1),        -- Customer 2 at Christchurch
('carol.taylor@gmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 2),    -- Customer 1 at Invercargill
('david.brown@hotmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 2),    -- Customer 2 at Invercargill
('eve.white@gmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 3),          -- Customer 1 at Wellington
('frank.jones@hotmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 3),    -- Customer 2 at Wellington
('grace.lee@gmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 4),          -- Customer 1 at Hamilton
('henry.wilson@hotmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 4),  -- Customer 2 at Hamilton
('ivy.morris@gmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 5),        -- Customer 1 at Auckland
('jack.clark@hotmail.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 1, TRUE, 5),     -- Customer 2 at Auckland
('samantha.carter@fruitexpress.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 1),  -- Christchurch account holder 1
('daniel.jackson@newworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 1),  -- Christchurch account holder 2
('jack.oneill@fruitexpress.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 2),        -- Invercargill account holder 1
('teal.c@freshworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 2),                  -- Invercargill account holder 2
('vala.maldoran@freshworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 3),     -- Wellington account holder 1
('jonas.quinn@freshworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 3),        -- Wellington account holder 2
('george.hammond@freshworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 4),    -- Hamilton account holder 1
('janet.fraiser@newworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 4),    -- Hamilton account holder 2
('cameron.mitchell@fruitexpress.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 5),-- Auckland account holder 1
('carolyn.lam@newworld.com', 'bdc67b03774fe2b0dc601c1747c29a32f4dbfed57ef12d0ae48af127b94ea398', 2, TRUE, 5);        -- Auckland account holder 2


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
(21, 'Jack', 'Clark', '777 Peach Rd, Auckland', '021443212', DATE('1990-02-15')),               -- Customer 2 at Auckland
(22, 'Samantha', 'Carter', '123 Main St, Christchurch', '0212233445', DATE('1977-11-28')),       -- Christchurch account holder 1
(23, 'Daniel', 'Jackson', '123 Money St, Christchurch', '0213344556', DATE('1982-06-17')),          -- Christchurch account holder 2
(24, 'Jack', 'Oneill', '101 Pine St, Invercargill', '0214455667', DATE('1989-03-22')),                -- Invercargill account holder 1
(25, 'Teal', 'C', '101 Pinetree St, Invercargill', '0215566778', DATE('1992-09-05')),                            -- Invercargill account holder 2
(26, 'Vala', 'Mal Doran', '222 Kevin St, Wellington', '0216677889', DATE('1976-07-14')),              -- Wellington account holder 1
(27, 'Jonas', 'Quinn', '222 Apple St, Wellington', '0217788990', DATE('1981-01-30')),                     -- Wellington account holder 2
(28, 'George', 'Hammond', '444 Cherry St, Hamilton', '0218899001', DATE('1988-05-09')),           -- Hamilton account holder 1
(29, 'Janet', 'Fraiser', '444 King St, Hamilton', '0219900112', DATE('1980-10-24')),                -- Hamilton account holder 2
(30, 'Cameron', 'Mitchell', '666 Grape St, Auckland', '0210011223', DATE('1979-04-01')),        -- Auckland account holder 1
(31, 'Carolyn', 'Lam', '666 Panell St, Auckland', '0211122334', DATE('1985-12-12'));                        -- Auckland account holder

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
INSERT INTO account_holder (business_name, business_address, business_phone, user_id, credit_account_id, isApproved) VALUES 
('Fruit Express', '123 Cashel St, Christchurch', '0212233445', 22, 1, TRUE),       -- Christchurch account holder 1
('New World', '456 Colombo St, Christchurch', '036562233', 23, 2, TRUE),          -- Christchurch account holder 2
('Fruit Express', '789 Dee St, Invercargill', '0274455667', 24, 3, TRUE),                -- Invercargill account holder 1
('Fresh World', '101 Esk St, Invercargill', '0275566778', 25, 4, TRUE),                            -- Invercargill account holder 2
('Fresh World', '222 Lambton Quay, Wellington', '042255636', 26, 5, TRUE),            -- Wellington account holder 1
('Fresh World', '333 Cuba St, Wellington', '0217788990', 27, 6, TRUE),                   -- Wellington account holder 2
('Fresh World', '444 Victoria St, Hamilton', '072255464', 28, 7, TRUE),          -- Hamilton account holder 1
('New World', '555 Hood St, Hamilton', '0219900112', 29, 8, TRUE),              -- Hamilton account holder 2
('Fruit Express', '666 Queen St, Auckland', '093032266', 30, 9, TRUE),       -- Auckland account holder 1
('New World', '777 Ponsonby Rd, Auckland', '096365566', 31, 10, TRUE);                          -- Auckland account holder 2
    
    
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
(15, 'kg'),    -- Large box
(NULL, 'Head'),
(NULL, 'Each'),
(NULL, 'Bag'),
(NULL, 'Dozen'),
(NULL, 'Half Dozen'),
(NULL, 'Punnet'),
(NULL, 'Tray'),
(500, 'Grams');

    
    
INSERT INTO product_category (category_name) VALUES
('Fruits'),
('Vegetables'),
('Herbs'),
('Salads'),
('Eggs'),
('Honey'),
('Premade Box');
    
-- Populate product type 
-- Fruits
INSERT INTO product_type (product_type_name, product_weight_id, description, category_id) VALUES
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
('Fruit Salad', 3, 'Mixed fruit salad, sold in 500 g containers.', 4);

INSERT INTO product_type (product_type_name, product_weight_id, description, category_id) VALUES
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
    
    

-- Christchurch Depot (depot_id = 1)
INSERT INTO product (orig_price, stock_quantity, depot_id, product_type_id, promotion_type_id, is_active) VALUES
(2.55, 150, 1, 1, NULL, TRUE),   -- Apple
(3.10, 80, 1, 2, NULL, TRUE),    -- Banana
(2.99, 90, 1, 3, NULL, TRUE),    -- Orange
(2.65, 90, 1, 4, NULL, TRUE),    -- Kiwi
(2.30, 100, 1, 5, NULL, TRUE),   -- Blueberry
(5.25, 85, 1, 6, NULL, TRUE),    -- Strawberry
(3.75, 95, 1, 7, NULL, TRUE),    -- Pear
(7.99, 90, 1, 8, NULL, TRUE),    -- Mango
(7.75, 110, 1, 9, NULL, TRUE),   -- Grapes
(8.50, 150, 1, 10, NULL, TRUE),   -- Cherry
(1.50, 120, 1, 11, NULL, TRUE),   -- Potato
(1.90, 140, 1, 12, NULL, TRUE),   -- Carrot
(2.55, 85, 1, 13, NULL, TRUE),    -- Tomato
(1.85, 90, 1, 14, NULL, TRUE),    -- Cucumber
(2.00, 100, 1, 15, NULL, TRUE),   -- Pepper
(8.25, 95, 1, 16, NULL,TRUE),    -- Broccoli
(6.50, 110, 1, 17, NULL,TRUE),   -- Lettuce
(7.90, 180, 1, 18, NULL, TRUE),   -- Mushroom
(24.95, 150, 1, 19, NULL, TRUE),  -- Spinach
(18.99, 160, 1, 20, NULL, TRUE),  -- Onion
(19.99, 120, 1, 21, NULL, TRUE),  -- Basil
(6.50, 85, 1, 22, NULL, TRUE),    -- Mint
(8.15, 150, 1, 23, NULL, TRUE),   -- Parsley
(8.25, 120, 1, 24, NULL, TRUE),   -- Rosemary
(6.50, 110, 1, 25, NULL, TRUE),   -- Thyme
(7.90, 200, 1, 26, NULL, TRUE),   -- Oregano
(24.95, 120, 1, 27, NULL, TRUE),  -- Cilantro
(18.99, 160, 1, 28, NULL, TRUE),  -- Sage
(19.99, 120, 1, 29, NULL, TRUE),  -- Dill
(6.50, 85, 1, 30, NULL, TRUE),    -- Chives
(8.15, 150, 1, 31, NULL, TRUE),   -- Mixed Salad
(8.25, 120, 1, 32, NULL, TRUE),   -- Caesar Salad
(6.50, 110, 1, 33, NULL, TRUE),   -- Greek Salad
(7.90, 200, 1, 34, NULL, TRUE),   -- Caprese
(24.95, 120, 1, 35, NULL, TRUE),  -- Arugula Salad
(18.99, 160, 1, 36, NULL, TRUE),  -- Kale Salad
(19.99, 120, 1, 37, NULL, TRUE),  -- Spinach Salad
(6.50, 85, 1, 38, NULL, TRUE),    -- Cobb Salad
(8.15, 150, 1, 39, NULL, TRUE),   -- Asian Salad
(8.25, 120, 1, 40, NULL, TRUE),   -- Fruit Salad
(12.99, 200, 1, 41, NULL, TRUE),  -- Jumbo Cage-Free Eggs - Half Dozen
(10.99, 180, 1, 42, NULL, TRUE),  -- Large Cage-Free Eggs - Half Dozen
(8.99, 150, 1, 43, NULL, TRUE),   -- Standard Cage-Free Eggs - Half Dozen
(9.99, 160, 1, 44, NULL, TRUE),   -- Mixed Grade Cage-Free Eggs - Half Dozen
(13.99, 150, 1, 45, NULL, TRUE),  -- Jumbo Cage-Free Eggs
(11.99, 140, 1, 46, NULL, TRUE),  -- Large Cage-Free Eggs
(9.49, 130, 1, 47, NULL, TRUE),   -- Standard Cage-Free Eggs
(10.49, 120, 1, 48, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs
(30.99, 110, 1, 49, NULL, TRUE),  -- Manuka Honey
(15.99, 100, 1, 50, NULL, TRUE),  -- Clover Honey
(17.99, 90, 1, 51, NULL, TRUE),   -- Wildflower Honey
(18.99, 85, 1, 52, NULL, TRUE),   -- Kamahi Honey
(16.99, 80, 1, 53, NULL, TRUE),   -- Beechwood Honeydew


-- Invercargill Depot (depot_id = 2)
(2.95, 160, 2, 1, NULL, TRUE),   -- Apple
(3.45, 200, 2, 2, NULL, TRUE),   -- Banana
(1.95, 140, 2, 3, NULL, TRUE),   -- Orange
(6.75, 170, 2, 4, NULL, TRUE),   -- Kiwi
(3.60, 170, 2, 5, NULL, TRUE),   -- Blueberry
(5.55, 95, 2, 6, NULL, TRUE),    -- Strawberry
(3.89, 140, 2, 7, NULL, TRUE),   -- Pear
(7.99, 160, 2, 8, NULL, TRUE),   -- Mango
(7.20, 85, 2, 9, NULL, TRUE),    -- Grapes
(8.50, 120, 2, 10, NULL, TRUE),   -- Cherry
(1.80, 160, 2, 11, NULL, TRUE),   -- Potato
(1.75, 160, 2, 12, NULL, TRUE),   -- Carrot
(2.00, 170, 2, 13, NULL, TRUE),   -- Tomato
(1.85, 90, 2, 14, NULL, TRUE),    -- Cucumber
(4.55, 145, 2, 15, NULL, TRUE),   -- Pepper
(8.95, 150, 2, 16, NULL, TRUE),   -- Broccoli
(6.50, 110, 2, 17, NULL, TRUE),   -- Lettuce
(7.90, 200, 2, 18, NULL, TRUE),   -- Mushroom
(24.95, 120, 2, 19, NULL, TRUE),  -- Spinach
(18.99, 160, 2, 20, NULL, TRUE),  -- Onion
(19.99, 160, 2, 21, NULL, TRUE),  -- Basil
(6.50, 110, 2, 22, NULL, TRUE),   -- Mint
(8.15, 105, 2, 23, NULL, TRUE),   -- Parsley
(8.25, 120, 2, 24, NULL, TRUE),   -- Rosemary
(6.50, 110, 2, 25, NULL, TRUE),   -- Thyme
(7.90, 200, 2, 26, NULL, TRUE),   -- Oregano
(24.95, 120, 2, 27, NULL, TRUE),  -- Cilantro
(18.99, 160, 2, 28, NULL, TRUE),  -- Sage
(19.99, 160, 2, 29, NULL, TRUE),  -- Dill
(6.50, 85, 2, 30, NULL, TRUE),    -- Chives
(8.15, 150, 2, 31, NULL, TRUE),   -- Mixed Salad
(8.25, 120, 2, 32, NULL, TRUE),   -- Caesar Salad
(6.50, 110, 2, 33, NULL, TRUE),   -- Greek Salad
(7.90, 200, 2, 34, NULL, TRUE),   -- Caprese
(24.95, 120, 2, 35, NULL, TRUE),  -- Arugula Salad
(18.99, 160, 2, 36, NULL, TRUE),  -- Kale Salad
(19.99, 120, 2, 37, NULL, TRUE),  -- Spinach Salad
(6.50, 85, 2, 38, NULL, TRUE),    -- Cobb Salad
(8.15, 150, 2, 39, NULL, TRUE),   -- Asian Salad
(8.25, 120, 2, 40, NULL, TRUE),   -- Fruit Salad
(13.49, 190, 2, 41, NULL, TRUE),  -- Jumbo Cage-Free Eggs - Half Dozen
(11.49, 175, 2, 42, NULL, TRUE),  -- Large Cage-Free Eggs - Half Dozen
(9.49, 160, 2, 43, NULL, TRUE),   -- Standard Cage-Free Eggs - Half Dozen
(10.49, 170, 2, 44, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs - Half Dozen
(14.49, 160, 2, 45, NULL, TRUE),  -- Jumbo Cage-Free Eggs
(12.49, 150, 2, 46, NULL, TRUE),  -- Large Cage-Free Eggs
(10.49, 140, 2, 47, NULL, TRUE),  -- Standard Cage-Free Eggs
(11.49, 135, 2, 48, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs
(31.99, 115, 2, 49, NULL, TRUE),  -- Manuka Honey
(16.99, 105, 2, 50, NULL, TRUE),  -- Clover Honey
(18.49, 95, 2, 51, NULL, TRUE),   -- Wildflower Honey
(19.49, 90, 2, 52, NULL, TRUE),   -- Kamahi Honey
(17.49, 85, 2, 53, NULL, TRUE),   -- Beechwood Honeydew



-- Wellington Depot (depot_id = 3)
(2.95, 160, 3, 1, NULL, TRUE),   -- Apple
(3.30, 85, 3, 2, NULL, TRUE),    -- Banana
(5.55, 140, 3, 3, NULL, TRUE),   -- Orange
(2.50, 150, 3, 4, NULL, TRUE),   -- Kiwi
(4.40, 90, 3, 5, NULL, TRUE),    -- Blueberry
(5.55, 110, 3, 6, NULL, TRUE),   -- Strawberry
(3.75, 120, 3, 7, NULL, TRUE),   -- Pear
(7.99, 85, 3, 8, NULL, TRUE),    -- Mango
(7.25, 110, 3, 9, NULL, TRUE),   -- Grapes
(7.75, 110, 3, 10, NULL, TRUE),   -- Cherry
(1.20, 85, 3, 11, NULL, TRUE),    -- Potato
(1.95, 140, 3, 12, NULL, TRUE),   -- Carrot
(2.55, 160, 3, 13, NULL, TRUE),   -- Tomato
(1.95, 140, 3, 14, NULL, TRUE),   -- Cucumber
(4.45, 100, 3, 15, NULL, TRUE),   -- Pepper
(7.99, 140, 3, 16, NULL, TRUE),   -- Broccoli
(6.50, 120, 3, 17, NULL, TRUE),   -- Lettuce
(7.90, 180, 3, 18, NULL, TRUE),   -- Mushroom
(24.95, 155, 3, 19, NULL, TRUE),  -- Spinach
(18.99, 155, 3, 20, NULL, TRUE),  -- Onion
(19.99, 120, 3, 21, NULL, TRUE),  -- Basil
(6.50, 85, 3, 22, NULL, TRUE),    -- Mint
(8.15, 105, 3, 23, NULL, TRUE),   -- Parsley
(8.25, 120, 3, 24, NULL, TRUE),   -- Rosemary
(6.50, 110, 3, 25, NULL, TRUE),   -- Thyme
(7.90, 200, 3, 26, NULL, TRUE),   -- Oregano
(24.95, 120, 3, 27, NULL, TRUE),  -- Cilantro
(18.99, 155, 3, 28, NULL, TRUE),  -- Sage
(19.99, 120, 3, 29, NULL, TRUE),  -- Dill
(6.50, 85, 3, 30, NULL, TRUE),    -- Chives
(8.15, 150, 3, 31, NULL, TRUE),   -- Mixed Salad
(8.25, 120, 3, 32, NULL, TRUE),   -- Caesar Salad
(6.50, 110, 3, 33, NULL, TRUE),   -- Greek Salad
(7.90, 180, 3, 34, NULL, TRUE),   -- Caprese
(24.95, 120, 3, 35, NULL, TRUE),  -- Arugula Salad
(18.99, 155, 3, 36, NULL, TRUE),  -- Kale Salad
(19.99, 120, 3, 37, NULL, TRUE),  -- Spinach Salad
(6.50, 85, 3, 38, NULL, TRUE),    -- Cobb Salad
(8.15, 150, 3, 39, NULL, TRUE),   -- Asian Salad
(8.25, 120, 3, 40, NULL, TRUE),   -- Fruit Salad
(13.99, 180, 3, 41, NULL, TRUE),  -- Jumbo Cage-Free Eggs - Half Dozen
(11.99, 170, 3, 42, NULL, TRUE),  -- Large Cage-Free Eggs - Half Dozen
(9.99, 160, 3, 43, NULL, TRUE),   -- Standard Cage-Free Eggs - Half Dozen
(10.99, 165, 3, 44, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs - Half Dozen
(14.99, 160, 3, 45, NULL, TRUE),  -- Jumbo Cage-Free Eggs
(12.99, 155, 3, 46, NULL, TRUE),  -- Large Cage-Free Eggs
(10.99, 150, 3, 47, NULL, TRUE),  -- Standard Cage-Free Eggs
(11.99, 145, 3, 48, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs
(32.99, 120, 3, 49, NULL, TRUE),  -- Manuka Honey
(17.99, 110, 3, 50, NULL, TRUE),  -- Clover Honey
(19.99, 100, 3, 51, NULL, TRUE),  -- Wildflower Honey
(20.99, 95, 3, 52, NULL, TRUE),   -- Kamahi Honey
(18.99, 90, 3, 53, NULL, TRUE),   -- Beechwood Honeydew


-- Hamilton Depot (depot_id = 4)
(6.20, 95, 4, 1, NULL, TRUE),    -- Apple
(3.40, 170, 4, 2, NULL , TRUE),   -- Banana
(2.99, 165, 4, 3, NULL, TRUE),   -- Orange
(2.65, 120, 4, 4, NULL, TRUE),   -- Kiwi
(2.30, 160, 4, 5, NULL, TRUE),   -- Blueberry
(5.25, 110, 4, 6, NULL, TRUE),   -- Strawberry
(3.75, 95, 4, 7, NULL, TRUE),    -- Pear
(7.99, 95, 4, 8, NULL, TRUE),    -- Mango
(7.25, 110, 4, 9, NULL, TRUE),   -- Grapes
(7.75, 95, 4, 10, NULL, TRUE),    -- Cherry
(1.90, 80, 4, 11, NULL, TRUE),    -- Potato
(1.85, 75, 4, 12, NULL, TRUE),    -- Carrot
(7.45, 120, 4, 13, NULL, TRUE),   -- Tomato
(2.00, 90, 4, 14, NULL, TRUE),    -- Cucumber
(8.25, 105, 4, 15, NULL, TRUE),   -- Pepper
(4.20, 140, 4, 16, NULL, TRUE),   -- Broccoli
(6.50, 110, 4, 17, NULL, TRUE),   -- Lettuce
(7.90, 200, 4, 18, NULL, TRUE),   -- Mushroom
(24.95, 90, 4, 19, NULL, TRUE),   -- Spinach
(18.99, 150, 4, 20, NULL, TRUE),  -- Onion
(19.99, 90, 4, 21, NULL, TRUE),   -- Basil
(6.50, 85, 4, 22, NULL, TRUE),    -- Mint
(8.15, 105, 4, 23, NULL, TRUE),   -- Parsley
(8.25, 120, 4, 24, NULL, TRUE),   -- Rosemary
(6.50, 110, 4, 25, NULL, TRUE),   -- Thyme
(7.90, 200, 4, 26, NULL, TRUE),   -- Oregano
(24.95, 90, 4, 27, NULL, TRUE),   -- Cilantro
(18.99, 150, 4, 28, NULL, TRUE),  -- Sage
(19.99, 90, 4, 29, NULL, TRUE),   -- Dill
(6.50, 85, 4, 30, NULL, TRUE),    -- Chives
(8.15, 105, 4, 31, NULL, TRUE),   -- Mixed Salad
(8.25, 120, 4, 32, NULL, TRUE),   -- Caesar Salad
(6.50, 110, 4, 33, NULL, TRUE),   -- Greek Salad
(7.90, 200, 4, 34, NULL, TRUE),   -- Caprese
(24.95, 90, 4, 35, NULL, TRUE),   -- Arugula Salad
(18.99, 150, 4, 36, NULL, TRUE),  -- Kale Salad
(19.99, 90, 4, 37, NULL, TRUE),   -- Spinach Salad
(6.50, 85, 4, 38, NULL, TRUE),    -- Cobb Salad
(8.15, 105, 4, 39, NULL, TRUE),   -- Asian Salad
(8.25, 120, 4, 40, NULL, TRUE),   -- Fruit Salad
(14.49, 185, 4, 41, NULL, TRUE),  -- Jumbo Cage-Free Eggs - Half Dozen
(12.49, 175, 4, 42, NULL, TRUE),  -- Large Cage-Free Eggs - Half Dozen
(10.49, 165, 4, 43, NULL, TRUE),  -- Standard Cage-Free Eggs - Half Dozen
(11.49, 160, 4, 44, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs - Half Dozen
(15.49, 155, 4, 45, NULL, TRUE),  -- Jumbo Cage-Free Eggs
(13.49, 150, 4, 46, NULL, TRUE),  -- Large Cage-Free Eggs
(11.49, 145, 4, 47, NULL, TRUE),  -- Standard Cage-Free Eggs
(12.49, 140, 4, 48, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs
(33.99, 125, 4, 49, NULL, TRUE),  -- Manuka Honey
(18.99, 115, 4, 50, NULL, TRUE),  -- Clover Honey
(20.99, 105, 4, 51, NULL, TRUE),  -- Wildflower Honey
(21.99, 100, 4, 52, NULL, TRUE),  -- Kamahi Honey
(19.99, 95, 4, 53, NULL, TRUE),  -- Beechwood Honeydew



-- Auckland Depot (depot_id = 5)
(6.20, 95, 5, 1, NULL, TRUE),    -- Apple
(3.40, 170, 5, 2, NULL, TRUE),   -- Banana
(2.99, 165, 5, 3, NULL, TRUE),   -- Orange
(2.65, 120, 5, 4, NULL, TRUE),   -- Kiwi
(2.30, 160, 5, 5, NULL, TRUE),   -- Blueberry
(5.25, 110, 5, 6, NULL, TRUE),   -- Strawberry
(3.75, 95, 5, 7, NULL, TRUE),    -- Pear
(7.99, 95, 5, 8, NULL, TRUE),    -- Mango
(7.25, 110, 5, 9, NULL, TRUE),   -- Grapes
(7.75, 95, 5, 10, NULL, TRUE),   -- Cherry
(1.90, 80, 5, 11, NULL, TRUE),   -- Potato
(1.85, 75, 5, 12, NULL, TRUE),   -- Carrot
(7.45, 120, 5, 13, NULL, TRUE),   -- Tomato
(2.00, 90, 5, 14, NULL, TRUE),    -- Cucumber
(8.25, 105, 5, 15, NULL, TRUE),   -- Pepper
(4.20, 140, 5, 16, NULL, TRUE),   -- Broccoli
(6.50, 110, 5, 17, NULL, TRUE),   -- Lettuce
(7.90, 200, 5, 18, NULL, TRUE),   -- Mushroom
(24.95, 90, 5, 19, NULL, TRUE),   -- Spinach
(18.99, 150, 5, 20, NULL, TRUE),  -- Onion
(19.99, 90, 5, 21, NULL, TRUE),   -- Basil
(6.50, 85, 5, 22, NULL, TRUE),    -- Mint
(8.15, 105, 5, 23, NULL, TRUE),   -- Parsley
(8.25, 120, 5, 24, NULL, TRUE),   -- Rosemary
(6.50, 110, 5, 25, NULL, TRUE),   -- Thyme
(7.90, 200, 5, 26, NULL, TRUE),   -- Oregano
(24.95, 90, 5, 27, NULL, TRUE),   -- Cilantro
(18.99, 150, 5, 28, NULL, TRUE),  -- Sage
(19.99, 90, 5, 29, NULL, TRUE),   -- Dill
(6.50, 85, 5, 30, NULL, TRUE),    -- Chives
(8.15, 105, 5, 31, NULL, TRUE),   -- Mixed Salad
(8.25, 120, 5, 32, NULL, TRUE),   -- Caesar Salad
(6.50, 110, 5, 33, NULL, TRUE),   -- Greek Salad
(7.90, 200, 5, 34, NULL, TRUE),   -- Caprese
(24.95, 90, 5, 35, NULL, TRUE),   -- Arugula Salad
(18.99, 150, 5, 36, NULL, TRUE),  -- Kale Salad
(19.99, 90, 5, 37, NULL, TRUE),   -- Spinach Salad
(6.50, 85, 5, 38, NULL, TRUE),    -- Cobb Salad
(8.15, 105, 5, 39, NULL, TRUE),   -- Asian Salad
(8.25, 120, 5, 40, NULL, TRUE),   -- Fruit Salad
(14.99, 190, 5, 41, NULL, TRUE),  -- Jumbo Cage-Free Eggs - Half Dozen
(12.99, 180, 5, 42, NULL, TRUE),  -- Large Cage-Free Eggs - Half Dozen
(10.99, 170, 5, 43, NULL, TRUE),  -- Standard Cage-Free Eggs - Half Dozen
(11.99, 165, 5, 44, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs - Half Dozen
(15.99, 160, 5, 45, NULL, TRUE),  -- Jumbo Cage-Free Eggs
(13.99, 155, 5, 46, NULL, TRUE),  -- Large Cage-Free Eggs
(11.99, 150, 5, 47, NULL, TRUE),  -- Standard Cage-Free Eggs
(12.99, 145, 5, 48, NULL, TRUE),  -- Mixed Grade Cage-Free Eggs
(34.99, 130, 5, 49, NULL, TRUE),  -- Manuka Honey
(19.99, 120, 5, 50, NULL, TRUE),  -- Clover Honey
(21.99, 110, 5, 51, NULL, TRUE),  -- Wildflower Honey
(22.99, 105, 5, 52, NULL, TRUE),  -- Kamahi Honey
(20.99, 100, 5, 53, NULL, TRUE);  -- Beechwood Honeydew

    
    
INSERT INTO box_frequency  (frequency) VALUES
('Weekly'),
('Fortnightly'),
('Monthly');     


INSERT INTO box_size (size_name, price, description) VALUES
('Small', 19.99, 'Small box containing up to 5 kg, suitable for individuals or small families'),
('Medium', 39.99, 'Medium box containing up to 10 kg, suitable for medium-sized families or groups'),
('Large', 59.99, 'Large box containing up to 15 kg, suitable for large families or gatherings');


INSERT INTO box_category (category) VALUES
('Fruits'),
('Vegetables'),
('Mixed');

  
INSERT INTO order_status (status_name, description) VALUES
('Confirmed', 'The order has been confirmed by the customer.'),
('Processing', 'The order is being processed.'),
('Dispatched', 'The order has been shipped and is on its way to the customer.'),
('Received', 'Customer received the order.'),
('Cancelled', 'The order has been cancelled.'); 
    
    
INSERT INTO shipping_option (shipping_option_name, price, is_active) VALUES
('Standard', 6.00, TRUE),  -- Standard shipping typically takes longer but costs less
('Rural', 15.00, TRUE);  -- Rural shipping is for delivery further than 50kms from the depot  
    
    
INSERT INTO order_hdr (user_id, order_date, total_price, status_id, shipping_option_id, purpose) VALUES
(12, '2024-05-01', 59.99, 1, 1, 'order'), -- Customer 1 at Christchurch
(13, '2024-05-02', 115.80, 1, 1, 'order'), -- Customer 2 at Christchurch
(14, '2024-05-03', 39.99, 1, 2 , 'order'), -- Customer 1 at Invercargill
(15, '2024-05-04', 79.99, 1, 1, 'order'), -- Customer 2 at Invercargill
(16, '2024-05-05', 24.95, 1, 2, 'order'), -- Customer 1 at Wellington
(17, '2024-05-06', 47.90, 1, 2, 'order'), -- Customer 2 at Wellington
(18, '2024-05-07', 99.95, 1, 1, 'order'), -- Customer 1 at Hamilton
(19, '2024-05-08', 63.99, 1, 1, 'order'), -- Customer 2 at Hamilton
(20, '2024-05-09', 49.95, 1, 1, 'order'), -- Customer 1 at Auckland
(21, '2024-05-10', 35.90, 1, 2, 'order'); -- Customer 2 at Auckland


INSERT INTO order_detail (order_hdr_id, product_id, quantity, line_total_price) VALUES
-- Order 1
(1, 3, 1, 59.99), -- Veggie Delight Box - Large
-- Order 2
(2, 4, 2, 39.99), -- Fruit Blast Box - Small
(2, 14, 1, 35.90), -- Blueberry
(2, 16, 1, 39.99), -- Pear
-- Order 3
(3, 5, 1, 39.99), -- Fruit Blast Box - Medium
-- Order 4
(4, 6, 1, 59.99), -- Fruit Blast Box - Large
(4, 10, 2, 20.00), -- Blueberry
-- Order 5
(5, 28, 1, 24.95), -- Spinach
-- Order 6
(6, 5, 1, 39.99), -- Fruit Blast Box - Medium
(6, 16, 1, 7.90), -- Pear
-- Order 7
(7, 3, 1, 59.99), -- Veggie Delight Box - Large
(7, 14, 1, 39.99), -- Blueberry
-- Order 8
(8, 5, 1, 39.99), -- Fruit Blast Box - Medium
(8, 28, 1, 24.00), -- Spinach
-- Order 9
(9, 6, 1, 39.99), -- Fruit Blast Box - Large
(9, 10, 1, 10.00), -- Blueberry
-- Order 10
(10, 5, 1, 19.95), -- Fruit Blast Box - Medium
(10, 16, 1, 15.95); -- Pear



INSERT INTO depot_order (order_hdr_id, depot_id) VALUES
(1, 1), -- Christchurch
(2, 1), -- Christchurch
(3, 2), -- Invercargill
(4, 2), -- Invercargill
(5, 3), -- Wellington
(6, 3), -- Wellington
(7, 4), -- Hamilton
(8, 4), -- Hamilton
(9, 5), -- Auckland
(10, 5); -- Auckland
    
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
    
INSERT INTO message_status (message_status_id, status_name, description) VALUES
(1, 'New', 'Message is received'),
(2, 'Read', 'Message is read'),
(3, 'Sent', 'Message is sent'),
(4, 'Processed', 'Message is processed');

INSERT INTO message_category (message_category_id, message_category_name, description) VALUES
(1, 'Notification', 'Includes any sort of messages from Welcome message to order status notification'),
(2, 'General Enquiry', 'Enquiry to Staff'),
(3, 'Order Enquiry', 'Enquiry about a specific order to Staff'),
(4, 'Issues on Product delivered', 'Notify to Staff issues with product delivered');

    
    
    
    
    
    