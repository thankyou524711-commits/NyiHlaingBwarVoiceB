import os
import asyncio
import edge_tts
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NyiHlaingBwarVoice</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        .container { max-width: 500px; margin: auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 140px; margin-bottom: 5px; padding: 10px; box-sizing: border-box; }
        select { width: 100%; padding: 10px; margin-bottom: 10px; }
        label { font-weight: bold; display: block; margin-top: 10px; }
        .char-count { font-size: 13px; color: #666; text-align: right; margin-bottom: 10px; }
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
            <label for="voice">အသံအမျိုးအစား ရွေးပါ:</label>
            <select name="voice" id="voice">
                <option value="my-MM-NilarNeural">Burmese (မြန်မာ - Nilar)</option>
                <option value="my-MM-ThihaNeural">Burmese (မြန်မာ - Thiha)</option>
                <option value="en-US-AvaNeural">English (US - Ava)</option>
                <option value="en-US-AndrewNeural">English (US - Andrew)</option>
            </select>

            <label for="rate">အသံနှုန်း (Speed):</label>
            <select name="rate" id="rate">
                <option value="-25%">-25% (အနှေး)</option>
                <option value="+0%" selected>0% (မဂ္ဂဇင်း/ပုံမှန်)</option>
                <option value="+10%">+10% (အနည်းငယ်မြန်)</option>
                <option value="+20%">+20% (မြန်)</option>
                <option value="+30%">+30% (အလွန်မြန်)</option>
            </select>

            <label for="pitch">အသံ အနိမ့်အမြင့် (Pitch):</label>
            <select name="pitch" id="pitch">
                <option value="-10Hz">အသံဩ/အနိမ့် (-10Hz)</option>
                <option value="+0Hz" selected>ပုံမှန် (+0Hz)</option>
                <option value="+10Hz">အသံစိမ်း/အမြင့် (+10Hz)</option>
            </select>

            <label for="text">စာသား ရိုက်ထည့်ပါ:</label>
            <textarea name="text" id="text" maxlength="15000" placeholder="ဒီမှာ စာသားရိုက်ထည့်ပါ (အများဆုံး စာလုံး ၁၅,၀၀၀ အထိ)..." oninput="updateCount()" required></textarea>
            <div class="char-count">စာလုံးအရေအတွက်: <span id="count">0</span> / 15,000</div>

            <button type="submit">Audio ဖိုင်ထုတ်မည်</button>
        </form>

        {% if audio_generated %}
            <h3>အသံဖိုင် နားထောင်ရန်:</h3>
            <audio controls autoplay>
                <source src="/get-audio" type="audio/mpeg">
            </audio>
        {% endif %}
    </div>

    <script>
        function updateCount() {
            const textarea = document.getElementById('text');
            const countDisplay = document.getElementById('count');
            const currentLength = textarea.value.length;
            countDisplay.innerText = currentLength;
            
            if (currentLength >= 15000) {
                countDisplay.classList.add('limit-warning');
            } else {
                countDisplay.classList.remove('limit-warning');
            }
        }
    </script>
</body>
</html>
"""

async def generate_speech(text, voice_name, rate, pitch, output_file="output.mp3"):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
    await communicate.save(output_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    audio_generated = False
    if request.method == 'POST':
        text = request.form.get('text')
        voice = request.form.get('voice', 'my-MM-NilarNeural')
        rate = request.form.get('rate', '+0%')
        pitch = request.form.get('pitch', '+0Hz')
        if text:
            if len(text) > 15000:
                text = text[:15000]
            asyncio.run(generate_speech(text, voice, rate, pitch, "output.mp3"))
            audio_generated = True
    return render_template_string(HTML_TEMPLATE, audio_generated=audio_generated)

@app.route('/get-audio')
def get_audio():
    if os.path.exists("output.mp3"):
        return send_file("output.mp3", mimetype="audio/mpeg")
    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
