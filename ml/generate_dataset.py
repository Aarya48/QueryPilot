import csv
import random
from pathlib import Path


random.seed(42)

OUTPUT_PATH = Path(__file__).resolve().parent / "intent_dataset.csv"


# =========================================================
# QueryPilot actual database concepts
# =========================================================

customers = [
    "customers",
    "customer records",
    "customers in the database",
]

products = [
    "products",
    "product records",
    "items in the product catalog",
]

orders = [
    "orders",
    "customer orders",
    "order records",
]

reviews = [
    "product reviews",
    "reviews",
    "product review records",
]

order_items = [
    "order items",
    "items in orders",
    "ordered products",
]

customer_filters = [
    "from Delhi",
    "from Mumbai",
    "from Bangalore",
    "from Hyderabad",
    "from Pune",
    "from Chennai",
    "from Kolkata",
]

product_filters = [
    "priced below 500",
    "priced below 1000",
    "priced above 5000",
    "with high ratings",
    "with low ratings",
]

order_filters = [
    "above 1000",
    "above 5000",
    "below 1000",
    "from this month",
    "from last month",
    "from this year",
]

review_filters = [
    "with a rating above 4",
    "with a rating below 3",
    "with high ratings",
    "with low ratings",
]

numbers = [3, 5, 10, 20, 50]


# =========================================================
# INTENT DATA
# =========================================================

data = {}


def add(intent, questions):
    data[intent] = questions


# =========================================================
# COUNT
# =========================================================

add("COUNT", [
    f"How many {x} are there?" for x in
    [*customers, *products, *orders, *reviews, *order_items]
])

data["COUNT"] += [
    "What is the total number of customers?",
    "What is the total number of products?",
    "How many orders have been placed?",
    "How many product reviews exist?",
    "How many order items are there?",
    "Give me the customer count.",
    "Give me the product count.",
    "Give me the order count.",
    "Tell me how many reviews exist.",
    "Count all the orders.",
    "Count all the products.",
    "Count all the customers.",
    "What is the number of customer records?",
    "What is the number of product records?",
    "What is the number of order records?",
]


# =========================================================
# FILTER
# =========================================================
add("FILTER", [
    "Find customers from Delhi.",
    "Find customers from Mumbai.",
    "Find customers from Bangalore.",
    "Find customers from Hyderabad.",
    "Find customers from Pune.",
    "Find customers from Chennai.",
    "Show customers from Delhi.",
    "Show customers from Mumbai.",
    "List customers from Bangalore.",
    "List customers from Hyderabad.",

    "Find products priced below 500.",
    "Find products priced above 1000.",
    "Show products with price below 500.",
    "Show products with price above 1000.",
    "Find products with rating above 4.",
    "Find products with rating below 3.",
    "Show products with ratings above 4.",
    "Show products with ratings below 3.",

    "Find orders above 1000.",
    "Find orders below 500.",
    "Show orders with amount above 1000.",
    "Show orders with amount below 500.",

    "Find reviews with rating 5.",
    "Find reviews with rating above 4.",
    "Find reviews with rating below 3.",
    "Show reviews with a rating of 5.",
])
add("FILTER", [
    f"Show customers {x}." for x in customer_filters
] + [
    f"Find customers {x}." for x in customer_filters
] + [
    f"List customers {x}." for x in customer_filters
] + [
    f"Show products {x}." for x in product_filters
] + [
    f"Find products {x}." for x in product_filters
] + [
    f"List products {x}." for x in product_filters
] + [
    f"Show orders {x}." for x in order_filters
] + [
    f"Find orders {x}." for x in order_filters
] + [
    f"List orders {x}." for x in order_filters
] + [
    f"Show reviews {x}." for x in review_filters
] + [
    f"Find reviews {x}." for x in review_filters
])


# =========================================================
# SORT
# =========================================================

add("SORT", [
    "Sort customers by spending.",
    "Sort customers by number of orders.",
    "Sort products by price.",
    "Sort products by rating.",
    "Sort products by number of reviews.",
    "Sort orders by amount.",
    "Sort orders by date.",
    "Sort reviews by rating.",
    "Show customers ordered by spending.",
    "Show customers ordered by number of orders.",
    "Show products ordered by price.",
    "Show products ordered by rating.",
    "Show orders from highest amount to lowest.",
    "Show orders from newest to oldest.",
    "Order products by their price.",
    "Order customers by their total spending.",
    "Which customers have the highest spending?",
    "Which products have the highest ratings?",
    "Which orders have the highest amounts?",
])


# =========================================================
# TOP_N
# =========================================================

add("TOP_N", [
    f"Show the top {n} customers by spending." for n in numbers
] + [
    f"Show the top {n} products by price." for n in numbers
] + [
    f"Show the top {n} products by rating." for n in numbers
] + [
    f"Show the top {n} customers by number of orders." for n in numbers
] + [
    f"Show the top {n} orders by amount." for n in numbers
] + [
    f"Give me the top {n} products with the most reviews." for n in numbers
])


# =========================================================
# BOTTOM_N
# =========================================================

add("BOTTOM_N", [
    f"Show the bottom {n} customers by spending." for n in numbers
] + [
    f"Show the bottom {n} products by price." for n in numbers
] + [
    f"Show the bottom {n} products by rating." for n in numbers
] + [
    f"Show the bottom {n} customers by number of orders." for n in numbers
] + [
    f"Show the bottom {n} orders by amount." for n in numbers
])


# =========================================================
# AGGREGATION TYPES
# =========================================================

add("SUM", [
    "What is the total order amount?",
    "What is the total sales?",
    "Calculate total revenue from orders.",
    "What is the sum of all order amounts?",
    "How much money was generated from orders?",
    "Calculate total customer spending.",
    "What is the total value of all orders?",
    "Give me the total sales amount.",
    "What is the combined value of all orders?",
    "Calculate the overall order value.",
])

add("AVERAGE", [
    "What is the average order amount?",
    "What is the average product price?",
    "What is the average product rating?",
    "Calculate the average order value.",
    "Calculate the average price of products.",
    "Find the average review rating.",
    "What is the mean order amount?",
    "What is the average customer spending?",
    "Give me the average order value.",
    "Find the average product rating.",
])

add("MINIMUM", [
    "What is the minimum order amount?",
    "What is the lowest product price?",
    "What is the lowest product rating?",
    "Find the smallest order amount.",
    "Which product has the lowest price?",
    "Which product has the lowest rating?",
    "What is the minimum customer spending?",
    "Find the lowest order value.",
])

add("MAXIMUM", [
    "What is the maximum order amount?",
    "What is the highest product price?",
    "What is the highest product rating?",
    "Find the largest order amount.",
    "Which product has the highest price?",
    "Which product has the highest rating?",
    "What is the maximum customer spending?",
    "Find the highest order value.",
])


# =========================================================
# GROUP BY
# =========================================================

add("GROUP_BY", [
    "Show total sales by customer.",
    "Show total sales by product.",
    "Show order count by customer.",
    "Show review count by product.",
    "Show average rating by product.",
    "Show orders grouped by customer.",
    "Show products grouped by rating.",
    "Show reviews grouped by rating.",
    "Show the number of orders for each customer.",
    "Show the number of reviews for each product.",
    "Calculate total order value for each customer.",
    "Calculate average rating for each product.",
    "Give me a breakdown of orders by customer.",
    "Give me a breakdown of reviews by product.",
])


# =========================================================
# DISTINCT
# =========================================================

add("DISTINCT", [
    "Show unique customer cities.",
    "List distinct customer cities.",
    "What different cities do customers come from?",
    "Show all unique customer locations.",
    "How many unique customer cities are there?",
    "List unique product categories.",
    "Show distinct product categories.",
    "What different product categories exist?",
    "List unique review ratings.",
    "Show all distinct ratings.",
])


# =========================================================
# JOIN
# =========================================================

add("JOIN", [
    "Show customers with their orders.",
    "Which customers have placed orders?",
    "Show orders with customer information.",
    "List customers and their orders.",
    "Show products with their reviews.",
    "Which products have received reviews?",
    "Show product reviews with product information.",
    "List products and their reviews.",
    "Show orders with their order items.",
    "Which orders contain which order items?",
    "Show order items with their products.",
    "Which products appear in order items?",
    "Show customers and their reviews.",
    "Which customers have written reviews?",
])


# =========================================================
# LEFT JOIN
# =========================================================

add("LEFT_JOIN", [
    "Show all customers including those without orders.",
    "List every customer and their orders if they have any.",
    "Show all customers whether or not they placed an order.",
    "Find customers who may not have any orders.",
    "Show all products including products without reviews.",
    "List every product with reviews if available.",
    "Show all products whether or not they have reviews.",
    "Find products that may not have reviews.",
    "Show all orders including orders without order items.",
    "List every order with its items if available.",
])


# =========================================================
# MULTI TABLE JOIN
# =========================================================

add("MULTI_TABLE_JOIN", [
    "Show customers and the products they ordered.",
    "Show customers with their orders and order items.",
    "Show customers, orders, and products.",
    "Which customers purchased which products?",
    "Show customer names with the products they purchased.",
    "Show products ordered by each customer.",
    "Show customers, products, and their reviews.",
    "Show customer information with product reviews.",
    "Connect customers, orders, order items, and products.",
    "Show the complete customer order history with products.",
    "Show orders with customers and products.",
    "Show products along with their orders and customers.",
])


# =========================================================
# SUBQUERY
# =========================================================

add("SUBQUERY", [
    "Find customers whose spending is above the average customer spending.",
    "Show products priced above the average product price.",
    "Find orders above the average order amount.",
    "Which products have a rating above the average rating?",
    "Show customers who placed more orders than the average customer.",
    "Find orders with amounts greater than the average order amount.",
    "Which products cost more than the average product?",
    "Show customers whose total spending exceeds the average.",
])


# =========================================================
# HAVING
# =========================================================

add("HAVING", [
    "Which customers have placed more than 10 orders?",
    "Which customers have placed more than 5 orders?",
    "Show customers with at least 10 orders.",
    "Show customers whose total spending exceeds 10000.",
    "Which products have more than 10 reviews?",
    "Which products have at least 5 reviews?",
    "Show products with more than 20 reviews.",
    "Which ratings have more than 100 reviews?",
    "Group customers by orders and show groups with more than 10 orders.",
])


# =========================================================
# DATE FILTER
# =========================================================

add("DATE_FILTER", [
    "Show orders from this month.",
    "Show orders from last month.",
    "Show orders from this year.",
    "Show orders from last year.",
    "Show recent orders.",
    "Find recent orders.",
    "List orders from this month.",
    "List orders from last month.",
    "List orders from this year.",
    "Find orders placed this month.",
    "Find orders placed last month.",
    "Find orders placed this year.",
    "Show orders from January.",
    "Show orders from February.",
    "Show orders from March.",
    "Show orders from April.",
    "Show orders from May.",
    "Show orders from June.",
    "Show orders from July.",
    "Show orders from August.",
    "Show orders from September.",
    "Show orders from October.",
    "Show orders from November.",
    "Show orders from December.",
])

# =========================================================
# DATE AGGREGATION
# =========================================================

add("DATE_AGGREGATION", [
    "Show order totals by month.",
    "Show order count by month.",
    "Show revenue by month.",
    "Show sales by month.",
    "Show orders grouped by year.",
    "Show revenue grouped by year.",
    "Calculate monthly order totals.",
    "Calculate yearly order totals.",
    "Show average order amount by month.",
    "Show monthly order counts.",
])


# =========================================================
# TREND
# =========================================================

add("TREND", [
    "Show the trend in sales over time.",
    "Show the order trend over time.",
    "How have order amounts changed over time?",
    "How has revenue changed over time?",
    "Show monthly sales trends.",
    "Show monthly order trends.",
    "Analyze the change in sales over time.",
    "How are orders changing over time?",
    "Show the historical sales trend.",
    "Show revenue growth over time.",
])


# =========================================================
# COMPARISON
# =========================================================

add("COMPARISON", [
    "Compare sales between two periods.",
    "Compare order amounts between two periods.",
    "Compare product prices.",
    "Compare product ratings.",
    "Compare customer spending.",
    "Compare order counts between customers.",
    "Which product has a higher rating?",
    "Which group has higher sales?",
    "Compare the performance of two products.",
    "Compare sales across two groups.",
])


# =========================================================
# RANKING
# =========================================================

add("RANKING", [
    "Rank customers by spending.",
    "Rank customers by number of orders.",
    "Rank products by price.",
    "Rank products by rating.",
    "Rank products by number of reviews.",
    "Rank orders by amount.",
    "Give me the ranking of customers by spending.",
    "Rank all products according to their ratings.",
    "What is the ranking of products by price?",
])


# =========================================================
# PERCENTAGE
# =========================================================

add("PERCENTAGE", [
    "What percentage of customers have placed orders?",
    "What percentage of products have reviews?",
    "What percentage of orders are above 5000?",
    "What percentage of reviews have a rating above 4?",
    "What percentage of customers are from Delhi?",
    "Calculate the percentage of orders from this month.",
    "What percentage of products are highly rated?",
    "Calculate the proportion of customers with orders.",
])


# =========================================================
# RATIO
# =========================================================

add("RATIO", [
    "What is the ratio of orders to customers?",
    "What is the ratio of reviews to products?",
    "Calculate the ratio of orders to customers.",
    "What is the ratio between product reviews and products?",
    "Find the ratio of customers with orders to total customers.",
    "Calculate the ratio of high rated products to all products.",
])


# =========================================================
# NULL CHECK
# =========================================================

add("NULL_CHECK", [
    "Show customers with missing information.",
    "Find products with missing values.",
    "Show orders with missing values.",
    "Find reviews with missing ratings.",
    "Which records have null values?",
    "How many customers have missing values?",
    "Find products where a field is missing.",
    "Show orders where information is unavailable.",
])


# =========================================================
# DUPLICATE CHECK
# =========================================================

add("DUPLICATE_CHECK", [
    "Find duplicate customers.",
    "Find duplicate products.",
    "Find duplicate orders.",
    "Find duplicate reviews.",
    "Are there duplicate customer records?",
    "Are there duplicate product records?",
    "Check customers for duplicate records.",
    "Check products for duplicate records.",
    "Identify repeated customer records.",
    "Identify duplicate entries in the database.",
])


# =========================================================
# EXISTS
# =========================================================

add("EXISTS", [
    "Find customers who have at least one order.",
    "Which customers have orders?",
    "Show customers who have placed an order.",
    "Find products that have at least one review.",
    "Which products have reviews?",
    "Show products that have received reviews.",
    "Find orders that contain order items.",
    "Which orders have order items?",
])


# =========================================================
# NOT EXISTS
# =========================================================

add("NOT_EXISTS", [
    "Find customers who have no orders.",
    "Which customers have never placed an order?",
    "Show customers without orders.",
    "Find products that have no reviews.",
    "Which products have never received a review?",
    "Show products without reviews.",
    "Find orders without order items.",
    "Which orders have no items?",
])


# =========================================================
# GROWTH
# =========================================================

add("GROWTH", [
    "What is the growth in sales?",
    "Calculate revenue growth.",
    "How much have orders grown?",
    "What is the growth rate of sales?",
    "Calculate the growth in order value.",
    "Show sales growth compared with the previous period.",
    "How much has revenue increased?",
    "Calculate month-over-month sales growth.",
])


# =========================================================
# CHANGE OVER TIME
# =========================================================

add("CHANGE_OVER_TIME", [
    "How much did sales change over time?",
    "Show changes in order amounts over time.",
    "How did revenue change between months?",
    "Show month-to-month changes in sales.",
    "Calculate changes in order volume over time.",
    "Compare order totals across different periods.",
    "Show period-over-period changes in revenue.",
])


# =========================================================
# DISTRIBUTION
# =========================================================

add("DISTRIBUTION", [
    "Show the distribution of product ratings.",
    "Show the distribution of order amounts.",
    "How are product prices distributed?",
    "Show the distribution of customer spending.",
    "Analyze the distribution of review ratings.",
    "How are orders distributed by amount?",
    "Give me the distribution of product prices.",
])


# =========================================================
# CONTRIBUTION
# =========================================================

add("CONTRIBUTION", [
    "Which customers contribute the most to total sales?",
    "Which products contribute the most to revenue?",
    "Show each customer's contribution to total sales.",
    "Show each product's contribution to total revenue.",
    "Which products contribute most to total sales?",
    "Calculate customer contribution to total spending.",
])


# =========================================================
# SHARE
# =========================================================

add("SHARE", [
    "What share of total sales comes from each customer?",
    "What share of revenue comes from each product?",
    "Calculate each customer's share of total spending.",
    "Calculate each product's share of total sales.",
    "Which product has the largest share of sales?",
    "Which customer accounts for the largest share of spending?",
])


# =========================================================
# SCHEMA / DATABASE INFORMATION
# =========================================================

add("SCHEMA_INFO", [
    "What tables are in the database?",
    "Show me the database schema.",
    "What is the database structure?",
    "List all available tables.",
    "What tables can I query?",
    "Show the schema of the database.",
    "Which tables are available in QueryPilot?",
    "What data tables are available?",
    "Tell me about the database structure.",
    "What entities are stored in the database?",
])


add("TABLE_INFO", [
    "What columns are in the customers table?",
    "Describe the customers table.",
    "Show the structure of customers.",
    "What fields does customers contain?",
    "What columns are in the products table?",
    "Describe the products table.",
    "Show the structure of products.",
    "What columns are in the orders table?",
    "Describe the orders table.",
    "What columns are in the order_items table?",
    "Describe the order_items table.",
    "What columns are in the product_reviews table?",
    "Describe the product_reviews table.",
])


add("RELATIONSHIP_INFO", [
    "How are customers and orders related?",
    "How are orders and order items related?",
    "How are products and order items related?",
    "How are products and reviews related?",
    "How are customers and reviews related?",
    "Which table is related to customers?",
    "Which tables can be joined with orders?",
    "Which tables can be joined with products?",
    "Show the relationships between the tables.",
    "Explain the foreign key relationships.",
])


# =========================================================
# DATA QUALITY
# =========================================================

add("DATA_QUALITY", [
    "Check the data quality of customers.",
    "Check the data quality of products.",
    "Check the data quality of orders.",
    "Check the data quality of order items.",
    "Check the data quality of product reviews.",
    "Are there missing values in customers?",
    "Are there duplicate products?",
    "Are there invalid orders?",
    "Give me a data quality report.",
    "Check the database for data quality problems.",
])


# =========================================================
# GREETING
# =========================================================

add("GREETING", [
    "Hello",
    "Hi",
    "Hey",
    "Hi QueryPilot",
    "Hello QueryPilot",
    "Good morning",
    "Good afternoon",
    "Can you help me?",
    "Hey there",
    "I need help",
    "Hello there",
    "Hi there",
])


# =========================================================
# INVALID QUERY
# =========================================================

add("INVALID_QUERY", [
    "asdfgh",
    "qwerty",
    "random words",
    "This does not make sense",
    "I don't know what to ask",
    "Something random",
    "Can you do something impossible?",
    "Random unrelated question",
    "This is not a database question",
    "Give me something meaningless",
])


# =========================================================
# UNSUPPORTED REQUEST
# =========================================================

add("UNSUPPORTED_REQUEST", [
    "Delete all customers.",
    "Delete all orders.",
    "Drop the customers table.",
    "Drop the products table.",
    "Delete every product.",
    "Delete all reviews.",
    "Update every customer record.",
    "Change the database password.",
    "Modify the database configuration.",
    "Drop the entire database.",
])


# =========================================================
# Extra paraphrasing
# =========================================================

prefixes = [
    "",
    "Please ",
    "Can you ",
    "Could you ",
    "I want to know: ",
    "I need to know: ",
]

suffixes = [
    "",
    "?",
]

rows = []


# Generate variations
for intent, questions in data.items():

    # Start with original curated questions
    unique_questions = set()

    for question in questions:
        question = question.strip()

        if question:
            unique_questions.add(question)

    # Generate variations until we have a healthy amount
    base_questions = list(unique_questions)

    attempts = 0

    while len(unique_questions) < 100 and attempts < 1000:

        attempts += 1

        base = random.choice(base_questions)
        prefix = random.choice(prefixes)

        # Avoid "Please How..." style
        if prefix == "Please ":
            variation = prefix + base[0].lower() + base[1:]
        elif prefix:
            variation = prefix + base[0].lower() + base[1:]
        else:
            variation = base

        if not variation.endswith((".", "?")):
            variation += random.choice(suffixes)

        unique_questions.add(variation)

    for question in unique_questions:
        rows.append({
            "text": question,
            "intent": intent
        })


# =========================================================
# Shuffle + save
# =========================================================

random.shuffle(rows)

with open(
    OUTPUT_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=["text", "intent"]
    )

    writer.writeheader()
    writer.writerows(rows)


# =========================================================
# Summary
# =========================================================

print("\nQueryPilot Intent Dataset Generated!")
print("-----------------------------------")
print(f"Total examples: {len(rows)}")
print(f"Total intents: {len(data)}")
print(f"Saved to: {OUTPUT_PATH}")

print("\nExamples per intent:")

counts = {}

for row in rows:
    counts[row["intent"]] = counts.get(row["intent"], 0) + 1

for intent in sorted(counts):
    print(f"{intent:25} {counts[intent]}")