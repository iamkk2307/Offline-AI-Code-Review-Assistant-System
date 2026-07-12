-- SQL Sample Query with smells

-- Style Smell: SELECT * query
SELECT * FROM users WHERE active = 1;

-- Security Smell: GRANT ALL privileges
GRANT ALL PRIVILEGES ON database_development.* TO 'root'@'localhost';

-- Performance Smell: NOT IN subquery
SELECT id, name FROM products 
WHERE category_id NOT IN (SELECT id FROM categories WHERE status = 'disabled');

-- Performance Smell: FUNCTION usage on indexed column in WHERE clause
SELECT order_id, order_date FROM orders 
WHERE UPPER(customer_name) = 'ALICE';
