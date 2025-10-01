"""Calculate mode-specific RTP adjustment factors."""

# Current RTPs from 100k spin test
current_rtps = {
    "macron": 94.32,
    "putin": 93.94,
    "trump": 106.77,
}

target_rtp = 98.0

print("\n" + "="*60)
print("MODE-SPECIFIC RTP ADJUSTMENT FACTORS")
print("="*60)

mode_adjustments = {}
for mode, current in current_rtps.items():
    adjustment = target_rtp / current
    mode_adjustments[mode] = adjustment
    print(f"{mode.upper():10s}: {current:6.2f}% → {target_rtp:.2f}% (multiply by {adjustment:.4f})")

print("\n" + "="*60)
print("Add to game_config.py:")
print("="*60)
print("\n# Mode-specific RTP adjustments")
print("self.mode_rtp_adjustments = {")
for mode, adj in mode_adjustments.items():
    print(f'    "{mode}": {adj:.4f},')
print("}")