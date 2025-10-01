# Beat the Boss - Stake Engine Upload Guide

## Files to Upload

Upload these files from `games/beat_the_boss/library/publish_files/`:

### 1. **index.json** (Required)
**Path:** `library/publish_files/index.json`

Main configuration file defining all three game modes.

```json
{
    "modes": [
        {
            "name": "macron",
            "cost": 1.0,
            "events": "books_macron.jsonl.zst",
            "weights": "lookUpTable_macron_0.csv"
        },
        {
            "name": "putin",
            "cost": 2.0,
            "events": "books_putin.jsonl.zst",
            "weights": "lookUpTable_putin_0.csv"
        },
        {
            "name": "trump",
            "cost": 3.0,
            "events": "books_trump.jsonl.zst",
            "weights": "lookUpTable_trump_0.csv"
        }
    ]
}
```

### 2. **Lookup Tables** (Required - 3 files)
**Paths:**
- `library/publish_files/lookUpTable_macron_0.csv` (1.9 MB)
- `library/publish_files/lookUpTable_putin_0.csv` (1.9 MB)
- `library/publish_files/lookUpTable_trump_0.csv` (1.9 MB)

**Format:** CSV with columns: `index, seed, weight`

These contain the optimized reel weights for the RGS to use when generating spins.

---

## Game Configuration Summary

### Game Metadata
- **Game ID:** `beat_the_boss`
- **Provider Number:** `1001`
- **Working Name:** `Beat the Boss`
- **Game Type:** Sequence-based boxing game (6-move combos)
- **RTP:** 98.00% (all modes)

### Three Game Modes

| Mode | Bet Cost | Max Win | RTP | Hit Rate | Volatility |
|------|----------|---------|-----|----------|------------|
| **Macron** | 1.0x | 5000x | 98.00% | 99.37% | Low (Defensive) |
| **Putin** | 2.0x | 7500x | 98.00% | 98.11% | Medium (Balanced) |
| **Trump** | 3.0x | 10000x | 98.00% | 99.29% | High (Aggressive) |

### Key Features
- **Best Win Only:** Awards highest-paying sequence per spin
- **6-Move Sequences:** Maximum combo length
- **42 Winning Combinations:** From 0.0212x to 2336x
- **No Freespins:** Continuous base game with round mechanics
- **No Bet Cost Scaling:** Paytable multipliers are consistent, mode adjustments applied internally

---

## Backend Integration Requirements

### Paytable Configuration
The backend needs to implement mode-specific RTP adjustments:

```javascript
mode_rtp_adjustments = {
    "macron": 1.0390,   // Multiply all wins by this
    "putin": 1.0432,
    "trump": 0.9179
}
```

### Win Calculation Logic
```
1. Generate 6-move sequence using lookUpTable weights
2. Evaluate all possible subsequences (2-6 moves)
3. Find highest-paying match in paytable
4. Multiply by mode adjustment factor
5. Apply wincap if needed (5000x/7500x/10000x)
6. Return best win
```

### Paytable (Base Values)
See `game_config.py` lines 42-94 for complete paytable.

Key examples:
- **Minimum win:** 0.0212x (BWD-BWD)
- **Common wins:** 0.053x - 0.47x (2-3 move combos)
- **Knockout wins:** 14x - 233x (sequences ending in KO)
- **Legendary wins:** 467x - 2336x (complex KO combos)

---

## Symbols

| Symbol | Name | Type | Description |
|--------|------|------|-------------|
| **FWD** | Forward | Positioning | Move forward |
| **BWD** | Backward | Defensive | Move back |
| **PUN** | Punch | Basic Attack | Standard hit |
| **UPP** | Uppercut | Power Attack | Strong hit |
| **DUK** | Duck | Dodge | Defensive dodge |
| **HRT** | Hurt | Damage | Damage taken |
| **DIZ** | Dizzy | Stunned | Vulnerability |
| **KO** | Knockout | Finisher | Big win trigger |

---

## Verification

### Test Spins (Recommended)
Run these test sequences to verify integration:

1. **Minimum Win:** BWD-BWD = 0.0212x (Macron adjusted: 0.0220x)
2. **Common Win:** FWD-PUN = 0.053x (Macron adjusted: 0.0551x)
3. **Knockout Win:** UPP-KO = 23.369x (Macron adjusted: 24.28x)
4. **Max Win:** DUK-DUK-DUK-DUK-UPP-KO = 2336.6264x (capped at mode wincap)

### RTP Verification
After integration, run 1M+ spins per mode and verify:
- **Macron:** ~98% RTP (±0.5%)
- **Putin:** ~98% RTP (±0.5%)
- **Trump:** ~98% RTP (±0.5%)

---

## Optional Files (For Testing/Verification)

### Simulation Books (Not required for production)
**Paths:**
- `library/books/books_macron.json` (~11.9 MB)
- `library/books/books_putin.json`
- `library/books/books_trump.json`

Contains 100k simulated spins per mode for verification/testing.

### Source Code (Reference only)
- `game_config.py` - Paytable and configuration
- `game_override.py` - Game logic implementation
- `gamestate.py` - Spin execution
- `game_optimization.py` - Optimization parameters

---

## Upload Checklist

- [ ] `index.json`
- [ ] `lookUpTable_macron_0.csv`
- [ ] `lookUpTable_putin_0.csv`
- [ ] `lookUpTable_trump_0.csv`
- [ ] Backend implements mode RTP adjustments (1.0390, 1.0432, 0.9179)
- [ ] Backend implements paytable from game_config.py
- [ ] Backend implements "best win only" logic
- [ ] Wincaps configured (5000x, 7500x, 10000x)
- [ ] Test spins verify correct win calculation
- [ ] Long-run RTP test confirms 98% across all modes

---

## Support

**Math Configuration Date:** 2025-09-30
**SDK Version:** Python 3.12+
**Optimization:** Rust-based (completed)
**Status:** ✅ Production Ready

For questions or issues, reference:
- `games/beat_the_boss/game_config.py` - Complete configuration
- `games/beat_the_boss/test_all_modes.py` - RTP verification script
- This upload guide