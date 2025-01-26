from flask import Flask,request, jsonify
import requests
import pandas as pd
from src.utils import process_quiz_records
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
    save_json_to_file(data, "..\\PERSONALIZED-STUDENT-RECOMMENDATIONS\\Data\\fetched_data.json")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the JSON data: {e}")


 #process data into a dataframe         
records = process_quiz_records(data)

# Create a DataFrame
df = pd.DataFrame(records)

# Save the DataFrame to CSV
df.to_csv("..\\PERSONALIZED-STUDENT-RECOMMENDATIONS\\Data\\student_performance.csv", index=False)

json_url_quiz="https://www.jsonkeeper.com/b/LLQT"

# Sample Data (JSON) for quiz
quiz_data = None
try:
    # Fetch the JSON data
    response = requests.get(json_url_quiz, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors
    quiz_data = response.json()

    # Pretty-print the fetched JSON data
    # pretty_print(quiz_data)

    
    save_json_to_file(data, "..\\PERSONALIZED-STUDENT-RECOMMENDATIONS\\Data\\fetched_quiz_data.json")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the JSON data: {e}")

@app.route("/get_quiz_data", methods=["GET"])
def get_quiz_data():
    global quiz_data  # Access the global quiz data
    
    if not quiz_data:
        return jsonify({"error": "Quiz data not found"}), 404
    
    # Return the quiz data as JSON
    return jsonify(quiz_data), 200

@app.route('/submit_quiz', methods=['POST'])

def submit_quiz():
    # Get the student answers from the request data
    student_answers = request.json.get('answers')
    quiz_id = request.json.get('quiz_id')
    topic = request.json.get('topic')
    max_mistakes = request.json.get('max_mistakes', 15)  # Default mistakes allowed

    correct_answers_count = 0
    mistakes_left = max_mistakes

    # Calculate the accuracy and mistakes
    for question, student_answer in zip(quiz_data["quiz"]["questions"], student_answers):
        correct_option = next((opt for opt in question["options"] if opt["is_correct"]), None)
        if student_answer == correct_option["id"]:
            correct_answers_count += 1
        else:
            mistakes_left -= 1

    accuracy = (correct_answers_count / len(quiz_data["quiz"]["questions"])) * 100

    # Performance gap can be the difference between the total questions and the number of correct answers
    performance_gap = len(quiz_data["quiz"]["questions"]) - correct_answers_count

    # Create the response data
    response_data = {
        "accuracy": accuracy,
        "quiz_id": quiz_id,
        "topic": topic,
        "performance_gap": performance_gap,
        "mistakes_allowed_left": mistakes_left
    }

    # Call to recommender system (this can be an external function or API)
    # recommendation = recommender_system(response_data)

    # Return the response
    return jsonify(response_data), 200




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
