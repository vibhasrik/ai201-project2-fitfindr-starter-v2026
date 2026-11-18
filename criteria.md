# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

My search is a plain keyword match, so a query worded differently from the
listings (say "cargo pants" when the listing says "utility trousers") can come
back empty even when a good item exists. 4 of 5 allows for one phrasing miss
like that; a crash or a missing fit card on a query that did match still counts
as a fail.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

This path has no model and no ranking in it: an empty list either triggers the
branch in `run_agent` or it doesn't. That's deterministic code, so anything
less than 5 of 5 means the branch is broken, not unlucky.

---

## 3. The searched item is the item every tool receives

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

In 5 of 5 tries, the `id` of `session["selected_item"]` is the same as the `id`
of `session["search_results"][0]`, and the same `id` appears in the trace
inputs of both `suggest_outfit` and `create_fit_card`.

**Why this target:**

Passing one dict through the session is plain code with no model involved, so
it should never drift. Comparing `id`s rather than titles makes it a yes/no
check: two listings can share a word in the title, but never an `id`.



---

## 4. The fit card states the right facts

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

For 5 different items, at least 4 of the 5 fit cards are 2 to 4 sentences long
and mention the item's exact price (e.g. `$18`) and its platform (e.g.
`depop`). None of the 5 may mention a brand when the listing's `brand` is None.

**Why this target:**

The wording is supposed to change between runs, so I'm checking facts, not
words. 4 of 5 because the model at temperature 0.9 sometimes rounds or drops
the price, and that's worth catching without failing the whole criterion. The
brand rule is 5 of 5 because a made-up brand is an invented fact, and most
listings have no brand.



---

## 5. Search respects size and price

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

For 5 searches with a size and a max price set, every returned listing is at or
under the max price and has the requested size as a whole token. Example: a
size `S` search returns no `US 9` shoes and no `XL` items. 5 of 5 searches.

**Why this target:**

`search_listings` doesn't call the model, so every result is either inside the
filters or it isn't. The size data is messy (`S/M`, `W30 L30`, `US 8.5`,
`XL (oversized)`), and a plain substring check would let `S` match `US 9`. One
wrong-size result makes the search look broken to a user, so I'm not allowing
any.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Extension criteria — Shape B: harden against failure

Written before the Milestone 5 tests. All five are about the extension. 2–4
are about the bad path. Failures are injected by replacing the model client
with a fake that returns 503s, hangs, or empty text.

---

## 1. A temporary 503 doesn't cost the fit card

When a model call returns `503 UNAVAILABLE` once and then succeeds, the run
finishes with a fit card, and its log line shows `retries` ≥ 1. 5 of 5 tries.

**Why this target:**

In unit 4, 7 of 65 runs lost their fit card to a single 503, and this is the
fix for that. With the failure injected, the retry path is plain code with no
randomness, so any miss means the retry is broken. Losing a card to a one-off
spike is the exact failure I'm fixing, so I'm not allowing one.

---

## 2. A model that keeps failing ends in a clear stop, not a crash

When every attempt fails (503 on all 5 attempts, or an empty response), `/ask`
returns HTTP 200 with `session["error"]` set, `stopped_at` naming the tool that
failed, and a log line with `status: "stopped"`. No 500s, no stack traces.
5 of 5 tries for each of the two failure types.

**Why this target:**

Before this unit, running out of retries raised `RuntimeError`, which the
agent didn't catch, so a long outage became a 500. A user can act on "the
model failed, try again". They can't act on a stack trace. This is
deterministic code, so 5 of 5.

---

## 3. A hung model call can't hang the request

When the model never answers, `/ask` still returns a stopped session within
180 seconds. 5 of 5 tries.

**Why this target:**

The worst case by design is 5 attempts × 30 s timeout + 15 s of backoff =
165 s, so 180 s leaves margin without hiding a missing timeout. A stricter
number would mean lowering `REQUEST_TIMEOUT_S`, which would start failing
slow but real answers (one live run took 20 s). It has to stay under
gunicorn's `--timeout 400`, or the worker is killed and no log line is
written.

> **Tightened in Milestone 6:** When the model never answers, `/ask` returns
> a stopped session within **75 seconds**. 5 of 5 tries.
>
> **Why tightened:** 180 s was MET 15 of 15 times (165.6 s every try), so the
> target was set to my design, not to the user. Nobody waits almost three
> minutes for an error. 75 s allows one 30 s timeout, one retry for a blip,
> and margin. Going lower would mean cutting `REQUEST_TIMEOUT_S`, and real
> calls on Render have taken up to ~17 s.

---

## 4. Bad input is rejected before any model call

Each of these four inputs gets a 400 or a session with
`stopped_at: "parse_query"`, makes `model_calls: 0`, and writes a log line:
`""`, `"   "`, `"under $30"`, and a body that isn't JSON. 4 of 4 inputs,
every time.

**Why this target:**

A blank query used to be sent to search as an empty description. Each wasted
model call counts against a 15-per-minute free tier, and the server handles
one request at a time. Input checks are plain code, so anything under 100%
means a check is missing.

---

## 5. Every request leaves a log record

For a batch of 20 requests (10 matching, 10 failing or rejected), `/logs`
returns exactly 20 new records, and every record has `ts`, `query`, `status`,
`latency_ms` and `error`. A record with `status: "ok"` also has a non-empty
`output` and `prompt_tokens` > 0. 20 of 20.

**Why this target:**

A failure that only shows up as a missing line is one I'll never find, and the
cost numbers in the README come from these records. One silent request means
the log can't be trusted for counting. Tokens > 0 on ok runs checks that the
cache is really off on Render. Otherwise the cost measurement is measuring
the cache.
