# External Coqui TTS Server for MoodNest

This server provides real Coqui neural TTS voices for MoodNest when deployed externally.

## Quick Deploy Options

### Option 1: Railway (Recommended)
1. Fork this folder to a new GitHub repo
2. Connect Railway to your repo
3. Railway will auto-detect the Dockerfile and deploy
4. Get your URL from Railway dashboard

### Option 2: Google Cloud Run
```bash
gcloud run deploy coqui-tts \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

### Option 3: Local + ngrok
```bash
# Install and run locally
pip install -r requirements.txt
python server.py

# In another terminal
ngrok http 5500
```

## Connect to Replit

1. Copy your server URL (e.g., `https://your-app.railway.app`)
2. In Replit, add environment variable:
   ```
   EXTERNAL_COQUI_URL=https://your-app.railway.app
   ```
3. Restart your Replit app

## Testing

Test your server:
```bash
curl "https://your-server.com/health"
curl "https://your-server.com/speak?text=Hello&voice=ljspeech" -o test.wav
```

## Available Voices

- `ljspeech` - Emma (Clear female voice)
- `vctk_p225` - Sarah (Warm female voice)  
- `vctk_p226` - David (Deep male voice)
- `vctk_p227` - Alex (Gentle male voice)

## Notes

- First request will be slow (~30s) as models download
- Models are cached after first use
- Each model is ~100-500MB
- Server needs ~4GB RAM for all voices