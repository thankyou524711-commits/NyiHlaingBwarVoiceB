import asyncio
import os
from flask import Flask, render_template_string, request, send_file
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
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; color: #333; }
        label { display: block; margin-top: 10px; font-weight: bold; color: #555; }
        select, textarea, button { width: 100%; margin-top: 5px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 120px; resize: vertical; }
        .char-count { text-align: right; font-size: 12px; color: #777; margin-top: 4px; }
        button { background-color: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; margin-top: 15px; }
        button:hover { background-color: #0056b3; }
        audio { width: 100%; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>NyiHlaingBwarVoice</h2>
        <form method="POST">
            <label>အသံအမျိုးအစား ရွေးရန်:</label>
            <select name="voice">
                <option value="my-MM-NilarNeural" {% if voice == 'my-MM-NilarNeural' %}selected{% endif %}>မြန်မာ (Nilar - အမျိုးသမီး)</option>
                <option value="my-MM-ThihaNeural" {% if voice == 'my-MM-ThihaNeural' %}selected{% endif %}>မြန်မာ (Thiha - အမျိုးသား)</option>
            </select>

            <label>အသံအမြန်နှုန်း (Speed):</label>
            <select name="rate">
                <option value="+0%" {% if rate == '+0%' %}selected{% endif %}>+0% (ပုံမှန်)</option>
                <option value="+10%" {% if rate == '+10%' %}selected{% endif %}>+10% (အနည်းငယ်မြန်)</option>
                <option value="-10%" {% if rate == '-10%' %}selected{% endif %}>-10% (အနည်းငယ်နှေး)</option>
            </select>

            <label>ပြောမည့် စာသားကို ထည့်ပါ:</label>
            <textarea name="text" id="text" placeholder="ဒီမှာ စာရိုက်ပါ..." oninput="updateCount()">{{ text if text else '' }}</textarea>
            <div class="char-count" id="charCount">စာလုံးရေ: 0 / 15000</div>

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
            document.getElementById('charCount').innerText = "စာလုံးရေ: " + count + " / 15000";
        }
        window.onload = function() {
            updateCount();
        };
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    text = ""
    voice = "my-MM-NilarNeural"
    rate = "+0%"
    
    if request.method == "POST":
        text = request.form.get("text", "")
        voice = request.form.get("voice", "my-MM-NilarNeural")
        rate = request.form.get("rate", "+0%")

        if text:
            output_path = "output.mp3"
            async def generate():
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(output_path)

            asyncio.run(generate())
            audio_file = "/audio"

    return render_template_string(HTML_TEMPLATE, audio_file=audio_file, text=text, voice=voice, rate=rate)

@app.route("/audio")
def audio():
    if os.path.exists("output.mp3"):
        return send_file("output.mp3", mimetype="audio/mp3")
    return "Audio not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
