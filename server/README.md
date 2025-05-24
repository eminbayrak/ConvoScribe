# ConvoScribe Flask Server

A Flask backend server for ConvoScribe that provides YouTube video transcript summarization and chat functionality using local LLM (Ollama with gemma3:latest model).

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- gemma3:latest model pulled in Ollama

## Setup Instructions

### 1. Install Ollama and Model

First, make sure you have Ollama installed and the required model:

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai/ for installation instructions

# Pull the gemma3:latest model
ollama pull gemma3:latest

# Start Ollama service (if not running)
ollama serve
```

### 2. Create Virtual Environment

Navigate to the server directory and create a virtual environment:

```powershell
# Navigate to server directory
cd c:\Users\ebyrock\projects\VidScribeAI\server

# Create virtual environment
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**

```cmd
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

With the virtual environment activated, install the required packages:

```powershell
pip install -r requirements.txt
```

### 5. Environment Configuration (Optional)

Create a `.env` file if you want to use cloud-based LLM APIs as fallback:

```powershell
# Copy the example file
copy .env.example .env

# Edit .env file and add your API keys if needed
notepad .env
```

### 6. Start the Flask Server

With the virtual environment activated and dependencies installed:

```powershell
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Chat Endpoint

- **URL:** `POST /api/chat`
- **Body:** `{"message": "Your message here"}`
- **Response:** `{"reply": "AI response"}`

### Summarize Video

- **URL:** `POST /api/summarize`
- **Body:** `{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}`
- **Response:** `{"summary": "Video summary"}`

### Explain Video

- **URL:** `POST /api/explain`
- **Body:** `{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}`
- **Response:** `{"explanation": "Detailed explanation"}`

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**

   - Ensure Ollama is running: `ollama serve`
   - Check if gemma3:latest model is available: `ollama list`

2. **Virtual Environment Issues**

   - If activation fails, try: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
   - Then retry the activation command

3. **YouTube Transcript Issues**

   - Some videos may have disabled transcripts
   - The server will return appropriate error messages for unavailable transcripts

4. **Python Path Issues**

   - Make sure you're using the Python from your virtual environment
   - Check with: `where python` (should point to venv directory)

5. **SvelteKit DevTools 404 Error**
   - Error message: `SvelteKitError: Not found: /.well-known/appspecific/com.chrome.devtools.json`
   - This is harmless - it's Chrome DevTools trying to access a non-existent endpoint
   - Your application will work normally despite this error
   - You can safely ignore this message

### Development Mode

The server runs in debug mode by default, which provides:

- Auto-reload on file changes
- Detailed error messages
- CORS enabled for frontend development

## Project Structure

```
server/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env              # Your environment variables (create this)
├── README.md         # This file
└── venv/             # Virtual environment (created after setup)
```

## Dependencies

- **Flask**: Web framework
- **flask-cors**: CORS support for frontend integration
- **python-dotenv**: Environment variable management
- **youtube-transcript-api**: YouTube transcript fetching
- **requests**: HTTP client for Ollama API communication

## Integration with Frontend

This server is designed to work with the Svelte frontend located in `../svelte-client/`. The server serves API endpoints that the frontend consumes for:

- Real-time chat with AI
- YouTube video summarization
- Detailed video explanations

Start both the Flask server (port 5000) and the Svelte dev server (port 5173) for full functionality.
