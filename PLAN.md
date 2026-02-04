# Whisper Service — Project Plan

> GPU-accelerated speech-to-text API for Sage Control

---

## Overview

A dockerized Whisper transcription service running on TrueNAS with RTX 3090 GPU acceleration. Provides a simple REST API for Sage Control to transcribe voice recordings.

## Architecture

```
┌─────────────────┐                    ┌─────────────────────────┐
│  Sage Control   │  ───── HTTP ─────▶ │  Whisper Service (NAS)  │
│  (Browser)      │                    │  faster-whisper + 3090  │
│                 │  ◀──── JSON ────── │  large-v3 model         │
└─────────────────┘                    └─────────────────────────┘
        │
        ▼
   Transcript inserted
   into chat (auto-send
   or manual, per setting)
```

## Decisions

| Decision | Choice |
|----------|--------|
| Whisper engine | faster-whisper (CTranslate2) |
| Model | large-v3 (baked into image) |
| Language | Auto-detect (Spanish/English) |
| Port | 5555 |
| GPU | NVIDIA RTX 3090 via nvidia-container-toolkit |

## API Specification

### POST /transcribe

Transcribes an audio file.

**Request:**
```
Content-Type: multipart/form-data
Body: audio file (field name: "audio")
Supported formats: webm, mp3, wav, m4a, ogg, flac
```

**Response 200:**
```json
{
  "text": "transcribed text here",
  "language": "es",
  "duration": 4.2
}
```

**Response 503:**
```json
{
  "error": "Transcription service unavailable"
}
```

### GET /health

Health check endpoint.

**Response 200:**
```json
{
  "status": "ok",
  "model": "large-v3",
  "gpu": true
}
```

## Deployment

```bash
# On TrueNAS
git clone git@github.com:sage-ai-openclaw/whisper-service.git
cd whisper-service
docker compose up -d --build
```

First build downloads large-v3 model (~3GB) and takes several minutes.

## Network

- Runs on TrueNAS (truenas-scale / 100.105.233.10)
- Port 5555, Tailscale-only access
- No authentication (Tailscale network is trusted)

---

*Created: February 4, 2026*
