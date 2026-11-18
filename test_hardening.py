"""
Runs the five extension criteria in criteria.md and writes what happened to
results/hardening_run<N>_<part>.md.

    python test_hardening.py --run 1 --part local    criteria 1-4, injected failures
    python test_hardening.py --run 1 --part live     criterion 5, against Render

Criteria 1-2 swap the model client for a fake that returns 503s or empty text.
Criterion 3 points a real genai client at a local socket that accepts and never
answers, so the real request timeout has to fire. Criterion 4 sends bad input.
All four go through serve.py's /ask with Flask's test client.
"""

import argparse
import json
import os
import socket
import sys
import tempfile
import threading
import time
import urllib.request
from types import SimpleNamespace as NS

import config

TRIES = 5
# Criterion 3's limit. 180 s in Milestone 5; tightened to 75 s in Milestone 6.
C3_LIMIT_S = 75
LIVE_URL = "https://ai201-fitfindr.onrender.com"
QUERY = "vintage graphic tee under $30"


def fake_client(outcomes):
    """A stand-in for genai.Client: each call takes the next outcome."""
    it = iter(outcomes)

    def generate_content(**_):
        o = next(it)
        if isinstance(o, Exception):
            raise o
        return NS(text=o, usage_metadata=None)

    return NS(models=NS(generate_content=generate_content))


def hang_server() -> int:
    """A TCP server that accepts connections and never sends a byte."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen()
    held = []
    threading.Thread(target=lambda: [held.append(sock.accept()) for _ in iter(int, 1)],
                     daemon=True).start()
    return sock.getsockname()[1]


def run_local(out):
    os.environ["AI201_LOG_FILE"] = tempfile.mktemp(suffix=".jsonl")
    config.CACHE_ENABLED = False
    import generate
    import serve
    client = serve.app.test_client()
    real_time = generate.time

    def last_log():
        return json.loads(serve.LOG_FILE.read_text().splitlines()[-1])

    def ask(body, **kw):
        started = time.monotonic()
        r = client.post("/ask", json=body, **kw) if body is not None else \
            client.post("/ask", data="garbage", **kw)
        return r, time.monotonic() - started, last_log()

    def no_waiting(on):
        # Backoff and pacing sleeps skipped for injected failures: criteria 1-2
        # are about outcome, not time.
        generate.time = NS(sleep=lambda s: None, monotonic=real_time.monotonic) if on else real_time

    results = {}

    # 1. one 503, then success
    no_waiting(True)
    passes, evidence = 0, []
    for i in range(TRIES):
        generate._client = fake_client([Exception("503 UNAVAILABLE. high demand"),
                                        "Outfit: tee + jeans.", "A $18 tee on depop. So good."])
        r, _, log = ask({"query": QUERY})
        ok = r.status_code == 200 and bool(r.get_json()["fit_card"]) and log["retries"] >= 1
        passes += ok
        evidence.append((ok, log))
    results[1] = (passes, TRIES, evidence)

    # 2. every attempt fails: 503 x5, and an empty response
    for label, outcomes, tool in [
        ("503 on all attempts", [Exception("503 UNAVAILABLE")] * config.MAX_RETRIES, "suggest_outfit"),
        ("empty response", ["Outfit: tee + jeans.", ""], "create_fit_card"),
    ]:
        passes, evidence = 0, []
        for i in range(TRIES):
            generate._client = fake_client(outcomes)
            r, _, log = ask({"query": QUERY})
            s = r.get_json()
            ok = (r.status_code == 200 and bool(s["error"]) and s["stopped_at"] == tool
                  and log["status"] == "stopped")
            passes += ok
            evidence.append((ok, log))
        results[f"2 ({label})"] = (passes, TRIES, evidence)
    no_waiting(False)

    # 3. hung model call, real client, real timeout, real backoff
    from google import genai
    from google.genai import types
    port = hang_server()
    passes, evidence = 0, []
    for i in range(TRIES):
        generate._client = genai.Client(api_key="test", http_options=types.HttpOptions(
            base_url=f"http://127.0.0.1:{port}", timeout=config.REQUEST_TIMEOUT_S * 1000))
        generate._call_times.clear()
        r, secs, log = ask({"query": QUERY})
        s = r.get_json()
        ok = r.status_code == 200 and bool(s.get("error")) and secs < C3_LIMIT_S
        passes += ok
        evidence.append((ok, {**log, "client_seconds": round(secs, 1)}))
        print(f"  c3 try {i + 1}: {secs:.1f}s {ok}", flush=True)
    results[3] = (passes, TRIES, evidence)

    # 4. bad input: rejected, 0 model calls, logged
    generate._client = fake_client([])  # any model call would raise StopIteration
    passes, evidence = 0, []
    for body in [{"query": ""}, {"query": "   "}, {"query": "under $30"}, None]:
        lines_before = len(serve.LOG_FILE.read_text().splitlines())
        r, _, log = ask(body)
        logged = len(serve.LOG_FILE.read_text().splitlines()) == lines_before + 1
        rejected = r.status_code == 400 or r.get_json().get("stopped_at") == "parse_query"
        ok = rejected and logged and (log.get("model_calls") or 0) == 0
        passes += ok
        evidence.append((ok, {"http": r.status_code, **log}))
    results[4] = (passes, 4, evidence)

    write(out, results)


def http(method, path, body=None):
    data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
    req = urllib.request.Request(LIVE_URL + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=450) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def run_live(out):
    http("GET", "/health")  # wake it up if it's asleep
    before = len(http("GET", "/logs?n=100000")[1])
    matching = ["vintage graphic tee under $30", "baggy jeans size W30 under $50",
                "black combat boots", "cottagecore dress under $40", "denim jacket size M",
                "sneakers size US 9 under $80", "oversized hoodie under $35", "leather belt",
                "y2k mini skirt size S", "cargo pants under $30"]
    failing = [{"query": ""}, {"query": "   "}, {"query": "under $30"}, b"garbage",
               {"query": "designer ballgown size XXS under $5"}, {"query": "tuxedo size XXXL"},
               {"nope": 1}, {"query": "$5"}, {"query": "space suit under $1"}, b"[1,2"]
    for q in matching:
        http("POST", "/ask", {"query": q})
    for body in failing:
        http("POST", "/ask", body)
    records = http("GET", "/logs?n=100000")[1][before:]
    evidence, passes = [], 0
    for rec in records:
        ok = all(k in rec for k in ("ts", "query", "status", "latency_ms", "error"))
        if rec.get("status") == "ok":
            ok = ok and bool(rec.get("output")) and rec.get("prompt_tokens", 0) > 0
        passes += ok
        evidence.append((ok, rec))
    note = f"{len(records)} new records for 20 requests"
    if len(records) != 20:
        passes = min(passes, len(records)) - abs(20 - len(records))
    write(out, {5: (passes, 20, evidence)}, note)


def write(out, results, note=""):
    lines = []
    for crit, (passes, total, evidence) in results.items():
        lines.append(f"## Criterion {crit}: {passes}/{total}\n")
        lines.append("```")
        lines += [("PASS " if ok else "FAIL ") + json.dumps(e, ensure_ascii=False) for ok, e in evidence]
        lines.append("```\n")
    if note:
        lines.append(note + "\n")
    text = "\n".join(lines)
    out.write_text(text)
    print(text)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--part", choices=["local", "live"], required=True)
    a = p.parse_args()
    out = config.RESULTS_DIR / f"hardening_run{a.run}_{a.part}.md"
    (run_local if a.part == "local" else run_live)(out)
    print(f"wrote {out}", file=sys.stderr)
