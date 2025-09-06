# Static Files Directory

This directory contains static files and test data for the Voice AI Bot Backend.

## Contents

- Sample audio files for testing transcription endpoints
- Test data for unit tests
- Documentation assets

## Usage

Place audio files (.mp3, .wav, .m4a, .webm) here for testing the `/transcribe` endpoint.

Example:
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "x-api-key: fast_API_KEY" \
  -F "file=@static/sample_audio.mp3"
```
