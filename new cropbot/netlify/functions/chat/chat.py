import json
import os
import requests


def handler(event, context):
    if event.get("httpMethod") != "POST":
        return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}

    try:
        body = json.loads(event.get("body") or "{}")
        user_input = body.get("message", "").strip()

        if not user_input:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Message cannot be empty"}),
            }

        api_url = os.environ.get("HUGGINGFACE_API_URL", "")
        api_key = os.environ.get("HUGGINGFACE_API_KEY", "")

        if not api_url or not api_key:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "response": "Chat service not configured yet. Set HUGGINGFACE_API_URL and HUGGINGFACE_API_KEY in Netlify environment variables."
                }),
            }

        prompt = f"You are a friendly farming assistant. User said: {user_input}"
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "temperature": 0.7, "top_p": 0.9},
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        reply = data[0]["generated_text"] if isinstance(data, list) else str(data)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"response": reply}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
