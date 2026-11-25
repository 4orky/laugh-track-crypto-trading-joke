"""Entry for the Laugh Track crypto-trading joke contest.

Fourteen one-line jokes about life as a crypto trader were written for
this contest and then ranked against the five things the judges care
about, most important first: a setup that turns, a genuine laugh, a
detail that rings true to anyone who has watched a chart at 3 a.m.,
wording with nothing wasted, and a line worth repeating to a friend.
Each joke gets a mark from zero to five on every one of those five
points, and the points are weighted five, four, three, two, one, so
the first thing the judges care about counts the most.

A joke that leans on a punchline everybody has already heard does not
get full credit for ringing true: every stale trope spotted inside
the joke itself knocks one off its truth mark, down to zero at the
lowest. The best total takes the prize; when two jokes tie, the one
that appears first in the list takes it, which keeps the whole pick
repeatable down to the byte.

The winning joke went through a second draft before it was frozen.
At first the two halves were joined with a plain "and now the group
chat calls it...", which read flat. The rewrite cuts in with an
em dash, points back with "the same chat" instead of naming the
group chat twice, and leaves the closing punchline exactly where it
was. The winning line is printed, written out, and hashed below.

Nothing here touches the network, rolls dice, or reads anything from
outside the file: the jokes, the marks, and the rules all live in
this one script, and it only ever writes one file. This is the whole entry."""

import hashlib
import os
import sys

PRIORITY_WEIGHTS = [5, 4, 3, 2, 1]

TIRED_TROPES = (
    "to the moon|diamond hands|bought the dip|buy the dip|lambo|"
    "wen moon|have fun staying poor"
).split("|")

JOKE_BOOK = [
    {
        "text": "The group chat called it a generational buying opportunity, so I bought the top — and now the same chat calls it a generational learning experience.",
        "marks": [5, 5, 5, 4, 5],
    },
    {
        "text": "I bought the dip, then the dip dipped, then I bought that dip too — my average entry is now a support level for the entire market.",
        "marks": [5, 4, 5, 5, 4],
    },
    {
        "text": "I sold at the bottom to buy back lower, then watched it pump 40% while my limit order sat there like a gym membership in January.",
        "marks": [5, 4, 5, 4, 4],
    },
    {
        "text": "My portfolio is so diversified that when Bitcoin sneezes, my altcoins catch pneumonia and my stablecoins file for divorce.",
        "marks": [5, 4, 4, 4, 4],
    },
    {
        "text": "The exchange sent me a 'we miss you' email after one day away, which is more attention than my portfolio has given me all year.",
        "marks": [5, 4, 4, 4, 4],
    },
    {
        "text": "The whitepaper said the token would revolutionise finance; three months later it revolutionised my ability to explain losses to my girlfriend.",
        "marks": [5, 4, 4, 4, 3],
    },
    {
        "text": "I told my mum crypto was my retirement plan; she asked which year I plan to retire, and I said whichever year the chart goes back up.",
        "marks": [5, 4, 4, 3, 4],
    },
    {
        "text": "I set a stop-loss, a take-profit, and an alarm for 3 a.m.; the market hit all three, in that order, while I was asleep.",
        "marks": [5, 3, 5, 3, 3],
    },
    {
        "text": "I bought green candles, sold red ones, and now my net worth looks like a staircase going down.",
        "marks": [5, 3, 4, 4, 4],
    },
    {
        "text": "I check the chart so often my phone thinks I'm in a relationship with it, and honestly, it's the most committed one I've had.",
        "marks": [4, 3, 4, 4, 3],
    },
    {
        "text": "I finally understood support and resistance when my bank balance supported nothing and resisted every withdrawal.",
        "marks": [5, 3, 4, 4, 3],
    },
    {
        "text": "My risk management is impeccable: I only ever risk money I can't afford to lose, which is why I have nothing left to risk.",
        "marks": [5, 4, 3, 4, 4],
    },
    {
        "text": "I DCA into Bitcoin every payday, which means I buy the top twelve times a year with the discipline of a man paying rent to a landlord who keeps raising it.",
        "marks": [5, 3, 4, 3, 3],
    },
    {
        "text": "I told my therapist I day-trade crypto; she said my charts show classic avoidance, so now I avoid her too and watch the candles instead.",
        "marks": [5, 3, 4, 3, 3],
    }]


def truth_after_tropes(joke, truth_mark):
    lowered = joke.lower()
    stale = 0
    for trope in TIRED_TROPES:
        if trope in lowered:
            stale += 1
    if truth_mark - stale < 0:
        return 0
    return truth_mark - stale


def total_for(entry):
    marks = list(entry["marks"])
    marks[2] = truth_after_tropes(entry["text"], marks[2])
    points = 0
    for weight, mark in zip(PRIORITY_WEIGHTS, marks):
        points += weight * mark
    return points


def pick_winner(book):
    champion = 0
    champion_points = total_for(book[0])
    for position in range(1, len(book)):
        points = total_for(book[position])
        if points > champion_points:
            champion = position
            champion_points = points
    return champion, champion_points


def check_entry(line):
    flaws = []
    if len(line) < 1 or len(line) > 200:
        flaws.append("length %d outside 1..200" % len(line))
    if line != line.strip():
        flaws.append("leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        flaws.append("more than one line")
    return flaws


def main():
    winner, points = pick_winner(JOKE_BOOK)
    line = JOKE_BOOK[winner]["text"]
    flaws = check_entry(line)
    if flaws:
        for flaw in flaws:
            print("self-check failed: " + flaw, file=sys.stderr)
        sys.exit(1)
    target = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    folder, _, _name = target.rpartition("/")
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(target, "w", encoding="utf-8") as out:
        out.write(line)
    fingerprint = hashlib.sha256(line.encode("utf-8")).hexdigest()
    for position, entry in enumerate(JOKE_BOOK):
        print("candidate %d: %d points" % (position + 1, total_for(entry)))
    print("winner: candidate %d with %d points" % (winner + 1, points))
    print("entry: " + line)
    print("sha256: " + fingerprint)


if __name__ == "__main__":
    main()
