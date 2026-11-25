#!/usr/bin/env python3
"""Laugh Track: The Crypto Trading Joke Contest entry.

Writes one original one-line joke about crypto and trading life
(at most 200 characters) to /output/entry.txt.

How it picks the line: fourteen original candidate jokes, each written
for this entry, are scored against the judge's five criteria, in the
judge's own order of importance:

  1. it is a one-line joke about crypto and trading life, with a clear
     setup and a turn
  2. it lands a real laugh, with a surprise turn and a payoff that
     rewards the setup
  3. it feels true to crypto and trading life, with a recognisable
     detail such as the chart, the bag or the group chat
  4. it uses every word well: tight phrasing, no throat clearing, and
     the punchline at the end
  5. it holds up on a second read and is a line a trader would repeat
     to a friend

Each criterion is rated 0-5 and weighted 5, 4, 3, 2, 1, matching the
judge's priority order. The highest total wins; ties go to the
earliest candidate in the list, so the choice is fully deterministic.

Freshness is not only hand-rated: any candidate that leans on a tired
crypto-joke trope loses one point off its true-detail rating per
trope phrase found in its own text (clamped at zero) — a line built
on a trope everyone has heard is not an earned detail, so it cannot
win on a generous hand rating alone.

Revision (second pass on the winner, candidate 1): the first draft
read "...so I bought the top, and now the group chat calls it a
generational learning experience." The revision swaps the flat "and
now" for an em-dash beat and "the same chat" instead of repeating
"the group chat": the callback is tighter, the pause lets the turn
land, and the punchline still closes on "generational learning
experience". The revised line below is the entry.

No network, no external input, no randomness. The program verifies
its own output (1-200 characters, a single line, UTF-8) and prints
the SHA-256 of the file it wrote.
"""

from hashlib import sha256
from os import environ, makedirs
from sys import exit as finish, stderr

# Weights for the five judge criteria, in the judge's priority order:
# on-topic setup+turn, laugh, true detail, tight, repeatable.
WEIGHTS = (5, 4, 3, 2, 1)

# Overused crypto-joke tropes. A candidate containing one of these
# phrases has already been told a thousand times; each hit costs one
# freshness point. Matched case-insensitively against the text itself.
CLICHES = (
    "to the moon",
    "diamond hands",
    "bought the dip",
    "buy the dip",
    "lambo",
    "wen moon",
    "have fun staying poor",
)


# Each candidate: (text, (on-topic, laugh, true, tight, repeatable)).
# All fourteen lines are original, written for this entry.
CANDIDATES = [
    (
        "The group chat called it a generational buying opportunity, so I "
        "bought the top \u2014 and now the same chat calls it a "
        "generational learning experience.",
        (5, 5, 5, 4, 5),
    ),
    (
        "I bought the dip, then the dip dipped, then I bought that dip "
        "too \u2014 my average entry is now a support level for the "
        "entire market.",
        (5, 4, 5, 5, 4),
    ),
    (
        "I sold at the bottom to buy back lower, then watched it pump "
        "40% while my limit order sat there like a gym membership in "
        "January.",
        (5, 4, 5, 4, 4),
    ),
    (
        "My portfolio is so diversified that when Bitcoin sneezes, my "
        "altcoins catch pneumonia and my stablecoins file for divorce.",
        (5, 4, 4, 4, 4),
    ),
    (
        "The exchange sent me a 'we miss you' email after one day away, "
        "which is more attention than my portfolio has given me all year.",
        (5, 4, 4, 4, 4),
    ),
    (
        "The whitepaper said the token would revolutionise finance; "
        "three months later it revolutionised my ability to explain "
        "losses to my girlfriend.",
        (5, 4, 4, 4, 3),
    ),
    (
        "I told my mum crypto was my retirement plan; she asked which "
        "year I plan to retire, and I said whichever year the chart "
        "goes back up.",
        (5, 4, 4, 3, 4),
    ),
    (
        "I set a stop-loss, a take-profit, and an alarm for 3 a.m.; the "
        "market hit all three, in that order, while I was asleep.",
        (5, 3, 5, 3, 3),
    ),
    (
        "I bought green candles, sold red ones, and now my net worth "
        "looks like a staircase going down.",
        (5, 3, 4, 4, 4),
    ),
    (
        "I check the chart so often my phone thinks I'm in a "
        "relationship with it, and honestly, it's the most committed "
        "one I've had.",
        (4, 3, 4, 4, 3),
    ),
    (
        "I finally understood support and resistance when my bank "
        "balance supported nothing and resisted every withdrawal.",
        (5, 3, 4, 4, 3),
    ),
    (
        "My risk management is impeccable: I only ever risk money I "
        "can't afford to lose, which is why I have nothing left to risk.",
        (5, 4, 3, 4, 4),
    ),
    (
        "I DCA into Bitcoin every payday, which means I buy the top "
        "twelve times a year with the discipline of a man paying rent "
        "to a landlord who keeps raising it.",
        (5, 3, 4, 3, 3),
    ),
    (
        "I told my therapist I day-trade crypto; she said my charts "
        "show classic avoidance, so now I avoid her too and watch the "
        "candles instead.",
        (5, 3, 4, 3, 3),
    ),
]


def rate(text, ratings):
    """Weighted total for one candidate's five criterion ratings.

    The true-detail rating is adjusted first: each tired-trope phrase
    found in the candidate's own text costs one point.
    """
    on_topic, laugh, true_detail, tight, repeatable = ratings
    lowered = text.lower()
    hits = sum(1 for phrase in CLICHES if phrase in lowered)
    true_detail = max(0, true_detail - hits)
    adjusted = (on_topic, laugh, true_detail, tight, repeatable)
    return sum(w * r for w, r in zip(WEIGHTS, adjusted))


def choose(candidates):
    """Return (index, text, total) of the best candidate.

    Deterministic: strictly greater totals replace the leader, so the
    earliest candidate wins any tie.
    """
    best_index, best_text, best_total = -1, "", -1
    for index, (text, ratings) in enumerate(candidates):
        total = rate(text, ratings)
        if total > best_total:
            best_index, best_text, best_total = index, text, total
    return best_index, best_text, best_total


def gate(text):
    """Gate the chosen line the way the sealed scorer does."""
    if not (1 <= len(text) <= 200):
        return "length %d is outside 1..200 characters" % len(text)
    if text.strip() != text or not text.strip():
        return "entry is blank or has surrounding whitespace"
    if "\n" in text or "\r" in text:
        return "entry is not a single line"
    return None


def run():
    index, text, total = choose(CANDIDATES)
    problem = gate(text)
    if problem is not None:
        print("self-check failed: %s" % problem, file=stderr)
        return 1

    out_path = environ.get("OUTPUT_PATH", "/output/entry.txt")
    out_dir = out_path.rsplit("/", 1)[0] if "/" in out_path else ""
    if out_dir:
        makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(text)
    digest = sha256(text.encode("utf-8")).hexdigest()
    print("candidate %d of %d, score %d" % (index + 1, len(CANDIDATES), total))
    print("entry: %s" % text)
    print("sha256: %s" % digest)
    return 0


finish(run())
