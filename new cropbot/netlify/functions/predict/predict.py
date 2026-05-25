import json
import os
import warnings

warnings.filterwarnings("ignore")


def handler(event, context):
    if event.get("httpMethod") != "POST":
        return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}

    try:
        import pickle
        import numpy as np

        body = json.loads(event.get("body") or "{}")
        N = float(body["N"])
        P = float(body["P"])
        K = float(body["K"])
        temp = float(body["temperature"])
        humidity = float(body["humidity"])
        ph = float(body["ph"])
        rainfall = float(body["rainfall"])

        task_root = os.environ.get("LAMBDA_TASK_ROOT", os.getcwd())
        model_path = os.path.join(task_root, "models", "crop_model.pkl")

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        crop = str(model.predict(np.array([[N, P, K, temp, humidity, ph, rainfall]]))[0])

        recs = [f"Recommended Crop: {crop}"]
        if N < 50:
            recs.append("Add nitrogen-rich fertilizer.")
        if P < 40:
            recs.append("Add phosphorus-rich fertilizer.")
        if K < 40:
            recs.append("Add potassium-rich fertilizer.")
        if humidity < 60:
            recs.append("Irrigate - humidity is low.")
        if rainfall < 100:
            recs.append("Insufficient rainfall - consider irrigation.")
        if ph < 6.0:
            recs.append("Add lime - soil pH too low.")
        elif ph > 7.0:
            recs.append("Add sulfur - soil pH too high.")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"crop": crop, "recommendations": recs}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
