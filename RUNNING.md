# Running FitFindr

Everything about how the starter works and how to use it.

---

## Before your first class

Setup happens **before class**. The [environment setup page](../pages/ide_setup)
has the per-operating-system commands and the exact versions.

**Same API key you set up in unit 1.** Nothing new to sign up for. There is one
new package — the MCP SDK, for unit 4 — and it installs with everything else.

From inside this repo after you've forked and cloned it:

**macOS / Linux**

```bash
python3.13 --version          # must print 3.13.x — see below if it doesn't
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your key into .env
python test.py
```

> **Use `python3.13`, not `python3`.** On a current Mac, `python3` is 3.14,
> and the venv it builds fails `test.py` ("The pinned packages do not support
> 3.14 yet"). If `python3.13` isn't found, install it with
> `brew install python@3.13` or `pyenv install 3.13.5`. With pyenv, the
> repo's `.python-version` file selects it automatically.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env         # then paste your key into .env
python test.py
```

**You're ready when `python test.py` passes.**

If it doesn't and you've made one honest attempt at the error, post the
**whole** output in the help channel.

> Activate the virtual environment every time you open a new terminal. You
> should see `(.venv)` at the start of your prompt.

---

## Your first five minutes

Start with the data. Your tools will only be as good as your understanding of
what they're reading, and ten minutes here saves an hour of confused debugging.

```bash
python app.py fields                    # what a listing and a wardrobe item hold
python app.py listings --full -n 6      # read six listings all the way through
python app.py examples                  # queries worth trying
python app.py ask 'vintage graphic tee under $30'
```

> **Quote your queries with single quotes**, on every operating system. In
> PowerShell, `"vintage graphic tee under $30"` in double quotes silently
> becomes `vintage graphic tee under ` — PowerShell reads `$30` as a variable
> and substitutes nothing. You get results with no price ceiling and no error
> saying so. Single quotes are literal in PowerShell, bash and zsh alike.

That last one runs the loop. All three tools are stubs, so it will tell you the
loop isn't built yet. **That's the correct starting position** — it runs, and it
does nothing.

---

## Every command

| Command | What it does |
|---|---|
| `python test.py` | Checks your environment. Run it whenever something feels off |
| `python app.py fields` | The fields a listing and a wardrobe item have — **Milestone 1** |
| `python app.py listings` | Browse the data. `--full` for whole records, `-n` for how many |
| `python app.py examples` | Queries worth trying, including one that matches nothing |
| `python app.py ask '...'` | Run the agent on one query — **single quotes** |
| `python app.py ask` | Keep asking until you press Enter on an empty line |
| `python agent.py` | Runs both example paths — one that matches, one that can't |
| `python mcp_server.py` | Starts your MCP server — **unit 4** |
| `python mcp_client.py` | Asks the server what it offers — **unit 4** |
| `python run_eval.py --label before` | Runs every scenario five times and writes the run log — **unit 4** |
| `python serve.py` | Serves the agent over HTTP instead of exiting — **unit 9** |

Useful flags on `ask`:

| Flag | What it does |
|---|---|
| `--trace` | Print the loop step by step, once you've added the trace calls |
| `--empty-wardrobe` | Run as a user with nothing saved — one of unit 4's failure modes |

---

## Which command goes with which milestone

### Unit 3 — the build

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Read the data, run the starter | `app.py fields`, `app.py listings --full`, `app.py ask` |
| 2 | Spec your three tools | README, **Tool Inventory** |
| 3 | Write your acceptance criteria | `criteria.md` |
| 4 | Build the three tools | `tools.py`, tested one at a time from a terminal |
| 5 | Wire the loop and the state | `agent.py::run_agent` |
| 6 | Write it up | README |

### Unit 4 — the test

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Move one tool onto MCP | `mcp_server.py`, then `mcp_client.call_tool` in `run_agent` |
| 2 | Break it on purpose, then trace it | `trace.py`, `app.py ask --trace` |
| 3 | Run your test | `scenarios.py`, then `run_eval.py --label before` |
| 4 | Call each criterion, diagnose the misses | README |
| 5 | Fix one thing and re-run | `run_eval.py --label after` |
| 6 | Say what's still broken | README |

---

## Running it hosted (Render)

**Live URL:** `https://ai201-fitfindr.onrender.com` (free tier: the first request after ~15 idle
minutes takes about a minute while it wakes up)

```bash
curl https://ai201-fitfindr.onrender.com/health
curl -X POST https://ai201-fitfindr.onrender.com/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
curl 'https://ai201-fitfindr.onrender.com/logs?n=10'          # read the run log back
```

### How it got there

A Render **Web Service** connected to this GitHub repo, branch `main`. Every
push to `main` redeploys it. Settings in the Render dashboard:

| Setting | Value | Why |
|---|---|---|
| Runtime | Python 3 | Version comes from `.python-version` (3.13.5). Not 3.14, which the pinned packages don't support |
| Build command | `pip install -r requirements.txt` | |
| Start command | `gunicorn serve:app --timeout 400` | Default sync worker, never `-k gevent` (it breaks every MCP call). `--timeout 400` because gunicorn kills a worker after 30s by default, and a run that's retrying a 503 can legitimately take minutes: 2 model calls × 5 attempts × 30s timeout, plus backoff |
| Instance type | Free | |
| Env var `GEMINI_API_KEY` | your key | Set in the dashboard, never committed |
| Env var `AI201_CACHE` | `0` | Every run is a real model call, so the logged tokens and latency are real costs |

Render sets `PORT` itself; gunicorn reads it.

### Routes

| Route | What it does |
|---|---|
| `POST /ask` | `{"query": "...", "wardrobe": {...}}`, wardrobe optional. Returns the session dict; check `error` first |
| `GET /health` | `{"status": "ok"}` if it's awake |
| `GET /logs?n=20` | The last `n` run records from `logs/runs.jsonl`, oldest first |

### The run log

Every `/ask` request appends one JSON line to `logs/runs.jsonl` and prints the
same line to stdout (so it's also in Render's **Logs** tab). Rejected requests,
stopped runs and crashes get a line too.

| Field | Meaning |
|---|---|
| `ts` | When the request finished |
| `query` | The input |
| `status` | `ok`, `stopped` (run ended early with an error message), `bad_request` (400), or `crash` (500) |
| `stopped_at` | The step that stopped it: `parse_query`, `search_listings`, `suggest_outfit` or `create_fit_card` |
| `item` | The listing id that was selected |
| `output` | The fit card, or null |
| `model_calls` | Model call attempts, retries included |
| `retries` | How many of those were retries after a 503/429/timeout |
| `prompt_tokens`, `output_tokens` | Tokens the service reported for this request |
| `latency_ms` | Wall-clock time for the whole request, including waiting for the lock |
| `error` | `session["error"]`, or the exception for a crash |

### Known limits

- **The log file is wiped on every redeploy and restart.** Render's free disk
  isn't persistent. Render's Logs tab keeps the stdout copy for a while
  longer. The entries pasted in the README were copied out of `/logs`.
- **One request at a time.** A second request waits for the first. This is on
  purpose, and the reasons are in `serve.py`.
- **The session request budget is per process** (300 model calls,
  `SESSION_REQUEST_BUDGET`). A server that stays up past ~150 runs would start
  failing with `QuotaGuard`, logged as `crash`. The free tier sleeps after 15
  idle minutes, and sleeping resets the count.

### Running the server on your own machine instead

After the setup at the top of this file:

```bash
python serve.py                                    # Flask dev server on :5000
# or exactly what Render runs:
PORT=5000 gunicorn serve:app --timeout 400 --bind 0.0.0.0:5000
```

Then use the same `curl` commands with `http://localhost:5000` in place of the
URL. The log lands in `logs/runs.jsonl` (gitignored).

---

## Where everything lives

| File | What it does |
|---|---|
| `config.py` | Every setting worth changing — **TEMPERATURE and the cache are at the top** |
| `tools.py` | Your three tools. **Stubs — you build these** |
| `agent.py` | The planning loop and the session. **Stub — you build this** |
| `generate.py` | The only thing that calls out to a service. Handles pacing and quota |
| `trace.py` | The trace helper, and the loop's stop condition |
| `app.py` | The command line |
| `serve.py` | The same agent over HTTP, for deploying — **unit 9** |
| `mcp_server.py` | Your MCP server — **unit 4, you register the tool** |
| `mcp_client.py` | Calling an MCP tool from your agent. Given to you |
| `scenarios.py` | What your test runs. **You fill this in** |
| `run_eval.py` | Runs the scenarios repeatedly and writes the run log |
| `criteria.md` | Your five acceptance criteria. **You fill this in** |
| `data/` | 40 listings and the wardrobe schema |
| `utils/data_loader.py` | Loading the data. Use this rather than reading the files yourself |
| `results/` | Run logs. **Commit these** — they're your evidence |

---

## The two settings people go looking for

Both are at the top of `config.py`, and the brief points at them by name.

If your fit cards come out **word-for-word identical** every time, it is one of:

- **`CACHE_ENABLED`** — while you build, identical prompts reuse the answer
  already received. That's deliberate; it makes debugging free. `run_eval.py`
  turns it off automatically.
- **`TEMPERATURE`** — at `0.0` the model gives you the same words every time.
  It ships at `0.9`.

---

## About rate limits

**This is the heaviest pair in the course for call volume.** Two of your three
tools call the model, so one agent run is several requests, and a few runs back
to back while debugging can cross the per-minute limit.

`generate.py` handles it:

- **It paces itself** and says when it's waiting. **A pause is the starter
  doing its job, not a bug.**
- **It reuses answers** to prompts already sent, while you build.
- **It stops** if a session makes an unreasonable number of calls, rather than
  draining your day's allowance. For an agent, that usually means a loop isn't
  ending — look for that before raising the number.
- **It counts your calls** and prints the total when you exit.

`config.MAX_ITERATIONS` is the loop's own stop condition. Your loop this unit
is short enough that you may never hit it. Keep it — a missing stop condition
is the most common architectural failure in production agents.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `The planning loop isn't built yet` | Correct, at the start. That's the TODO in `agent.py` |
| `No GEMINI_API_KEY found` | No `.env`, or the key wasn't pasted in. On Windows check it didn't save as `.env.txt` |
| A message saying the model couldn't be reached | Usually a bad key. This is also **exactly what unit 4 Milestone 2 asks you to trigger on purpose** |
| `[rate limit] ... Waiting 34s` | Working as intended. Leave it |
| `[serve] another request is still running` | Also working as intended. `serve.py` answers one request at a time; yours is queued behind one that's mid-run |
| `QuotaGuard: This session has made 300 requests` | A loop isn't ending. Find it before raising the budget |
| `The loop ran 11 times, past MAX_ITERATIONS` | Same thing, caught earlier |
| `The server doesn't offer a tool called '...'` | Nothing registered in `mcp_server.py` yet, or the name doesn't match |
| MCP returns a string where you expected a list | You're not going through `mcp_client.call_tool`, which unwraps it |
| Fit cards identical every run | `CACHE_ENABLED` or `TEMPERATURE`. See above |
| `--trace` prints nothing | You haven't added `trace.step()` calls yet — unit 4, Milestone 2 |
| `IncompleteFieldDefinitionWarning: Field 'lifespan'` | Harmless noise from the MCP library's dependencies. Not your code, not an error. Ignore it |
| A price ceiling you typed is being ignored | You used double quotes in PowerShell. `$30` vanished. Use single quotes |
| `UnicodeEncodeError: 'charmap' codec can't encode` | Shouldn't happen — `config.py` sets the console to UTF-8. If you see it, you're running a file that doesn't import `config` |

Still stuck after one honest attempt? Post in the help channel with the full
error, what you ran, and what you expected.

---

## A note on committing

At least four new commits in unit 3, at least four more in unit 4. Your commit
history is what shows your criteria existed before your results did.

**Do not delete and recreate this repository.** You submit the same URL both
units.

`results/` is deliberately **not** in `.gitignore`.
