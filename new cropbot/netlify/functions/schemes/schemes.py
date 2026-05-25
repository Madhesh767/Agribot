import json
import os


def handler(event, context):
    task_root = os.environ.get("LAMBDA_TASK_ROOT", os.getcwd())
    schemes_path = os.path.join(task_root, "schemes.json")

    try:
        with open(schemes_path, "r") as f:
            schemes = json.load(f)
    except Exception:
        schemes = []

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(schemes),
    }
