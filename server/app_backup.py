import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from dotenv import load_dotenv
import requests  # Import the requests library
import xml.etree.ElementTree as ET

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='../client', static_url_path='')
CORS(app)  # Enable CORS for all routes

# --- LLM Interaction Placeholder Functions ---


def summarize_with_local_llm(transcript_text, is_detailed_explanation=False):
    """
    Summarizes or explains text using a locally running Ollama model.
    """
    action_type = "explain in detail like a teacher" if is_detailed_explanation else "summarize concisely"
    print(f"Attempting to {action_type} with local Ollama LLM...")
    ollama_api_url = "http://localhost:11434/api/generate"  # Your Ollama API endpoint
    model_name = "gemma3:latest"  # Corrected model name based on ollama list output

    if is_detailed_explanation:
        prompt = f"Act as a teacher and explain the following transcript line by line, providing examples and detailed explanations for concepts discussed. Be thorough and clear:\n\n{transcript_text}"
    else:
        prompt = f"Summarize the following transcript concisely:\n\n{transcript_text}"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False  # We want the full response, not a stream
    }

    try:
        response = requests.post(
            # Increased timeout for potentially longer explanations
            ollama_api_url, json=payload, timeout=300)

        print(f"Ollama API response status code: {response.status_code}")
        # Print first 500 chars
        print(f"Ollama API response text: {response.text[:500]}...")

        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            print(f"Failed to decode JSON response from Ollama: {json_err}")
            print(
                f"Ollama raw response that caused JSON error: {response.text}")
            return None

        content = response_data.get("response")

        if content:
            print(f"Successfully got content from {model_name}.")
            return content.strip()
        else:
            print(
                f"Ollama API response did not contain content. Response: {response_data}")
            return None

    except requests.exceptions.Timeout as e:
        print(f"Ollama API request timed out: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(
            f"Ollama API connection error. Is Ollama running at {ollama_api_url}? Error: {e}")
        return None
    except requests.exceptions.RequestException as e:  # Catches other requests-related errors like HTTPError
        print(f"Ollama API request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ollama error response status: {e.response.status_code}")
            print(f"Ollama error response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Ollama processing: {e}")
        return None


def summarize_with_api_llm(transcript_text, is_detailed_explanation=False):
    """Placeholder for summarizing or explaining text using a cloud-based LLM API."""
    action_type = "explain in detail" if is_detailed_explanation else "summarize"
    print(f"Attempting to {action_type} with API LLM...")
    api_key = os.getenv("OPENAI_API_KEY")  # Example for OpenAI

    if not api_key:
        print("API key or endpoint for LLM not found in .env file.")
        return None

    # Example for OpenAI API (requires 'openai' library: pip install openai)
    # from openai import OpenAI
    # client = OpenAI(api_key=api_key)
    # try:
    #     system_prompt = "You are a helpful assistant that summarizes video transcripts concisely."
    #     user_prompt = f"Please summarize the following transcript:\n\n{transcript_text}"
    #     if is_detailed_explanation:
    #         system_prompt = "You are a knowledgeable teacher. Explain the following transcript line by line, providing examples and detailed explanations for concepts discussed. Be thorough and clear."
    #         user_prompt = f"Please explain the following transcript in detail:\n\n{transcript_text}"

    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo", # Or your preferred model
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt}
    #         ]
    #     )
    #     content = response.choices[0].message.content
    #     return content
    # except Exception as e:
    #     print(f"OpenAI API call failed: {e}")
    #     return None

    print(f"API LLM {action_type} not implemented yet.")
    return None

# --- API Endpoints ---


@app.route('/api/chat', methods=['POST'])
def chat_with_model_endpoint():
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    print(f"Received chat message: {user_message}", flush=True)

    # Use the local LLM for chat for now
    # You might want a different prompt or model configuration for general chat
    ollama_api_url = "http://localhost:11434/api/generate"
    model_name = "gemma3:latest"

    # More conversational prompt for chat
    prompt = f"User: {user_message}\nAI:"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        # Shorter timeout for chat?
        response = requests.post(ollama_api_url, json=payload, timeout=180)
        print(
            f"Ollama API response status code for chat: {response.status_code}", flush=True)
        response_text_preview = response.text[:500] if response.text else ""
        print(
            f"Ollama API response text preview for chat: {response_text_preview}...", flush=True)

        response.raise_for_status()

        if not response.text or not response.text.strip():
            print(
                "Ollama API response for chat was empty. Returning generic error.", flush=True)
            return jsonify({"error": "AI model returned an empty response."}), 500

        response_data = response.json()
        ai_reply = response_data.get("response")

        if ai_reply:
            print(
                f"Successfully got chat reply from {model_name}.", flush=True)
            return jsonify({"reply": ai_reply.strip()})
        else:
            print(
                f"Ollama API chat response did not contain content. Response: {response_data}", flush=True)
            return jsonify({"error": "AI model did not provide a reply."}), 500

    except requests.exceptions.Timeout:
        print("Ollama API chat request timed out.", flush=True)
        return jsonify({"error": "Request to AI model timed out."}), 504
    except requests.exceptions.ConnectionError:
        print(
            f"Ollama API chat connection error. Is Ollama running at {ollama_api_url}?", flush=True)
        return jsonify({"error": "Could not connect to the AI model."}), 503
    except requests.exceptions.RequestException as e:
        print(f"Ollama API chat request failed: {e}", flush=True)
        return jsonify({"error": "Failed to communicate with the AI model."}), 502
    except Exception as e:
        print(
            f"An unexpected error occurred during chat processing: {e}", flush=True)
        return jsonify({"error": "An unexpected error occurred while chatting with the AI."}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize_video_endpoint():  # Renamed to avoid conflict
    return handle_transcript_processing(request, is_detailed_explanation=False)


@app.route('/api/explain', methods=['POST'])
def explain_video_endpoint():  # New endpoint
    return handle_transcript_processing(request, is_detailed_explanation=True)


def handle_transcript_processing(current_request, is_detailed_explanation):
    data = current_request.get_json()
    youtube_url = data.get('youtube_url')

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:        video_id = None
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL format"}), 400

        print(f"Fetching transcript for video ID: {video_id}")
        
        # Try to get transcript with better error handling
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception as transcript_error:
            print(f"Transcript fetch error: {transcript_error}")
            # Try alternative language codes if English fails
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en-GB', 'en'])
            except Exception as lang_error:
                print(f"Alternative language transcript fetch error: {lang_error}")
                raise transcript_error  # Re-raise the original error
        
        transcript_text = " ".join([item['text'] for item in transcript_list])

        if not transcript_text.strip():
            return jsonify({"error": "Fetched transcript is empty."}), 500

        action = "explanation" if is_detailed_explanation else "summary"
        print(
            f"Transcript fetched successfully for {action}. Length: {len(transcript_text)} chars.")

        # Try local LLM first
        content = summarize_with_local_llm(
            transcript_text, is_detailed_explanation)

        # Fallback to API LLM if local LLM fails or is not implemented
        if content is None:
            print(
                f"Local LLM failed or not implemented, trying API LLM for {action}.")
            content = summarize_with_api_llm(
                transcript_text, is_detailed_explanation)

        if content:
            return jsonify({action: content})
        else:
            return jsonify({"error": f"Failed to get {action} using all available methods."}), 500    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video. It might be disabled or not available in English."}), 404
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video."}), 403
    except VideoUnavailable:
        return jsonify({"error": "This video is unavailable or private."}), 404
    except ET.ParseError as xml_error:
        print(f"XML parsing error: {xml_error}")
        return jsonify({"error": "Failed to parse transcript data. The video transcript format may be corrupted."}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# --- Serve Client Files ---


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
