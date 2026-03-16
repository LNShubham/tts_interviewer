import asyncio
import edge_tts
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Interview-TTS")

app = FastAPI(title="AI Interviewer TTS Module")

# 2. Enable CORS (So the frontend can talk to the backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Request Model
class TTSRequest(BaseModel):
    text: str
    voice: str = "en-US-BrianNeural"

# 4. The API Endpoint for the Coordinator
@app.post("/tts")
async def text_to_speech_endpoint(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    logger.info(f"Generating speech for: {request.text[:50]}...")
    
    # Initialize edge-tts
    communicate = edge_tts.Communicate(request.text, request.voice)

    async def audio_generator():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(audio_generator(), media_type="audio/mpeg")

# 5. Serve the Frontend (Fixes the 0.0.0.0 / Invalid Address error)
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <body style='font-family:sans-serif; text-align:center; padding-top:50px;'>
                <h1>index.html not found!</h1>
                <p>Please ensure the index.html file is in the same folder as main.py</p>
            </body>
        </html>
        """

# 6. Run the Server
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="127.0.0.1", port=8000) # Use this for local testing
    uvicorn.run(app, host="0.0.0.0", port=8000)