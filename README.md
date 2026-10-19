# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr takes a plain-language thrift request, like "vintage graphic tee under
$30, size M", and searches 40 secondhand listings for the best keyword match
within that size and price. It then suggests one or two outfits that pair the
item with pieces from the user's wardrobe (or general styling advice if the
wardrobe is empty), and writes a short caption the user could post, mentioning
the item, its price and its platform. If nothing matches, it stops and says
what to change, such as different keywords, another size or a higher max price.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Filters `data/listings.json` by price and size, then ranks what's left by how many words of `description` appear in each listing's title, description and style tags. Filler words ("a", "for", "looking", …) are ignored.
- **Inputs:** `description` (str), `size` (str or None, None skips the size filter), `max_price` (float or None, inclusive, None skips the price filter). Size matches case-insensitively on whole tokens: the listing size is split on spaces, `/` and parentheses, so `"M"` matches `"S/M"` and `"M/L"` but `"L"` does not match `"XL"` and `"S"` does not match `"US 9"`. Listings sized "One Size" match any size.
- **Returns:** A `list[dict]` of at most `config.SEARCH_RESULT_LIMIT` (10) listing dicts, highest score first (ties keep their order in the data file), each with `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform`.
- **When it has nothing:** An empty list `[]`, never None and never an exception. Listings that match zero keywords are dropped, so a query with no word overlap also returns `[]`.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the thrifted item, using pieces from the user's wardrobe by name.
- **Inputs:** `new_item` (dict, one listing dict from `search_listings`), `wardrobe` (dict with an `items` key holding a list of item dicts: `id`, `name`, `category`, `colors`, `style_tags`, `notes`).
- **Returns:** A non-empty `str` of outfit suggestions that names specific wardrobe pieces.
- **When it has nothing:** If `wardrobe["items"]` is empty, it returns general styling advice for the item instead (still a non-empty `str`, never `""` and never an exception).

### `create_fit_card`

- **What it does:** Asks the model for a two-to-four sentence social-media caption about the find, mentioning the item, its price and its platform once each.
- **Inputs:** `outfit` (str, the output of `suggest_outfit`), `new_item` (dict, the same listing dict).
- **Returns:** A `str` caption of two to four sentences. It doesn't assume `brand` is set and leaves it out when it's None.
- **When it has nothing:** If `outfit` is empty or whitespace, it returns the string `"No outfit to caption, so no fit card was made."` without calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (keywords, size, max price) and stop without calling `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. `$30` (optionally after "under", "below", "less than" or "max") becomes `max_price` 30.0, and `size M` becomes `size` "M". Whatever is left is the `description`. Filler words like "looking for a" are ignored by `search_listings`, so they don't match every listing.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` (the list from `search_listings`) → `selected_item` (`search_results[0]`) → `outfit_suggestion` (from `suggest_outfit`, which reads `selected_item` and `wardrobe` from the session) → `fit_card` (from `create_fit_card`, which reads `outfit_suggestion` and `selected_item`). On an empty search the run stops after `search_results`, with `error` set and `selected_item`, `outfit_suggestion` and `fit_card` left as None.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'looking for a vintage graphic tee under $30'
```

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit: **Outfit 1:** Pair the Y2K Baby Tee with the baggy straight-leg jeans and the chunky white sneakers for a classic, effortless Y2K aesthetic. Layer the vintage black denim jacket on top to complete the look.

**Outfit 2:** Style the baby tee tucked into the wide-leg khaki trousers, accented by the brown leather belt, and wear it with the black combat boots for a cool mix of vintage and cottagecore vibes. Throw on the black cropped zip hoodie if you need an extra layer.

Fit card: Serving major Y2K energy with this adorable butterfly print baby tee, available now on Depop for just $18.00! Style it effortlessly with baggy jeans and a denim jacket for that classic turn-of-the-millennium look, or tuck it into khaki trousers with combat boots for a cool mix of vintage and cottagecore vibes.

2 model calls this session, 468 prompt + 177 output tokens

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(x['id'], x['title'], x['size'], x['price']) for x in search_listings('graphic tee', max_price=30)])"
[('lst_002', 'Y2K Baby Tee — Butterfly Print', 'S/M', 18.0), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 'L', 24.0), ('lst_017', 'Mesh Long-Sleeve Top — Black', 'S/M', 15.0), ('lst_033', 'Vintage Band Tee — Faded Grey', 'L', 19.0), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 'W29', 27.0), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 'L', 26.0)]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1: Casual Streetwear**
Pair the vintage Levi's with the white ribbed tank top and chunky white sneakers, then layer on the vintage black denim jacket for a classic, effortless look. Cinch the waist with the brown leather belt and complete the outfit with the black crossbody bag.

**Outfit 2: Cozy & Relaxed**
Combine the medium wash jeans with the oversized grey crewneck sweatshirt and black combat boots for an easy, laid-back vibe. Accessorize with the brown leather belt to tie the look together.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Channeling effortless off-duty streetwear energy with these medium wash Vintage Levi's 501 Jeans paired with fresh white sneakers. Snagged this classic denim staple for just $38.00 over on depop.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**
I used Claude for the tool testing in Milestone 4.

**Moment 2**
I used also Claude for some of the manual testing in Milestone 5 for the loop.

**Moment 3**
I used Claude in unit 4 to trigger the failures in milestone 2. I traced it myself, though.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Searched item is the item every tool receives | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card states the right facts (≥4 of 5 items, no invented brand) | 5 of 5 tries | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects size and price (all 5 searches) | 5 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |

From `results/run_2026-10-19_0003_before.md`, written by `run_eval.py::main`
(14 scenarios from `scenarios.py`, 5 tries each, caching off, temperature 0.9).
For criteria 4 and 5, one try covers all five of that criterion's scenarios:
try 2 of criterion 4 is the five fit cards from each scenario's second run.

**Real output from try 1**, pasted as text. The traces come from `trace.step()`
calls in `agent.py::run_agent`, fit cards from `tools.py::create_fit_card`,
search results from `tools.py::search_listings` over MCP.

Criterion 1 — `vintage graphic tee under $30`:

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: lst_002…
      →    branch: selected lst_002
[3] suggest_outfit
      in:  {'item': 'lst_002', 'wardrobe_items': 10}
      out: **Outfit 1:** Pair the Y2K Baby Tee with your baggy straight-leg jeans, dark wash and chunky white sneakers fo…
[4] create_fit_card
      in:  {'item': 'lst_002', 'outfit': '**Outfit 1:** Pair the Y2K Baby Tee with your baggy straight…'}
      out: Channel your inner 2000s pop star with this dreamy white, pink, and purple butterfly print Y2K Baby Tee, givin…

Fit card:
Channel your inner 2000s pop star with this dreamy white, pink, and purple butterfly print Y2K Baby Tee, giving off the ultimate nostalgic, sweet-yet-edgy vibe. Grab it now for just $18.00 exclusively on Depop before it's gone!
```

Criterion 2 — `designer ballgown size XXS under $5`:

```
- stopped early: yes — No listings matched "designer ballgown" in size XXS under $5. Try to use fewer or different keywords, or try another size, or raise your max price.
- selected_item: (none)
- search_results: 0

[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    branch: empty, stopping
```

Criterion 3 — `oversized flannel shirt under $40` (`lst_003` at every step):

```
- selected_item: Oversized Flannel Shirt — Plaid Red/Black ($22.0, thredUp)
- search_results: 7
  - lst_003: size XL (oversized), $22.0
  ...
[2] search_listings (MCP)
      out: 7 items: lst_003…
      →    branch: selected lst_003
[3] suggest_outfit
      in:  {'item': 'lst_003', 'wardrobe_items': 10}
[4] create_fit_card
      in:  {'item': 'lst_003', 'outfit': '**Outfit 1: 90s Grunge Casual**\nLayer the Oversized Flannel …'}
```

Criterion 4 — `butterfly baby tee` (`brand` is None; card has the price and
platform and no brand):

```
Channel your inner 2000s pop star with this dreamy Y2K Baby Tee — Butterfly Print, featuring the cutest pastel pink and purple graphics! Grab it right now on Depop for just $18.00 to complete your effortless throwback streetwear or edgy utility looks.
```

Criterion 5 — the two failing searches:

```
vintage graphic tee size L under $30
- search_results: 5
  - lst_006: size L, $24.0
  - lst_033: size L, $19.0
  - lst_015: size L, $26.0
  - lst_014: size One Size (adjustable), $12.0
  - lst_034: size One Size, $14.0

sneakers size US 9 under $80
[1] parse_query
      in:  sneakers size US 9 under $80
      out: {'description': 'sneakers 9', 'size': 'US', 'max_price': 80.0}
- search_results: 2
  - lst_035: size US 9, $20.0
  - lst_019: size US 8, $48.0
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| #   | Criterion | Target | Verdict | How I decided |
| --- | --------- | ------ | ------- | ------------- |
| 1   | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries ended with `stopped early: no` and a non-empty fit card, with no crashes. |
| 2   | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | All five stopped at `search_listings` with no outfit or fit card, and the message names keywords, size and max price to change. |
| 3   | Searched item is the item every tool receives | 5 of 5 | MET (5/5) | In every try, `search_results[0]`, the selected item and the `item` in the `suggest_outfit` and `create_fit_card` trace inputs were all `lst_003`. |
| 4   | Fit card states the right facts | 4 of 5 items, every try | MET (5/5) | All 25 cards (5 items × 5 tries) were 2–4 sentences with the exact price (e.g. `$18.00`) and platform. None of the 15 cards for unbranded items named a brand. Checked with a script against `data/listings.json`, then spot-read. |
| 5   | Search respects size and price | 5 of 5 | MISSED (0/5) | Price held in all 25 searches. Size failed in 2 of the 5 searches, the same two in every try, so no try had all five clean. |

**Diagnoses**

**Criterion 5 missed in every try, in two places, both about size.** Price
never failed: every result in all 25 searches was at or under the max. The
failures are the same two searches every time, which fits: search doesn't call
the model, so a wrong result is wrong every run.

1. **Tool, `tools.py::_size_matches`: "One Size" matches every size.** `vintage
   graphic tee size L under $30` returned a belt (`lst_014`, "One Size
   (adjustable)") and a bucket hat (`lst_034`, "One Size"). My Tool Inventory
   says One Size items match any size, so the tool did what its spec said. But
   criterion 5 says every result must have the requested size *as a whole
   token*, and "L" isn't one. The spec and the criterion disagree, and a user
   who asked for a size L tee getting a belt sides with the criterion. They
   only matched at all because "vintage" is in their style tags.
2. **Loop, `agent.py::parse_query`: a two-word size gets cut in half.** The
   regex `size\s+([a-z0-9./]+)` stops at the first space, so `size US 9` is
   parsed as size `"US"` and the `9` ends up in the description
   (`'sneakers 9'`). `_size_matches("US", "US 8")` is True, because "us" is a
   token of "US 8", so a US 8 shoe came back for a US 9 search. The tool was
   handed the wrong size. Search worked correctly on what it was given.

**The pattern:** both failures happen where free-text sizes meet the data's
messy size formats (`One Size (adjustable)`, `US 8.5`, `W30 L30`). Sizes that
are one plain token, like `S`, `M` or `W28`, never failed. One fix covers both:
treat the size as a whole phrase (parse everything after "size" up to "under"
or the end, and stop letting One Size match a specific size request).

**Criteria 1–4 were met 5/5, and honestly 1 and 4 were set low.** Criterion 1
allowed a miss for keyword phrasing, but every scenario used words straight
from the listings. Criterion 4 required only 4 of 5 cards per try, and all 25
passed. I'd tighten criterion 4 to 5 of 5 cards per try, and add that the
outfit names at least one piece from the wardrobe by its exact name, since that's
the part of the model's output nothing currently checks.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30, size L' --trace
[1] parse_query
      in:  vintage graphic tee under $30, size L
      out: {'description': 'vintage graphic tee', 'size': 'L', 'max_price': 30.0}
[2] search_listings (MCP)
      in:  {'description': 'vintage graphic tee', 'size': 'L', 'max_price': 30.0}
      out: 5 items: lst_006…
      →    branch: selected lst_006
[3] suggest_outfit
      in:  {'item': 'lst_006', 'wardrobe_items': 10}
      out: **Outfit 1 (Grunge Streetwear):** Pair the graphic tee with the baggy straight-leg jeans, dark wash, and layer…
[4] create_fit_card
      in:  {'item': 'lst_006', 'outfit': '**Outfit 1 (Grunge Streetwear):** Pair the graphic tee with …'}
      out: Scored this ultimate 2003 tour bootleg style graphic tee for just $24.00 on Depop. It’s got that perfectly wor…

  Found:    Graphic Tee — 2003 Tour Bootleg Style — $24.0 on depop
```

**Empty search**

```
$ python app.py ask 'sequined tuxedo size XXS under $3' --trace
[1] parse_query
      in:  sequined tuxedo size XXS under $3
      out: {'description': 'sequined tuxedo', 'size': 'XXS', 'max_price': 3.0}
[2] search_listings (MCP)
      in:  {'description': 'sequined tuxedo', 'size': 'XXS', 'max_price': 3.0}
      out: [] (empty)
      →    branch: empty, stopping

  No listings matched "sequined tuxedo" in size XXS under $3. Try to use fewer or different keywords, or try another size, or raise your max price.

0 model calls this session
```

The empty run is two steps instead of four: it stops at the branch and never
calls the model.

**The three failure modes, triggered one at a time:**

1. **Empty search** (`'sequined tuxedo size XXS under $3'`): stopped after
   `search_listings` with the message above. `fit_card` stayed None. No change needed.
2. **Empty wardrobe** (`'flannel shirt size L' --empty-wardrobe`):
   `suggest_outfit` gave general advice instead of crashing: _"Pair the olive
   canvas shacket with a classic white crewneck tee, well-fitted blue
   straight-leg jeans, and clean white canvas sneakers for an effortless,
   everyday look…"_ No change needed.
3. **Model unavailable** (bad `GEMINI_API_KEY`, new query
   `'red plaid flannel for layering'`): the first run didn't hang or show a
   stack trace, but only because `app.py` caught the exception
   (`ModelUnavailable: The model rejected your API key…`). `run_agent` itself
   raised, so anything else calling it would crash. I added a
   `ModelUnavailable` handler in `agent.py::run_agent` that keeps the search
   result and stops:

   ```
   [3] suggest_outfit
         →    model unavailable, stopping

     Found Oversized Flannel Shirt — Plaid Red/Black ($22 on thredUp), but couldn't reach the model to run suggest_outfit. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Then run the same query again.
   ```

**On the MCP move:** `search_listings` is registered in `mcp_server.py`, and
`run_agent` calls it through `mcp_client.call_tool("search_listings", {...})`
instead of importing it (step [2] above). Nothing else changed. For both a
matching query (10 results) and an empty one, the list that came back over MCP
was equal, dict for dict, to the direct call, so the tool was already returning
plain JSON-friendly values (dicts, lists, floats, and None for brand).

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
| --------- | ------ | ----- | ----- | ----- | ----- | ----- | ------- |
| 1.        |        |       |       |       |       |       |         |
| 2.        |        |       |       |       |       |       |         |
| 3.        |        |       |       |       |       |       |         |
| 4.        |        |       |       |       |       |       |         |
| 5.        |        |       |       |       |       |       |         |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
