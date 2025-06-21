# =================================================================
# CodeX - Flask Backend Server
# =================================================================
# Prothome kichu jinis install korte hobe:
# pip install Flask flask-cors openai
# =================================================================

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json

# Flask app initialize kora
app = Flask(__name__)
# CORS enable kora, jate frontend theke request ashe
CORS(app)

# --- OpenAI API Key Setup ---
# Apnar dewa API key-ti ekhane set kora hoyeche
openai.api_key = "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"

# --- Helper Function for API Call ---
def get_ai_response(prompt):
    """
    ChatGPT API ke call kore ebong JSON response return kore.
    """
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert YouTube and social media strategist. Respond ONLY with the requested JSON object, no other text or explanation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

# --- API Endpoints ---

@app.route('/api/generate-strategy', methods=['POST'])
def generate_strategy():
    """
    Frontend theke topic, category niye full strategy toiri kore.
    """
    data = request.json
    prompt = (
        f"You are a YouTube SEO expert. A content creator in {data.get('location', 'Global')} wants to make a "
        f"{data.get('contentType', 'video')} for {data.get('platform', 'YouTube')} in the "
        f"'{data.get('category', 'General')}' category. The main topic is \"{data.get('topic')}\". "
        f"Provide a JSON object with: 1. A key \"titles\" with an array of 5 SEO-optimized, catchy titles. "
        f"2. A key \"description\" with a full, engaging, hook-based video description including relevant hashtags. "
        f"3. A key \"tags\" with an array of 10 high-performing keywords/tags."
    )
    
    response_data = get_ai_response(prompt)
    if response_data:
        return jsonify(response_data)
    return jsonify({"error": "Failed to get response from AI"}), 500

@app.route('/api/expand-ideas', methods=['POST'])
def expand_ideas():
    """
    Ekta simple idea theke 3ta notun idea toiri kore.
    """
    data = request.json
    prompt = (
        f"You are a creative assistant for YouTubers. Take the user's video idea \"{data.get('topic')}\" "
        f"and expand it into 3 more engaging and specific video concepts. For each concept, provide a short, catchy "
        f"title and a one-sentence concept. Respond with a JSON object that has a single key \"ideas\", which is an "
        f"array of objects, each with \"title\" and \"concept\" keys."
    )

    response_data = get_ai_response(prompt)
    if response_data:
        return jsonify(response_data)
    return jsonify({"error": "Failed to get response from AI"}), 500

@app.route('/api/generate-hook', methods=['POST'])
def generate_hook():
    """
    Video'r title theke 5-seconder hook toiri kore.
    """
    data = request.json
    prompt = (
        f"You are an expert scriptwriter. Based on the video title \"{data.get('title')}\", write a powerful, 50-word "
        f"script hook to grab the viewer's attention in the first 5 seconds. Respond with a JSON object containing "
        f"a single key \"hook\"."
    )
    
    response_data = get_ai_response(prompt)
    if response_data:
        return jsonify(response_data)
    return jsonify({"error": "Failed to get response from AI"}), 500


# Server run korar jonno
