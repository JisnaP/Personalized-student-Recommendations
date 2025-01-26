import pandas

def process_quiz_records(data):
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
    return records
