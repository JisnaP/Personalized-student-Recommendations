from flask import Flask
import requests
import pandas as pd
from Data.datapreprocessing import pretty_print, save_json_to_file
from src.recommendation import train_improvement_model, suggest_improvements_ml
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)

json_url = "https://api.jsonserve.com/XgAgFJ"

# Fetch data globally
data = None
try:
    # Fetch the JSON data
    response = requests.get(json_url, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    # Pretty-print the fetched JSON data
    # pretty_print(data)

    # Save the JSON data to a file
    save_json_to_file(data, "../Data/fetched_data.json")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the JSON data: {e}")

# Process the data into a DataFrame
records = []
if data:
    for record in data:
        flat_record = {
            "user_id": record["user_id"],
            "submitted_at": record["submitted_at"],
            "quiz_id": record["quiz_id"],
            "quiz_title": record["quiz"]["title"],
            "topic": record["quiz"]["topic"],
            "difficulty_level": record["quiz"]["difficulty_level"],
            "total_questions": record["total_questions"],
            "correct_answers": record["correct_answers"],
            "incorrect_answers": record["incorrect_answers"],
            "score": record["score"],
            "accuracy_percent": float(record["accuracy"].strip(" %")),
            "negative_marks": float(record["quiz"]["negative_marks"]),
            "correct_answer_marks": float(record["quiz"]["correct_answer_marks"]),
            "max_mistake_count": record["quiz"]["max_mistake_count"],
        }
        # Calculate derived metrics
        flat_record["total_score_possible"] = (
            flat_record["total_questions"] * flat_record["correct_answer_marks"]
        )
        flat_record["total_negative_score"] = (
            flat_record["incorrect_answers"] * flat_record["negative_marks"]
        )
        flat_record["performance_gap"] = (
            flat_record["total_score_possible"] - flat_record["score"]
        )
        flat_record["mistakes_allowed_left"] = (
            flat_record["max_mistake_count"] - flat_record["incorrect_answers"]
        )
        records.append(flat_record)

# Create a DataFrame
df = pd.DataFrame(records)

# Save the DataFrame to CSV
df.to_csv("../Data/student_performance.csv", index=False)

@app.route("/", methods=["GET"])
def index():
    global df  # Ensure df is accessible within the function
    
    if df.empty:
        return "No data available to process."

    improvement_model = train_improvement_model(df)
    row = df.iloc[8]  # Example row
    improvement_suggestion = suggest_improvements_ml(row, improvement_model)
    print(improvement_suggestion)

    return improvement_suggestion

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
