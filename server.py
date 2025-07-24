#!/usr/bin/env python3
"""
External Coqui TTS Server
Deploy this on Railway, Google Cloud Run, or your own server
to provide real Coqui neural voices to your Replit app
"""

from flask import Flask, request, send_file, jsonify
import os
import tempfile
import logging
import uuid

# Try importing TTS, fallback to basic mode if not available
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logging.warning("TTS not available, running in fallback mode")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize models cache
models = {}

# Available Coqui models
VOICE_MODELS = {
    "ljspeech": {
        "model": "tts_models/en/ljspeech/tacotron2-DDC",
        "name": "Emma (Clear)",
        "gender": "female"
    },
    "vctk_p225": {
        "model": "tts_models/en/vctk/vits",
        "speaker": "p225",
        "name": "Sarah (Warm)", 
        "gender": "female"
    },
    "vctk_p226": {
        "model": "tts_models/en/vctk/vits",
        "speaker": "p226",
        "name": "David (Deep)",
        "gender": "male"
    },
    "vctk_p227": {
        "model": "tts_models/en/vctk/vits",
        "speaker": "p227",
        "name": "Alex (Gentle)",
        "gender": "male"
    }
}

def get_or_load_model(voice_id):
    """Load and cache TTS model"""
    if voice_id not in models:
        voice_config = VOICE_MODELS.get(voice_id, VOICE_MODELS["ljspeech"])
        model_name = voice_config["model"]
        
        logging.info(f"Loading model: {model_name}")
        models[voice_id] = TTS(model_name, gpu=False)
        logging.info(f"Model loaded successfully: {voice_id}")
    
    return models[voice_id], VOICE_MODELS.get(voice_id, VOICE_MODELS["ljspeech"])

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Coqui TTS Server Running",
        "models_loaded": len(models),
        "available_voices": list(VOICE_MODELS.keys())
    })

@app.route("/speak")
def speak():
    """Generate speech using Coqui TTS"""
    try:
        text = request.args.get("text", "Hello, this is a test of Coqui text to speech.")
        voice = request.args.get("voice", "ljspeech")
        
        # Clean up voice ID if it has prefix
        voice = voice.replace("coqui_", "").replace("vctk_", "")
        if voice.startswith("p"):
            voice = f"vctk_{voice}"
        
        # Get model and config
        tts_model, voice_config = get_or_load_model(voice)
        
        # Generate unique filename
        filename = f"speech_{uuid.uuid4().hex}.wav"
        output_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Generate speech
        if "speaker" in voice_config:
            # Multi-speaker model
            tts_model.tts_to_file(
                text=text,
                speaker=voice_config["speaker"],
                file_path=output_path
            )
        else:
            # Single speaker model
            tts_model.tts_to_file(
                text=text,
                file_path=output_path
            )
        
        # Return audio file
        return send_file(
            output_path,
            mimetype="audio/wav",
            as_attachment=False,
            download_name=f"speech_{voice}.wav"
        )
        
    except Exception as e:
        logging.error(f"TTS generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/voices")
def voices():
    """List available voices"""
    voice_list = []
    for voice_id, config in VOICE_MODELS.items():
        voice_list.append({
            "id": f"coqui_{voice_id}",
            "name": config["name"],
            "gender": config["gender"],
            "model": config["model"]
        })
    
    return jsonify({
        "voices": voice_list,
        "engine": "Coqui TTS Neural Models"
    })

if __name__ == "__main__":
    # Pre-load Emma voice for faster first request
    logging.info("Pre-loading default voice model...")
    get_or_load_model("ljspeech")
    
    # Start server
    port = int(os.environ.get("PORT", 5500))
    app.run(host="0.0.0.0", port=port, debug=False)