import pandas as pd

df = pd.read_csv("intent_dataset.csv")

print("\n========== DATASET INFO ==========")
print("Shape:", df.shape)
print("Columns:", list(df.columns))

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE QUESTIONS ==========")
duplicates = df[df.duplicated(subset=["text"], keep=False)]

if duplicates.empty:
    print("No duplicate questions found.")
else:
    print(duplicates.sort_values("text").to_string(index=False))

print("\n========== INTENT DISTRIBUTION ==========")
print(df["intent"].value_counts().sort_index())

print("\n========== UNIQUE INTENTS ==========")
print("Total intents:", df["intent"].nunique())

print("\n========== RANDOM SAMPLES ==========")

for intent in sorted(df["intent"].unique()):
    sample = df[df["intent"] == intent].sample(
        min(3, len(df[df["intent"] == intent])),
        random_state=42
    )

    print(f"\n--- {intent} ---")

    for text in sample["text"]:
        print("-", text)