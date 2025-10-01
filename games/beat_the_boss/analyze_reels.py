"""Analyze reel distributions for all three boss modes."""

from game_config import GameConfig

config = GameConfig()

modes = ["MACRON_BASE", "PUTIN_BASE", "TRUMP_BASE"]

print(f"\n{'='*60}")
print("REEL ANALYSIS - ALL BOSS MODES")
print(f"{'='*60}\n")

for mode_name in modes:
    reel = config.reels[mode_name][0]  # Get first (and only) reel strip

    symbol_counts = {}
    for symbol in reel:
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

    total = len(reel)

    print(f"{mode_name}:")
    print(f"Total symbols: {total}")
    print(f"\nSymbol distribution:")

    # Group by category
    defensive = 0
    offensive = 0
    damage = 0
    knockout = 0
    positioning = 0

    for symbol, count in sorted(symbol_counts.items()):
        pct = (count / total) * 100
        print(f"  {symbol:4s}: {count:3d} ({pct:5.1f}%)")

        if symbol in ["BWD", "DUK"]:
            defensive += count
        elif symbol in ["PUN", "UPP"]:
            offensive += count
        elif symbol in ["HRT", "DIZ"]:
            damage += count
        elif symbol == "KO":
            knockout += count
        elif symbol == "FWD":
            positioning += count

    print(f"\nCategory totals:")
    print(f"  Defensive (BWD+DUK): {defensive} ({(defensive/total)*100:.1f}%)")
    print(f"  Offensive (PUN+UPP): {offensive} ({(offensive/total)*100:.1f}%)")
    print(f"  Positioning (FWD):   {positioning} ({(positioning/total)*100:.1f}%)")
    print(f"  Damage (HRT+DIZ):    {damage} ({(damage/total)*100:.1f}%)")
    print(f"  Knockout (KO):       {knockout} ({(knockout/total)*100:.1f}%)")
    print(f"{'='*60}\n")