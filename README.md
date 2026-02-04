# Whisper Service

GPU-accelerated speech-to-text API using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with the `large-v3` model.

## Installation on TrueNAS Scale

### Option A: Custom App (Recommended)

1. Go to **Apps** → **Discover Apps** → **Custom App**
2. Fill in the form:

| Field | Value |
|-------|-------|
| **Application Name** | `whisper-service` |
| **Image Repository** | `ghcr.io/sage-ai-openclaw/whisper-service` |
| **Image Tag** | `latest` |

3. Under **Container Settings**:
   - No extra environment variables needed

4. Under **Networking**:
   - Add port: **Host Port** `5555` → **Container Port** `5555` (TCP)

5. Under **Resources Configuration** → **GPU Configuration**:
   - Enable **Passthrough available (non-NVIDIA) GPUs**
   - Or if NVIDIA option shows: Select your **RTX 3090**

6. Click **Install**

First start takes 1-2 minutes (model loading). Check logs in the Apps UI.

### Option B: Docker Compose (CLI)

```bash
git clone https://github.com/sage-ai-openclaw/whisper-service.git
cd whisper-service
docker compose up -d --build
```

---

## Features

- 🚀 GPU acceleration (NVIDIA CUDA)
- 🎯 High accuracy with large-v3 model
- 🌍 Auto language detection (Spanish/English)
- 📦 Model baked into Docker image
- ⚡ ~4x faster than OpenAI's original Whisper

## Requirements

- Docker with NVIDIA Container Toolkit
- NVIDIA GPU with CUDA support (tested on RTX 3090)
- ~10GB disk space (CUDA runtime + model)

## Quick Start

```bash
# Clone the repository
git clone git@github.com:sage-ai-openclaw/whisper-service.git
cd whisper-service

# Build and run (first build downloads model, takes ~5-10 min)
docker compose up -d --build

# Check logs
docker compose logs -f

# Test health endpoint
curl http://localhost:5555/health
```

## API Usage

### Transcribe Audio

```bash
curl -X POST http://localhost:5555/transcribe \
  -F "audio=@recording.webm"
```

**Response:**
```json
{
  "text": "Hello, this is a test recording.",
  "language": "en",
  "duration": 3.45,
  "transcription_time": 0.82
}
```

### Health Check

```bash
curl http://localhost:5555/health
```

**Response:**
```json
{
  "status": "ok",
  "model": "large-v3",
  "gpu": true,
  "gpu_name": "NVIDIA GeForce RTX 3090"
}
```

## Supported Formats

- webm (default from browsers)
- mp3
- wav
- m4a
- ogg/oga
- flac
- opus

## Configuration

The service runs on port `5555` by default. To change, edit `docker-compose.yml`:

```yaml
ports:
  - "YOUR_PORT:5555"
```

## Network Access

This service is designed for internal/Tailscale network access only. No authentication is implemented since it runs on a trusted network.

For Sage Control integration, ensure both services are on the same Tailscale network.

## Updating

```bash
git pull
docker compose up -d --build
```

## Troubleshooting

### GPU not detected
```bash
# Verify NVIDIA Container Toolkit is installed
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

### Model loading slow
First startup loads the model into GPU memory. Subsequent requests are fast. Check logs with `docker compose logs -f`.

### Out of memory
The large-v3 model needs ~3GB VRAM. Ensure no other GPU-intensive processes are running.

---

Built for [Sage Control](https://github.com/sage-ai-openclaw/sage-control) voice input feature.
