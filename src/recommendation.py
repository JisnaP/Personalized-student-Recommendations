import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def suggest_improvements(row):
    """
    Suggest improvements for a quiz taker based on their performance in a given topic.
    """
    # Evaluate accuracy
    if row["accuracy_percent"] < 70:
        improvement_area = "accuracy"
        suggestion = "Focus on improving accuracy in the topic: {}".format(row["topic"])

    # Check for mistakes allowed
    elif row["mistakes_allowed_left"] < 3:
        improvement_area = "mistake tolerance"
        suggestion = "Reduce mistakes in difficult questions for topic: {}".format(row["topic"])

    # Check for performance gaps
    elif row["performance_gap"] > 20:
        improvement_area = "performance gap"
        suggestion = "Focus on bridging the performance gap in the topic: {}".format(row["topic"])

    # General maintenance suggestion
    else:
        improvement_area = "maintenance"
        suggestion = "Maintain high accuracy in quizzes like: {}".format(row["quiz_title"])

    # Add detailed topic-specific advice
    if "key_concepts" in row:
        suggestion += " Review key concepts: {}".format(", ".join(row["key_concepts"]))

    return {"area": improvement_area, "suggestion": suggestion}






# Prepare a model to predict the improvement area
def train_improvement_model(data):
    # Use features like accuracy, mistakes_left, and performance_gap to train a model
    X = data[["accuracy_percent", "mistakes_allowed_left", "performance_gap"]]
    y = data["topic"]  # Assuming topic is the area we want to improve

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

    return model



def suggest_improvements_ml(row, model):
    """
    Suggest improvements based on a machine learning model and quiz performance.
    """
    # Predict improvement area using the trained model
    predicted_topic = model.predict([[row["accuracy_percent"], row["mistakes_allowed_left"], row["performance_gap"]]])[0]

    # Generate suggestion
    suggestion = f"Focus on improving in the topic: {predicted_topic}"

    # Add key concepts advice if available
    if "key_concepts" in row:
        suggestion += f" Review key concepts: {', '.join(row['key_concepts'])}"

    return {"suggestion": suggestion}

