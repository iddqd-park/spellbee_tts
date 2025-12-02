import csv
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# API Key: Get from https://elevenlabs.io/
# You can set this as an environment variable or paste it here directly.
API_KEY = os.environ.get("ELEVENLABS_API_KEY") 

# You can find more voice IDs in the ElevenLabs API documentation or your VoiceLab.
VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17" 

INPUT_CSV_FILE = 'data.csv'
OUTPUT_DIR = 'tts'

# ElevenLabs API Endpoint
TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

def generate_tts(text, output_filename):
    """
    Generates TTS for the given text and saves it to the output filename.
    """
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(TTS_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved: {output_filename}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    if not API_KEY:
        print("⚠️  Please set your ElevenLabs API Key in the .env file or environment variable 'ELEVENLABS_API_KEY'.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📂 Created directory: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_CSV_FILE):
        print(f"❌ Error: '{INPUT_CSV_FILE}' not found.")
        return

    print(f"🚀 Starting TTS generation from '{INPUT_CSV_FILE}'...")

    with open(INPUT_CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Skip header if it exists
        header = next(reader, None)
        if header and header[0].strip().lower() != 'number':
             pass

        for row in reader:
            if not row or len(row) < 4:
                continue

            # CSV Columns: Number, Word, Part of Speech, Definition, Alternative
            file_id = row[0].strip()
            word = row[1].strip()
            definition = row[3].strip()
            alternative = row[4].strip() if len(row) > 4 else ""

            if not file_id.isdigit():
                continue

            # 1. Generate TTS for Word -> {Number}_word.mp3
            filename_word = os.path.join(OUTPUT_DIR, f"{file_id}_word.mp3")
            if not os.path.exists(filename_word):
                print(f"Processing {file_id}_word: {word}")
                if generate_tts(word, filename_word):
                    time.sleep(0.2)
            else:
                print(f"Skipping {file_id}_word (already exists)")

            # 2. Generate TTS for Definition -> {Number}_def.mp3
            filename_def = os.path.join(OUTPUT_DIR, f"{file_id}_def.mp3")
            if not os.path.exists(filename_def):
                print(f"Processing {file_id}_def: {definition}")
                if generate_tts(definition, filename_def):
                    time.sleep(0.2)
            else:
                print(f"Skipping {file_id}_def (already exists)")

            # 3. Generate TTS for Alternative -> {Number}_alt.mp3 (if exists)
            if alternative:
                filename_alt = os.path.join(OUTPUT_DIR, f"{file_id}_alt.mp3")
                if not os.path.exists(filename_alt):
                    print(f"Processing {file_id}_alt: {alternative}")
                    if generate_tts(alternative, filename_alt):
                        time.sleep(0.2)
                else:
                    print(f"Skipping {file_id}_alt (already exists)")

    print("🎉 All done!")

if __name__ == "__main__":
    main()