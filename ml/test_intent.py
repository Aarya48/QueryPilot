import joblib


model = joblib.load("intent_classifier.pkl")


questions = [
    "How many customers do we have?",
    "Show me the five most expensive products.",
    "Which customers have never placed an order?",
    "Show me products that do not have any reviews.",
    "What was our revenue last month?",
    "Show products with rating greater than 4.",
    "Sort customers by their spending.",
    "Hello QueryPilot",
]


print("\n========== INTENT PREDICTIONS ==========\n")

for question in questions:
    prediction = model.predict([question])[0]
    probability = model.predict_proba([question]).max()

    print(f"Question    : {question}")
    print(f"Intent      : {prediction}")
    print(f"Confidence  : {probability:.2%}")
    print("-" * 60)