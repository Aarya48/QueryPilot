"""
Simple Intent Classifier Fallback

Since the intent classifier model file is missing, this creates a
simple rule-based fallback classifier that works without the pickle file.
"""

import joblib
from pathlib import Path

class SimpleIntentClassifier:
    """Rule-based fallback intent classifier"""

    def __init__(self):
        self.intents = {
            'SELECT': 0,
            'COUNT': 1,
            'AGGREGATE': 2,
            'JOIN': 3,
        }

    def predict(self, questions):
        """Predict intent for questions"""
        if isinstance(questions, str):
            questions = [questions]

        predictions = []
        for q in questions:
            q_upper = q.upper()

            if any(word in q_upper for word in ['COUNT', 'HOW MANY', 'TOTAL']):
                predictions.append('COUNT')
            elif any(word in q_upper for word in ['SUM', 'AVERAGE', 'MAX', 'MIN', 'AGGREGATE']):
                predictions.append('AGGREGATE')
            elif any(word in q_upper for word in ['JOIN', 'RELATIONSHIP', 'RELATE']):
                predictions.append('JOIN')
            else:
                predictions.append('SELECT')

        return predictions if len(predictions) > 1 else predictions[0] if predictions else 'SELECT'

    def predict_proba(self, questions):
        """Return confidence scores"""
        if isinstance(questions, str):
            questions = [questions]

        # Simple heuristic: if question is clear, confidence is high
        confidences = []
        for q in questions:
            if len(q) > 20 and any(c in q for c in ['?', 'show', 'list', 'get']):
                confidences.append(0.85)
            elif len(q) > 10:
                confidences.append(0.75)
            else:
                confidences.append(0.60)

        # Return as max probability
        import numpy as np
        return np.array([[conf, 1-conf] for conf in confidences]) if len(confidences) > 1 else np.array([[confidences[0], 1-confidences[0]]])

    def max(self):
        """For compatibility with sklearn interface"""
        return 0.85


# Create and save the fallback classifier
if __name__ == "__main__":
    classifier = SimpleIntentClassifier()
    output_path = Path(__file__).parent / "intent_classifier.pkl"

    try:
        joblib.dump(classifier, str(output_path))
        print(f"[OK] Created fallback intent classifier: {output_path}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
