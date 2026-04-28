"""
warm_cache.py — Jeevan runs this ONCE before the demo
Fires all 3 demo queries through the full pipeline and caches responses in Redis.
After this, demo responses come from cache (0ms) — the LLM is never called live.

Run from inside the FARMCAST/ai directory with venv active:
    python warm_cache.py

What it does:
  1. Transcribes each demo phrase (or uses hardcoded transcript to skip Whisper)
  2. Runs pipeline.run() for each scenario
  3. Calls tts.synthesise() on the Kannada response
  4. Stores both the JSON response and the MP3 bytes in Redis
  5. Verifies all 3 are cache hits
"""

import json
import sys
import redis
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("warm_cache")

# ── Make sure we can import from the ai/ directory ────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import run as pipeline_run
import tts as tts_module

# ── Redis connection ──────────────────────────────────────────────────────────
import os
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
    r.ping()
    log.info(f"Redis connected at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    log.error(f"Cannot connect to Redis: {e}")
    log.error("Make sure Redis is running:  redis-server")
    sys.exit(1)

# ── 3 Demo Scenarios ──────────────────────────────────────────────────────────
# Transcripts are hardcoded here so we don't need audio files to warm the cache.
# These match exactly what the farmers will say in the demo.
SCENARIOS = [
    {
        "name":       "Raju — Jowar disease (Haveri)",
        "dtmf":       "1",
        "transcript": "nanna jola bele mele bili chukke banthive haveri district alli",
        "cache_key":  "demo:scenario:disease",
    },
    {
        "name":       "Savitri — Cotton price query",
        "dtmf":       "2",
        "transcript": "cotton bele eshtu ide",
        "cache_key":  "demo:scenario:price",
    },
    {
        "name":       "Basavaraju — PM-KISAN scheme",
        "dtmf":       "3",
        "transcript": "PM kisan yojane nakku siguta ide 2 acre jowar ide",
        "cache_key":  "demo:scenario:scheme",
    },
]

# ── Run each scenario ─────────────────────────────────────────────────────────
def warm(scenario: dict) -> bool:
    name       = scenario["name"]
    dtmf       = scenario["dtmf"]
    transcript = scenario["transcript"]
    cache_key  = scenario["cache_key"]

    log.info(f"\n{'─'*60}")
    log.info(f"Warming: {name}")
    log.info(f"  DTMF: {dtmf}  |  transcript: {transcript}")

    # Run the AI pipeline
    try:
        result = pipeline_run(dtmf, transcript)
    except Exception as e:
        log.error(f"  pipeline.run() failed: {e}")
        return False

    if result.get("needs_retry"):
        log.warning(f"  Pipeline returned needs_retry=True for {name}.")
        log.warning(f"  Transcript may be missing required fields. Check scenario inputs.")
        return False

    log.info(f"  Intent:     {result.get('intent')}")
    log.info(f"  Confidence: {result.get('confidence')}")
    log.info(f"  Escalate:   {result.get('escalate')}")
    log.info(f"  Response:   {result.get('response_kannada', '')[:80]}…")

    # Synthesise the Kannada TTS audio
    kannada_text = result.get("response_kannada", "")
    if not kannada_text:
        log.warning(f"  No response_kannada in result — TTS skipped")
        mp3_bytes = None
    else:
        try:
            mp3_bytes = tts_module.synthesise(kannada_text)
            log.info(f"  TTS generated: {len(mp3_bytes)} bytes")
        except Exception as e:
            log.error(f"  TTS failed: {e}")
            mp3_bytes = None

    # Store in Redis (no expiry — demo responses are permanent)
    payload = {
        "result":   result,
        "has_audio": mp3_bytes is not None,
    }
    r.set(cache_key + ":json", json.dumps(payload, default=str))
    if mp3_bytes:
        r.set(cache_key + ":mp3", mp3_bytes)

    log.info(f"  Cached at:  {cache_key}:json  +  {cache_key}:mp3")
    return True


# ── Verify cache hits ─────────────────────────────────────────────────────────
def verify():
    log.info(f"\n{'═'*60}")
    log.info("Verifying cache hits…")
    all_ok = True
    for s in SCENARIOS:
        key_j = s["cache_key"] + ":json"
        key_m = s["cache_key"] + ":mp3"
        has_json  = r.exists(key_j)
        has_audio = r.exists(key_m)
        status = "✓" if (has_json and has_audio) else "✗ MISSING"
        log.info(f"  {status}  {s['name']}")
        log.info(f"         json={bool(has_json)}  mp3={bool(has_audio)}")
        if not has_json:
            all_ok = False
    return all_ok


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("KisanSathi demo cache warmup")
    log.info("="*60)

    results = []
    for scenario in SCENARIOS:
        ok = warm(scenario)
        results.append((scenario["name"], ok))

    passed = sum(1 for _, ok in results if ok)
    log.info(f"\n{'═'*60}")
    log.info(f"Warmed {passed}/{len(SCENARIOS)} scenarios")
    for name, ok in results:
        log.info(f"  {'✓' if ok else '✗'}  {name}")

    cache_ok = verify()

    if passed == len(SCENARIOS) and cache_ok:
        log.info("\n✓  All 3 demo scenarios cached. Demo is ready.")
        log.info("   Live calls will serve from cache — LLM never called on stage.")
    else:
        log.error("\n✗  Some scenarios failed. Check errors above before demo.")
        sys.exit(1)
