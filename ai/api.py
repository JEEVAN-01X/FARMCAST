from flask import Flask, request, jsonify
from diagnose import diagnose
from farmcast import transcribe, extract_crop
from mandi import get_mandi_price, format_price_summary
import os, tempfile

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "farmcast-ai"})

@app.route("/diagnose/text", methods=["POST"])
def diagnose_text():
    data = request.json
    symptom = data.get("symptom", "")
    crop = data.get("crop", None)
    if not symptom:
        return jsonify({"error": "symptom required"}), 400
    result = diagnose(symptom, crop=crop)
    return jsonify(result)

@app.route("/diagnose/audio", methods=["POST"])
def diagnose_audio():
    if "audio" not in request.files:
        return jsonify({"error": "audio file required"}), 400
    audio = request.files["audio"]
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio.save(tmp.name)
        transcript = transcribe(tmp.name)
        os.unlink(tmp.name)
    crop = extract_crop(transcript)
    result = diagnose(transcript, crop=crop)
    result["transcript"] = transcript
    result["detected_crop"] = crop
    return jsonify(result)

@app.route("/mandi/price", methods=["GET"])
def mandi_price():
    commodity = request.args.get("commodity", "")
    state = request.args.get("state", "Karnataka")
    if not commodity:
        return jsonify({"error": "commodity required"}), 400
    limit = int(request.args.get("limit", 10))
    prices = get_mandi_price(commodity, state, limit=limit)
    if not prices:
        return jsonify({"error": "no data found", "commodity": commodity, "state": state}), 404
    return jsonify({"commodity": commodity, "state": state, "count": len(prices), "prices": prices})

@app.route("/mandi/summary", methods=["GET"])
def mandi_summary():
    commodity = request.args.get("commodity", "")
    state = request.args.get("state", "Karnataka")
    if not commodity:
        return jsonify({"error": "commodity required"}), 400
    return jsonify({"summary": format_price_summary(commodity, state)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
