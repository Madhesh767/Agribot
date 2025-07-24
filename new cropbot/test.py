import requests
import json
import os

# Hugging Face API details for Mistral-7B-Instruct-v0.3
API_URL = ""
API_KEY = ""  # Replace with your API key

# List to store messages
messages = []

def get_ai_response(message, image_path=None):
    """Function to get AI response from Mistral-7B-Instruct-v0.3"""
    print(f"Sending request to {API_URL} with prompt: {message}")
    payload = {
        "inputs": f"<s>[INST] {message} [/INST]",
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
        },
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"Full API response: {data}")
            ai_reply = data[0]["generated_text"].replace(f"<s>[INST] {message} [/INST]", "").strip() or "No response"
            if not ai_reply.endswith(('.', '!', '?')):
                ai_reply += " (Response may be truncated)"
            return ai_reply
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error: {e}"

def pick_image():
    """Simulate image picking by asking for a file path"""
    image_path = input("Enter the path to an image file (or press Enter to skip): ").strip()
    if image_path and os.path.exists(image_path):
        return image_path
    return None

def get_new_content():
    """Function to search for new/trending content"""
    prompt = "Tell me about something new or trending today."
    return get_ai_response(prompt)

def main():
    """Main loop for the console chatbot"""
    print("Welcome to the Mistral-7B Chatbot!")
    while True:
        print("\nOptions:")
        print("1. Send a message")
        print("2. Add an image to your message")
        print("3. Get new/trending content")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            message = input("Type your message: ").strip()
            if message:
                print(f"You: {message}")
                ai_response = get_ai_response(message)
                print(f"AI: {ai_response}")
                messages.append({"sender": "You", "text": message})
                messages.append({"sender": "AI", "text": ai_response})
        
        elif choice == "2":
            message = input("Type your message: ").strip()
            image_path = pick_image()
            if message:
                print(f"You: {message}" + (f" [Image: {image_path}]" if image_path else ""))
                ai_response = get_ai_response(message)  # Note: API doesn't process images here
                print(f"AI: {ai_response}")
                messages.append({"sender": "You", "text": message, "image": image_path})
                messages.append({"sender": "AI", "text": ai_response})
        
        elif choice == "3":
            print("Fetching new content...")
            ai_response = get_new_content()
            print(f"AI: {ai_response}")
            messages.append({"sender": "AI", "text": ai_response})
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()