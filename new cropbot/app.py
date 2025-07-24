from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import pickle
import numpy as np
from translate import Translator
import requests
import json
import os
import warnings
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ✅ Suppress scikit-learn version mismatch warnings (safe for testing)
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_lah")  # ✅ Use env variable in production

# ✅ Hardcoded admin credentials (later move to DB)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# ✅ Hugging Face API details (FREE model - no license approval needed)
API_URL = ""
API_KEY = ""  # 🔥 Replace with your Hugging Face token


# ✅ Load the crop prediction model safely
def load_model():
    model_path = os.path.join(os.getcwd(), "models", "crop_model.pkl")
    if not os.path.exists(model_path):
        print(f"❌ Error: Crop model file not found at {model_path}. Run train.py first lah.")
        return None
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"❌ Error loading crop model: {e}")
        return None


model = load_model()


# ✅ Crop prediction function
def predict_crop(N, P, K, temp, humidity, ph, rainfall):
    if model is None:
        return "Bro, model not found lah!"
    try:
        input_data = np.array([[N, P, K, temp, humidity, ph, rainfall]])
        crop = model.predict(input_data)[0]
        return crop
    except Exception as e:
        return f"Aiyo, prediction failed lah: {str(e)}"


# ✅ Translation function
def translate_text(text, lang="en"):
    try:
        translator = Translator(to_lang=lang)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"⚠ Translation failed: {e}")
        return text


# ✅ Recommendation generator
def generate_recommendations(N, P, K, temp, humidity, ph, rainfall, pest_status, crop):
    recs = [f"Recommended Crop: {crop}"]
    if N < 50:
        recs.append("Add nitrogen-rich fertilizer lah.")
    if P < 40:
        recs.append("Add phosphorus-rich fertilizer sia.")
    if K < 40:
        recs.append("Add potassium-rich fertilizer bro.")
    if humidity < 60:
        recs.append("Irrigate lah, humidity damn low.")
    if rainfall < 100:
        recs.append("Need more water sia, rainfall not enough.")
    if ph < 6.0:
        recs.append("Add lime lah, soil pH too low.")
    elif ph > 7.0:
        recs.append("Add sulfur sia, pH too high.")
    if pest_status == "Pest Detected":
        recs.append("Got pests lah, use organic pesticide.")
    elif pest_status == "No Pest":
        recs.append("No pests sia, all good.")
    else:
        recs.append("Cannot tell pest status lah, reupload image.")
    return recs


# ✅ Chat function with Hugging Face API (Meta-LLaMA-3-8B-Instruct)
# ✅ New Chat function with Hugging Face (Flan-T5 works immediately)
def query_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200, "temperature": 0.7, "top_p": 0.9},
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data[0]["generated_text"] if isinstance(data, list) else str(data)
    except requests.exceptions.RequestException as e:
        return f"Aiyo, API problem lah: {str(e)}"


# ✅ JSON schemes loader & saver
def load_schemes():
    try:
        with open("schemes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_schemes(schemes):
    with open("schemes.json", "w") as f:
        json.dump(schemes, f, indent=4)


# ✅ LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("farmer_schemes"))
        return render_template("login.html", error="Wrong username or password lah!")
    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("home"))


# ✅ HOME (CROP RECOMMENDATION)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            N = float(request.form["N"])
            P = float(request.form["P"])
            K = float(request.form["K"])
            temp = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])
            language = request.form["language"]

            pest_status = "Unknown"
            if "image" in request.files:
                image = request.files["image"]
                if image.filename != "":
                    pest_status = "No Pest"  # ✅ Later replace with ML pest detection

            crop = predict_crop(N, P, K, temp, humidity, ph, rainfall)
            recommendations = generate_recommendations(N, P, K, temp, humidity, ph, rainfall, pest_status, crop)

            if language != "en":
                crop = translate_text(crop, language)
                recommendations = [translate_text(rec, language) for rec in recommendations]

            return render_template("results.html", crop=crop, recommendations=recommendations)
        except Exception as e:
            return render_template("index.html", error=f"Prediction failed lah: {e}")
    return render_template("index.html")


# ✅ CHAT ROUTE
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form["user_input"]
        prompt = f"Yo bro, you’re my buddy lah, chat with me like we’re just chilling sia. I said: {user_input}"
        bot_response = query_huggingface(prompt)
        return render_template("chat.html", user_input=user_input, bot_response=bot_response)
    return render_template("chat.html", user_input="", bot_response="")



# ✅ CROP ANIMATION (YouTube)
@app.route("/crop_animation")
def crop_animation():
    videos = [
        {"title": "The Farming Cycle", "id": "Dip81m1rRrM"},
        {"title": "How Plants Grow", "id": "DwDBVfsrQXo"},
        {"title": "Life of a Farmer", "id": "JDNCm-MQRsE"},
        {"title": "Water Cycle in Farming", "id": "j1HIClkuLnw"},
        {"title": "Photosynthesis Explained", "id": "oKzwgJMy0sQ"},
    ]
    return render_template("crop_animation.html", videos=videos)


# ✅ FARMER SCHEMES
@app.route("/farmer_schemes", methods=["GET", "POST"])
def farmer_schemes():
    schemes = load_schemes()
    if request.method == "POST":
        if "admin_add" in request.form:
            if not session.get("logged_in"):
                return redirect(url_for("login"))
            scheme_name = request.form["scheme_name"]
            scheme_desc = request.form["scheme_desc"]
            schemes.append({"name": scheme_name, "description": scheme_desc})
            save_schemes(schemes)

        language = request.form.get("language", "en")
        if language in ["kn", "ta", "ml"]:
            translated_schemes = [
                {"name": translate_text(s["name"], language), "description": translate_text(s["description"], language)}
                for s in schemes
            ]
            return render_template("farmer_schemes.html", schemes=translated_schemes, language=language)

    return render_template("farmer_schemes.html", schemes=schemes, language="en")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
