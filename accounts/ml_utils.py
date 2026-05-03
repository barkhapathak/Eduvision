import joblib
import os

model = None
encoder = None

def load_model():
    global model, encoder
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(BASE_DIR, 'accounts/ml_models/student_model.pkl')
        encoder_path = os.path.join(BASE_DIR, 'accounts/ml_models/label_encoder.pkl')

        model = joblib.load(model_path)
        encoder = joblib.load(encoder_path)

    except Exception:
        print("Using fallback logic (model not loaded)")  # ✅ clean message
        model = None
        encoder = None


def predict_performance(attendance, marks, assignment):
    if model is None:
        avg = (attendance + marks + assignment) / 3

        if avg >= 75:
            return "Excellent"
        elif avg >= 60:
            return "Average"
        else:
            return "Poor"

    try:
        pred = model.predict([[attendance, marks, assignment]])[0]
        label = encoder.inverse_transform([pred])[0]

        display_map = {
            "HighPerformer": "Excellent",
            "Safe": "Average",
            "AtRisk": "Poor"
        }

        return display_map.get(label, label)

    except Exception as e:
        print("Prediction error:", e)
        return "Error"
    
def get_reason(attendance, marks, assignment):
    reasons = []

    if attendance < 60:
        reasons.append("Low Attendance")

    if marks < 50:
        reasons.append("Low Exam Marks")

    if assignment < 50:
        reasons.append("Low Assignments Marks")

    if not reasons:
        return "Good Performance"

    return ", ".join(reasons)
