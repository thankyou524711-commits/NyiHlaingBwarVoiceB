import os
import asyncio
from flask import Flask, request, send_file
import edge_tts

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="my">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NyiHlaingBwarVoice</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }
        .container { max-width: 400px; margin: auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 140px; margin-bottom: 5px; padding: 10px; box-sizing: border-box; }
        select { width: 100%; padding: 10px; margin-bottom: 10px; }
        label { font-weight: bold; display: block; margin-top: 10px; }
        .char-count { font-size: 12px; color: #666; text-align: right; margin-bottom: 10px; }
        .limit-warning { color: red; font-weight: bold; }
        button { width: 100%; padding: 12px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
        button:hover { background-color: #0056b3; }
        audio { width: 100%; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>NyiHlaingBwarVoice</h2>
        <form method="POST">
            <label for="voice">အသံအမျိုးအစား ရွေးရန်:</label>
            <select name="voice" id="voice">
                <option value="my-MM-NilarNeural">မြန်မာ (Nilar - အမျိုးသမီး)</option>
                <option value="my-MM-ThihaNeural">မြန်မာ (Thiha - အမျိုးသား)</option>
                <option value="en-US-AvaNeural">English (US - Ava)</option>
                <option value="en-US-AndrewNeural">English (US - Andrew)</option>
            </select>

            <label for="rate">အသံအမြန်နှုန်း (Speed):</label>
            <select name="rate" id="rate">
                <option value="-25%">-25% (နှေး)</option>
                <option value="+0%" selected>+0% (ပုံမှန်)</option>
                <option value="+10%">+10% (မြန်)</option>
                <option value="+25%">+25% (ပိုမြန်)</option>
            </select>

            <label for="text">ပြောမည့်စာသားကို ထည့်ပါ:</label>
            <textarea name="text" id="text" placeholder="ဒီမှာ စာရိုက်ပါ..." oninput="updateCount()"></textarea>
            <div class="char-count" id="charCount">စာလုံးရေ: 0</div>

            <button type="submit">အသံထုတ်လုပ်ရန် (Generate)</button>
        </form>

        {% if audio_file %}
        <audio controls>
            <source src="{{ audio_file }}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        {% endif %}
    </div>

    <script>
        function updateCount() {
            const text = document.getElementById('text').value;
            const count = text.length;
            document.getElementById('charCount').innerText = "စာလုံးရေ: " + count;
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        text = request.form.get("text")
        voice = request.form.get("voice", "my-MM-NilarNeural")
        rate = request.form.get("rate", "+0%")
        
        if text:
            output_path = "output.mp3"
            async def generate():
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(output_path)
            
            asyncio.run(generate())
            audio_file = "/audio"

    return HTML_TEMPLATE.replace("{% if audio_file %}", "" if audio_file else "<!--").replace("{% endif %}", "" if audio_file else "-->").replace("{{ audio_file }}", "/audio" if audio_file else "")

@app.route("/audio")
def get_audio():
    if os.path.exists("output.mp3"):
        return send_file("output.mp3", mimetype="audio/mp3")
    return "No audio found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
