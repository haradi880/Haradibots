import json
import pandas as pd

# Load the intents.json
with open("G:/NEW/haradibots/data/intents.json", "r", encoding="utf-8") as f:
    data_json = json.load(f)

data = []
# Loop through each intent
for intent in data_json["intents"]:
    for pattern in intent["patterns"]:
        for response in intent["responses"]:
            data.append({"input": pattern.strip(), "output": response.strip()})

# Convert to CSV
df = pd.DataFrame(data)
df.to_csv("qna_dataset.csv", index=False)
print("Dataset saved as qna_dataset.csv with", len(df), "rows")
print(df.head())
