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
