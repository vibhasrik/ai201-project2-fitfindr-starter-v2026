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
| 1.        |        |       |       |       |       |       |         |
| 2.        |        |       |       |       |       |       |         |
| 3.        |        |       |       |       |       |       |         |
| 4.        |        |       |       |       |       |       |         |
| 5.        |        |       |       |       |       |       |         |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1   |           |        |         |               |
| 2   |           |        |         |               |
| 3   |           |        |         |               |
| 4   |           |        |         |               |
| 5   |           |        |         |               |

**Diagnoses**

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
