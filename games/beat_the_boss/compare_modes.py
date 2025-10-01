"""Compare sequence probabilities across all three modes."""

from game_config import GameConfig
import random

config = GameConfig()

modes = ["MACRON_BASE", "PUTIN_BASE", "TRUMP_BASE"]

print("\n" + "="*60)
print("SEQUENCE PROBABILITY ANALYSIS")
print("="*60)

# Test probability of generating common winning sequences
test_sequences = [
    ["FWD", "PUN"],
    ["PUN", "UPP"],
    ["FWD-PUN-UPP"],
    ["DUK", "UPP"],
]

num_tests = 100000

for mode_name in modes:
    reel = config.reels[mode_name][0]
    total_symbols = len(reel)

    print(f"\n{mode_name}:")
    print(f"Total reel positions: {total_symbols}")

    # Calculate probability of drawing each symbol
    symbol_probs = {}
    for symbol in reel:
        symbol_probs[symbol] = symbol_probs.get(symbol, 0) + 1

    for symbol in symbol_probs:
        symbol_probs[symbol] /= total_symbols

    # Calculate 2-move sequence probabilities
    print(f"\nTwo-move sequence probabilities:")
    print(f"  FWD-PUN: {symbol_probs.get('FWD', 0) * symbol_probs.get('PUN', 0) * 100:.2f}%")
    print(f"  PUN-UPP: {symbol_probs.get('PUN', 0) * symbol_probs.get('UPP', 0) * 100:.2f}%")
    print(f"  FWD-UPP: {symbol_probs.get('FWD', 0) * symbol_probs.get('UPP', 0) * 100:.2f}%")
    print(f"  DUK-UPP: {symbol_probs.get('DUK', 0) * symbol_probs.get('UPP', 0) * 100:.2f}%")

    # Simulate sequence generation
    sequence_hits = {
        "FWD-PUN": 0,
        "PUN-UPP": 0,
        "FWD-UPP": 0,
        "DUK-UPP": 0,
    }

    for _ in range(num_tests):
        # Generate 6-move sequence
        moves = [random.choice(reel) for _ in range(6)]

        # Check for winning sequences (looking for any subsequence)
        for i in range(len(moves)-1):
            two_move = f"{moves[i]}-{moves[i+1]}"
            if two_move in sequence_hits:
                sequence_hits[two_move] += 1

    print(f"\nActual frequency in {num_tests:,} 6-move sequences:")
    for seq, count in sequence_hits.items():
        payout = config.paytable.get((2, seq), 0)
        print(f"  {seq}: {count:,} ({count/num_tests*100:.2f}%) [pays {payout}x]")

print("\n" + "="*60)