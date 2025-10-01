"""Scale paytable to achieve target RTPs based on test results."""

from game_config import GameConfig

# Current RTPs from testing
current_rtps = {
    "macron": 88.96,
    "putin": 88.60,
    "trump": 100.70,
}

target_rtp = 98.0

# Calculate scaling factors
scaling_factors = {}
for mode, current_rtp in current_rtps.items():
    factor = target_rtp / current_rtp
    scaling_factors[mode] = factor
    print(f"{mode.upper()}: {current_rtp}% → {target_rtp}% (multiply by {factor:.4f})")

# Average scaling factor (use this for all modes to keep paytable consistent)
avg_factor = sum(scaling_factors.values()) / len(scaling_factors)
print(f"\nAverage scaling factor: {avg_factor:.4f}")

# Load current paytable
config = GameConfig()

print("\n" + "="*60)
print("SCALED PAYTABLE (using average factor):")
print("="*60)

scaled_paytable = {}
for key, value in config.paytable.items():
    scaled_value = value * avg_factor
    scaled_paytable[key] = round(scaled_value, 4)  # Round to 4 decimals

    # Print a few examples
    if len(scaled_paytable) <= 10:
        print(f"  {key}: {value:.4f} → {scaled_value:.4f}")

print(f"\nTotal entries: {len(scaled_paytable)}")

# Generate the Python dict format for copy-paste
print("\n" + "="*60)
print("Copy this to game_config.py:")
print("="*60)
print("self.paytable = {")

for key, value in sorted(scaled_paytable.items()):
    length, sequence = key
    comment = ""
    if "KO" in sequence:
        comment = "  # Knockout"
    elif length >= 5:
        comment = "  # Legendary"
    elif length == 4:
        comment = "  # Expert combo"
    elif length == 3:
        comment = "  # 3-move combo"

    print(f"    ({length}, \"{sequence}\"): {value},{comment}")

print("}")