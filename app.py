"""
Whisper Service - GPU-accelerated speech-to-text API
Uses faster-whisper with large-v3 model
"""

import os
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# Initialize FastAPI app
app = FastAPI(
    title="Whisper Service",
    description="GPU-accelerated speech-to-text API",
    version="1.0.0"
)

# Global model instance (loaded once at startup)
model: WhisperModel = None

# Supported audio formats
SUPPORTED_FORMATS = {".webm", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".mpeg", ".mpga", ".oga", ".opus"}


@app.on_event("startup")
async def load_model():
    """Load the Whisper model at startup."""
    global model
    
    # Check for CUDA availability
    import torch
    if torch.cuda.is_available():
        device = "cuda"
        compute_type = "float16"  # Best for GPU
        print(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        compute_type = "int8"  # Efficient for CPU
        print("⚠️ CUDA not available, using CPU")
    
    print("📥 Loading large-v3 model...")
    start = time.time()
    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    print(f"✅ Model loaded in {time.time() - start:.1f}s")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import torch
    return {
        "status": "ok",
        "model": "large-v3",
        "gpu": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe an audio file.
    
    - **audio**: Audio file (webm, mp3, wav, m4a, ogg, flac)
    
    Returns transcribed text, detected language, and duration.
    """
    global model
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate file extension
    filename = audio.filename or "audio.webm"
    ext = Path(filename).suffix.lower()
    
    # Handle .oga as .ogg (common for opus in ogg container)
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported format: {ext}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )
    
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Transcribe with auto language detection
        start = time.time()
        segments, info = model.transcribe(
            tmp_path,
            beam_size=5,
            language=None,  # Auto-detect
            vad_filter=True,  # Filter out silence
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Collect all segments
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())
        
        full_text = " ".join(text_parts)
        duration = time.time() - start
        
        return {
            "text": full_text,
            "language": info.language,
            "duration": round(info.duration, 2),
            "transcription_time": round(duration, 2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "Whisper Service",
        "version": "1.0.0",
        "endpoints": {
            "/transcribe": "POST - Transcribe audio file",
            "/health": "GET - Health check"
        }
    }
