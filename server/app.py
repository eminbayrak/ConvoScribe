import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET

# Load environment variables from .env file
load_dotenv()

static_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../client'))
app = Flask(__name__, static_folder=static_folder_path, static_url_path='')
CORS(app)  # Enable CORS for all routes

# --- LLM Interaction Functions ---


def summarize_with_local_llm(transcript_text, is_detailed_explanation=False):
    """
    Summarizes or explains text using a locally running Ollama model.
    """
    action_type = "explain in detail like a teacher" if is_detailed_explanation else "summarize concisely"
    print(f"Attempting to {action_type} with local Ollama LLM...")
    ollama_api_url = "http://localhost:11434/api/generate"
    model_name = "gemma3:latest"

    if is_detailed_explanation:
        prompt = f"Act as a teacher and explain the following transcript line by line, providing examples and detailed explanations for concepts discussed. Be thorough and clear:\n\n{transcript_text}"
    else:
        prompt = f"Summarize the following transcript concisely:\n\n{transcript_text}"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(ollama_api_url, json=payload, timeout=300)
        print(f"Ollama API response status code: {response.status_code}")
        print(f"Ollama API response text: {response.text[:500]}...")

        response.raise_for_status()

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
    except requests.exceptions.RequestException as e:
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
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("API key or endpoint for LLM not found in .env file.")
        return None

    # Example for OpenAI API (requires 'openai' library: pip install openai)
    # Uncomment and modify as needed
    print(f"API LLM {action_type} not implemented yet.")
    return None

# --- API Endpoints ---


@app.route('/api/chat', methods=['POST'])
def chat_with_model_endpoint():
    data = request.get_json()
    user_message = data.get('message')
    images = data.get('images', [])  # Get base64 encoded images
    stream = data.get('stream', False)  # Add streaming support

    if not user_message and not images:
        return jsonify({"error": "Message or images are required"}), 400

    print(f"Received chat message: {user_message}", flush=True)
    print(f"Received {len(images)} images", flush=True)
    print(f"Streaming requested: {stream}", flush=True)

    # Check if images are provided - use vision model
    if images:
        return handle_image_chat(user_message, images, stream)
    else:
        return handle_text_chat(user_message, stream)


def handle_text_chat(user_message, stream=False):
    """Handle text-only chat using Gemma3"""
    from flask import Response, stream_template
    import json
    import time
    
    ollama_api_url = "http://localhost:11434/api/generate"
    model_name = "gemma3:latest"

    # More conversational prompt for chat
    prompt = f"User: {user_message}\nAI:"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream  # Use streaming based on request
    }

    try:
        if stream:
            # Handle streaming response
            def generate_response():
                response = requests.post(ollama_api_url, json=payload, stream=True, timeout=180)
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line.decode('utf-8'))
                            if 'response' in chunk_data:
                                # Send each chunk as Server-Sent Events
                                yield f"data: {json.dumps({'chunk': chunk_data['response']})}\n\n"
                            
                            # Check if this is the final chunk
                            if chunk_data.get('done', False):
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                        except json.JSONDecodeError:
                            continue
                            
            return Response(
                generate_response(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            # Handle non-streaming response (existing logic)
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


def handle_image_chat(user_message, images, stream=False):
    """Handle image chat using LLaVA or OpenAI GPT-4 Vision"""
    
    # First, try to use LLaVA with Ollama for local processing
    try:
        return handle_image_chat_with_llava(user_message, images, stream)
    except Exception as llava_error:
        print(f"LLaVA failed: {llava_error}. Trying OpenAI GPT-4 Vision...", flush=True)
        
        # Fallback to OpenAI GPT-4 Vision if available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                return handle_image_chat_with_openai(user_message, images, openai_api_key, stream)
            except Exception as openai_error:
                print(f"OpenAI GPT-4 Vision failed: {openai_error}", flush=True)
        
        # If both fail, return error message
        return jsonify({
            "error": "Image analysis is not available. Please install LLaVA model in Ollama or configure OpenAI API key."
        }), 503


def handle_image_chat_with_llava(user_message, images, stream=False):
    """Handle image chat using LLaVA model via Ollama"""
    ollama_api_url = "http://localhost:11434/api/generate"
    
    # Try different LLaVA models that might be available
    llava_models = ["llava:latest", "llava:13b", "llava:7b", "llava-llama3:latest"]
    
    for model_name in llava_models:
        try:
            # Convert first base64 image to the format LLaVA expects
            if images:
                # Remove data:image/xxx;base64, prefix if present
                image_data = images[0]
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                prompt = user_message if user_message else "What do you see in this image? Please describe it in detail."
                
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "images": [image_data],  # LLaVA expects base64 without prefix
                    "stream": stream
                }
                
                print(f"Trying LLaVA model: {model_name}", flush=True)
                
                if stream:
                    # Handle streaming for vision models
                    from flask import Response
                    import json
                    
                    def generate_vision_response():
                        response = requests.post(ollama_api_url, json=payload, stream=True, timeout=300)
                        response.raise_for_status()
                        
                        for line in response.iter_lines():
                            if line:
                                try:
                                    chunk_data = json.loads(line.decode('utf-8'))
                                    if 'response' in chunk_data:
                                        yield f"data: {json.dumps({'chunk': chunk_data['response']})}\n\n"
                                    
                                    if chunk_data.get('done', False):
                                        yield f"data: {json.dumps({'done': True})}\n\n"
                                        break
                                except json.JSONDecodeError:
                                    continue
                                    
                    return Response(
                        generate_vision_response(),
                        mimetype='text/plain',
                        headers={
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'Access-Control-Allow-Origin': '*'
                        }
                    )
                else:
                    response = requests.post(ollama_api_url, json=payload, timeout=300)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        ai_reply = response_data.get("response")
                        
                        if ai_reply:
                            print(f"Successfully got vision reply from {model_name}.", flush=True)
                            return jsonify({"reply": ai_reply.strip()})
                        
        except Exception as e:
            print(f"Failed to use {model_name}: {e}", flush=True)
            continue
    
    # If no LLaVA model worked, raise exception to try OpenAI
    raise Exception("No LLaVA model available")


def handle_image_chat_with_openai(user_message, images, api_key, stream=False):
    """Handle image chat using OpenAI GPT-4 Vision"""
    from openai import OpenAI
    
    # Configure OpenAI client with the new v1 API
    client = OpenAI(api_key=api_key)
    
    # Prepare the messages for OpenAI API
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_message if user_message else "What do you see in this image? Please describe it in detail."
                }
            ]
        }
    ]
    
    # Add images to the message
    for image_data in images[:4]:  # GPT-4 Vision supports up to 4 images
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": image_data,  # GPT-4 Vision expects full data URL
                "detail": "high"
            }
        })
    
    try:
        if stream:
            # Handle streaming for OpenAI
            from flask import Response
            import json
            
            def generate_openai_response():
                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=messages,
                    max_tokens=1000,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'chunk': content})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                        
            return Response(
                generate_openai_response(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000
            )
            
            ai_reply = response.choices[0].message.content
            if ai_reply:
                print("Successfully got vision reply from OpenAI GPT-4 Vision.", flush=True)
                return jsonify({"reply": ai_reply.strip()})
            else:
                return jsonify({"error": "OpenAI returned an empty response."}), 500
            
    except Exception as e:
        print(f"OpenAI GPT-4 Vision request failed: {e}", flush=True)
        raise e


@app.route('/api/summarize', methods=['POST'])
def summarize_video_endpoint():
    return handle_transcript_processing(request, is_detailed_explanation=False)


@app.route('/api/explain', methods=['POST'])
def explain_video_endpoint():
    return handle_transcript_processing(request, is_detailed_explanation=True)


def handle_transcript_processing(current_request, is_detailed_explanation):
    data = current_request.get_json()
    youtube_url = data.get('youtube_url')

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        video_id = None
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
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=['en-US', 'en-GB', 'en'])
            except Exception as lang_error:
                print(
                    f"Alternative language transcript fetch error: {lang_error}")
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
            return jsonify({"error": f"Failed to get {action} using all available methods."}), 500

    except NoTranscriptFound:
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
