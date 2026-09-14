# ==========================================
# QueryPilot - SQL Generator
# ==========================================


def generate_sql(question: str, intent: str) -> str:
    """
    Generate SQL from the detected intent and user question.

    This is the initial rule-based baseline.
    We will replace/augment this later with an AI
    Text-to-SQL model.
    """

    question = question.lower().strip()

    # ==========================================
    # COUNT
    # ==========================================

    if intent == "COUNT":

        if "customer" in question:
            return """
SELECT COUNT(*) AS customer_count
FROM customers;
""".strip()

        if "product" in question:
            return """
SELECT COUNT(*) AS product_count
FROM products;
""".strip()

        if "order" in question:
            return """
SELECT COUNT(*) AS order_count
FROM orders;
""".strip()

        if "review" in question:
            return """
SELECT COUNT(*) AS review_count
FROM product_reviews;
""".strip()


    # ==========================================
    # SUM
    # ==========================================

    if intent == "SUM":

        if "order" in question or "revenue" in question:
            return """
SELECT SUM(total_amount) AS total_revenue
FROM orders;
""".strip()

        if "customer" in question and "spending" in question:
            return """
SELECT SUM(total_amount) AS total_customer_spending
FROM orders;
""".strip()


    # ==========================================
    # AVERAGE
    # ==========================================

    if intent == "AVERAGE":

        if "rating" in question or "review" in question:
            return """
SELECT AVG(rating) AS average_rating
FROM product_reviews;
""".strip()

        if "order" in question or "order value" in question:
            return """
SELECT AVG(total_amount) AS average_order_value
FROM orders;
""".strip()

        if "price" in question or "product" in question:
            return """
SELECT AVG(price) AS average_product_price
FROM products;
""".strip()


    # ==========================================
    # MAXIMUM
    # ==========================================

    if intent == "MAXIMUM":

        if "rating" in question:
            return """
SELECT MAX(rating) AS highest_rating
FROM product_reviews;
""".strip()

        if "price" in question:
            return """
SELECT MAX(price) AS highest_price
FROM products;
""".strip()

        if "order" in question or "amount" in question:
            return """
SELECT MAX(total_amount) AS highest_order_value
FROM orders;
""".strip()


    # ==========================================
    # MINIMUM
    # ==========================================

    if intent == "MINIMUM":

        if "rating" in question:
            return """
SELECT MIN(rating) AS minimum_rating
FROM product_reviews;
""".strip()

        if "price" in question:
            return """
SELECT MIN(price) AS minimum_price
FROM products;
""".strip()

        if "order" in question or "amount" in question:
            return """
SELECT MIN(total_amount) AS minimum_order_value
FROM orders;
""".strip()


    # ==========================================
    # DISTINCT
    # ==========================================

    if intent == "DISTINCT":

        if "categor" in question:
            return """
SELECT DISTINCT category
FROM products;
""".strip()

        if "brand" in question:
            return """
SELECT DISTINCT brand
FROM products;
""".strip()

        if "city" in question:
            # Note: current schema has country, not city.
            return """
SELECT DISTINCT country
FROM customers;
""".strip()


    # ==========================================
    # FILTER
    # ==========================================

    if intent == "FILTER":

        if "product" in question:

            if "below" in question or "under" in question:
                return """
SELECT *
FROM products
WHERE price < 500;
""".strip()

            if "above" in question or "over" in question:
                return """
SELECT *
FROM products
WHERE price > 1000;
""".strip()

            if "rating" in question:
                return """
SELECT *
FROM products p
WHERE EXISTS (
    SELECT 1
    FROM product_reviews r
    WHERE r.product_id = p.product_id
    AND r.rating > 4
);
""".strip()

        if "customer" in question:

            if "delhi" in question:
                return """
SELECT *
FROM customers
WHERE country = 'Delhi';
""".strip()

            if "mumbai" in question:
                return """
SELECT *
FROM customers
WHERE country = 'Mumbai';
""".strip()

        if "order" in question:

            if "above" in question or "over" in question:
                return """
SELECT *
FROM orders
WHERE total_amount > 1000;
""".strip()

            if "below" in question or "under" in question:
                return """
SELECT *
FROM orders
WHERE total_amount < 500;
""".strip()


    # ==========================================
    # SORT
    # ==========================================

    if intent == "SORT":

        if "product" in question:

            if "rating" in question:
                return """
SELECT *
FROM products
ORDER BY price DESC;
""".strip()

            return """
SELECT *
FROM products
ORDER BY price ASC;
""".strip()

        if "order" in question:
            return """
SELECT *
FROM orders
ORDER BY total_amount DESC;
""".strip()

        if "customer" in question:
            return """
SELECT
    c.customer_id,
    c.name,
    SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spending DESC;
""".strip()


    # ==========================================
    # TOP N
    # ==========================================

    if intent == "TOP_N":

        if "product" in question:
            return """
SELECT *
FROM products
ORDER BY price DESC
LIMIT 5;
""".strip()

        if "customer" in question:
            return """
SELECT
    c.customer_id,
    c.name,
    SUM(o.total_amount) AS total_spending
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spending DESC
LIMIT 5;
""".strip()

        if "order" in question:
            return """
SELECT *
FROM orders
ORDER BY total_amount DESC
LIMIT 5;
""".strip()


    # ==========================================
    # JOIN
    # ==========================================

    if intent == "JOIN":

        if "customer" in question and "order" in question:
            return """
SELECT
    c.customer_id,
    c.name,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id;
""".strip()

        if "product" in question and "review" in question:
            return """
SELECT
    p.product_id,
    p.product_name,
    r.rating,
    r.review_text
FROM products p
JOIN product_reviews r
    ON p.product_id = r.product_id;
""".strip()


    # ==========================================
    # LEFT JOIN
    # ==========================================

    if intent == "LEFT_JOIN":

        if "product" in question and "review" in question:
            return """
SELECT
    p.product_id,
    p.product_name,
    r.review_id,
    r.rating
FROM products p
LEFT JOIN product_reviews r
    ON p.product_id = r.product_id;
""".strip()

        if "customer" in question and "order" in question:
            return """
SELECT
    c.customer_id,
    c.name,
    o.order_id,
    o.total_amount
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id;
""".strip()


    # ==========================================
    # FALLBACK
    # ==========================================

    return None

