"""Analyze books_macron.json to verify RTP and win distribution."""

import json

# Load the books
with open("library/books/books_macron.json", "r") as f:
    books = json.load(f)

print(f"\n{'='*60}")
print("BOOK ANALYSIS - MACRON MODE")
print(f"{'='*60}\n")

total_spins = len(books)
total_wins = 0
wins_count = 0
win_distribution = {}
rounding_losses = 0

for book in books:
    # Get payout multiplier (stored as integer, need to divide by 100)
    payout_int = book.get("payoutMultiplier", 0)
    payout_multiplier = payout_int / 100.0

    if payout_multiplier > 0:
        wins_count += 1
        total_wins += payout_multiplier

        # Track win distribution
        if payout_multiplier < 0.01:
            rounding_losses += 1

        # Bucket wins for distribution analysis
        if payout_multiplier < 0.1:
            bucket = "tiny (0.01-0.09x)"
        elif payout_multiplier < 0.5:
            bucket = "small (0.1-0.49x)"
        elif payout_multiplier < 2.0:
            bucket = "medium (0.5-1.99x)"
        elif payout_multiplier < 10.0:
            bucket = "big (2-9.99x)"
        elif payout_multiplier < 100.0:
            bucket = "huge (10-99.99x)"
        else:
            bucket = "mega (100x+)"

        win_distribution[bucket] = win_distribution.get(bucket, 0) + 1

# Calculate RTP
rtp = (total_wins / total_spins) * 100
hit_rate = (wins_count / total_spins) * 100

print(f"Total spins: {total_spins:,}")
print(f"Winning spins: {wins_count:,}")
print(f"Hit rate: {hit_rate:.2f}%")
print(f"\nRTP: {rtp:.2f}%")
print(f"Average win: {total_wins/wins_count:.4f}x")

print(f"\n{'='*60}")
print("WIN DISTRIBUTION")
print(f"{'='*60}")
for bucket in sorted(win_distribution.keys()):
    count = win_distribution[bucket]
    pct = (count / total_spins) * 100
    print(f"{bucket:20s}: {count:6,} ({pct:5.2f}%)")

print(f"\n{'='*60}")
print("ROUNDING CHECK")
print(f"{'='*60}")
print(f"Wins < 0.01x (potential rounding issues): {rounding_losses:,}")
print(f"These should be 0 with the new paytable design.")
print(f"{'='*60}\n")