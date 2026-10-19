"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # State: the item search picked must be the one both later tools get.
        # Scored from the trace (item id at each step) and the session.
        "name": "selected item reaches every tool",
        "query": "oversized flannel shirt under $40",
        "wardrobe": "example",
        "criterion": 3,
    },
    # Fit card facts: five different items, two with a brand and three
    # without, so an invented brand would show up.
    {"name": "fit card: Levi's jeans (brand)", "query": "levi's 501 jeans",
     "wardrobe": "example", "criterion": 4},
    {"name": "fit card: baby tee (no brand)", "query": "butterfly baby tee",
     "wardrobe": "example", "criterion": 4},
    {"name": "fit card: Champion jacket (brand)", "query": "champion jacket",
     "wardrobe": "example", "criterion": 4},
    {"name": "fit card: cargo pants (no brand)", "query": "low-rise cargo pants",
     "wardrobe": "example", "criterion": 4},
    {"name": "fit card: bucket hat (no brand)", "query": "reversible bucket hat",
     "wardrobe": "example", "criterion": 4},
    # Search filters: five searches with both a size and a max price.
    {"name": "filters: graphic tee size L under $30",
     "query": "vintage graphic tee size L under $30", "wardrobe": "example", "criterion": 5},
    {"name": "filters: y2k top size S under $25",
     "query": "y2k top size S under $25", "wardrobe": "example", "criterion": 5},
    {"name": "filters: flannel size M under $35",
     "query": "flannel shirt size M under $35", "wardrobe": "example", "criterion": 5},
    {"name": "filters: jacket size M under $60",
     "query": "jacket size M under $60", "wardrobe": "example", "criterion": 5},
    {"name": "filters: sneakers size US 9 under $80",
     "query": "sneakers size US 9 under $80", "wardrobe": "example", "criterion": 5},
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
