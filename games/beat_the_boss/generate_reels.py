"""Generate properly sized reel strips for all three modes."""

import random

def create_reel(symbol_counts, output_file):
    """Create a reel CSV with exact symbol counts."""
    symbols = []
    for symbol, count in symbol_counts.items():
        symbols.extend([symbol] * count)

    # Verify total is 100
    assert len(symbols) == 100, f"Total symbols: {len(symbols)}, expected 100"

    # Shuffle for randomness
    random.shuffle(symbols)

    # Write to CSV
    with open(output_file, 'w') as f:
        f.write("symbol\n")
        for symbol in symbols:
            f.write(f"{symbol}\n")

    print(f"Created {output_file} with {len(symbols)} symbols")
    for symbol, count in sorted(symbol_counts.items()):
        pct = (count / len(symbols)) * 100
        print(f"  {symbol}: {count} ({pct:.1f}%)")

# Macron: Defensive, target ~98% RTP
# v6 FINAL: Reduce DUK from 18% to 16% (was 108.72%, need 98%)
macron_symbols = {
    "BWD": 26,
    "DUK": 16,
    "FWD": 20,
    "PUN": 20,
    "UPP": 12,
    "HRT": 4,
    "DIZ": 1,
    "KO": 1,
}

# Putin: Balanced, target ~98% RTP
# v6 FINAL: Keep at 12% DUK - achieved 98.81% (PERFECT!)
putin_symbols = {
    "FWD": 26,
    "PUN": 25,
    "BWD": 16,
    "DUK": 12,
    "UPP": 11,
    "HRT": 5,
    "DIZ": 4,
    "KO": 1,
}

# Trump: Aggressive, target ~98% RTP
# v7 ACTUAL FINAL: UPP was the culprit! Reduce from 21% to 12%
trump_symbols = {
    "FWD": 32,
    "PUN": 32,
    "UPP": 12,
    "DUK": 8,
    "BWD": 10,
    "HRT": 4,
    "DIZ": 1,
    "KO": 1,
}

print("\n" + "="*60)
print("GENERATING REEL STRIPS")
print("="*60 + "\n")

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
reels_dir = os.path.join(script_dir, "reels")

create_reel(macron_symbols, os.path.join(reels_dir, "macron_base_v6.csv"))
print()
create_reel(putin_symbols, os.path.join(reels_dir, "putin_base_v6.csv"))
print()
create_reel(trump_symbols, os.path.join(reels_dir, "trump_base_v6.csv"))

print("\n" + "="*60)
print("REEL GENERATION COMPLETE")
print("="*60 + "\n")