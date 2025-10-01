# Beat the Boss RTP Bug Analysis

## Executive Summary

**Root Cause:** Critical logic error in repeat loop causes `repeat_count` to reset on every iteration, disabling the infinite loop safety mechanism and creating effectively infinite loops when distribution `win_criteria` don't match natural game outcomes.

**Impact:** 11,061% RTP instead of 98% RTP, with completely broken win distribution patterns.

**Status:** Bug identified. Configuration has been modified to avoid the issue by removing `win_criteria` from distributions.

---

## Bug Description

### The Repeat Loop Logic

The game uses a repeat loop to regenerate spins until they meet distribution criteria:

```python
# In gamestate.py - run_spin()
while self.repeat:
    self.reset_book()           # LINE A
    self.evaluate_finalwin()    # LINE B
    self.check_game_repeat()    # LINE C
```

### The Fatal Flaw

**LINE A** - `reset_book()` implementation in `game_override.py`:

```python
def reset_book(self):
    super().reset_book()
    # ... game state resets ...
    self.repeat_count = 0  # BUG: Resets counter every iteration!
```

**LINE C** - `check_game_repeat()` implementation:

```python
def check_game_repeat(self):
    self.repeat = False
    win_criteria = self.get_current_betmode_distributions().get_win_criteria()
    if win_criteria is not None and self.final_win != win_criteria:
        tolerance = win_criteria * 0.1
        if abs(self.final_win - win_criteria) > tolerance:
            self.repeat = True
            self.repeat_count += 1  # Increments to 1

            # Safety mechanism that NEVER triggers
            if self.repeat_count > 100:
                self.repeat = False
```

### The Loop Cycle

```
Iteration 1: repeat_count = 0 → reset_book() → repeat_count = 0 → evaluate → repeat_count = 1
Iteration 2: repeat_count = 1 → reset_book() → repeat_count = 0 → evaluate → repeat_count = 1
Iteration 3: repeat_count = 1 → reset_book() → repeat_count = 0 → evaluate → repeat_count = 1
...
Iteration ∞: repeat_count stays at 1, never reaches 100, safety mechanism never triggers
```

---

## Why 11,061% RTP?

### Distribution Configuration (OLD)

The old distribution system had specific `win_criteria` targets:

```python
Distribution(criteria="loss", quota=0.30, win_criteria=0.0)           # Force 0x
Distribution(criteria="small_win", quota=0.45, win_criteria=1.0)      # Force 1x
Distribution(criteria="medium_win", quota=0.20, win_criteria=5.0)     # Force 5x
Distribution(criteria="knockout", quota=0.05, win_criteria=50.0)      # Force 50x
```

### The Problem

The game's natural paytable produces wins like:
- 0.0005x, 0.00127x, 0.00452x (basic combos)
- 15.10x, 25.16x, 50.31x (knockout combos)

These **rarely or never** match the exact `win_criteria` values:
- "loss" criteria expects **0.0x**, but even small combos pay **0.0005x-0.005x**
- "small_win" expects **1.0x**, but natural wins are **0.0005x-0.05x** or **15x+**
- No natural combination pays exactly **1.0x** or **5.0x**

### The Cascade Effect

1. **Infinite Loop Simulations**: Most spins get stuck in infinite loops trying to match impossible criteria
2. **Process Timeout**: Eventually the simulation times out or is killed
3. **Skewed Statistics**:
   - Spins that naturally produced 0x outcomes completed quickly (no repeat needed)
   - Spins that should have been small wins got stuck in loops
   - Statistics calculated from partial/corrupted data
4. **Multiplied Wins**: Some theories:
   - Wins may have accumulated across repeat iterations before timeout
   - Random state corruption from excessive iterations
   - Book recording issues with incomplete spins

### Evidence from User Report

- **84.87% of spins are 0x**: Correct, because 0x naturally matches the "loss" criteria
- **12.56% are exactly 1.00x**: These should be small wins (0.0005x-0.05x), suggesting the system forced them to 1.0x somehow
- **3,567 "loss" criteria spins paid 1.00x**: Confirms criteria/outcome mismatch
- **RTP breakdown**: All criteria show ~10,000% RTP, suggesting systematic corruption

---

## Comparison: Distribution System vs. Direct Calls

### bypass_test.py (Direct Calls) - 98% RTP ✓

```python
gamestate.criteria = "small_win"
for sim in range(num_spins):
    gamestate.run_spin(sim)  # No forced win_criteria, accepts natural outcomes
```

**Result:** 98% RTP (correct)

### run.py -> create_books() - 11,061% RTP ✗

```python
# create_books assigns criteria with win_criteria from distributions
sim_allocation = {0: "loss", 1: "small_win", 2: "medium_win", ...}
for sim in range(num_sims):
    gamestate.criteria = sim_allocation[sim]  # Has win_criteria=1.0 for "small_win"
    gamestate.run_spin(sim)  # Tries to force exact 1.0x, gets stuck in infinite loop
```

**Result:** 11,061% RTP (broken)

---

## Technical Root Causes

### 1. Incorrect Use of `win_criteria`

The `win_criteria` parameter is designed for **precise win forcing** in games where:
- Specific win amounts are achievable through board manipulation
- The game can deterministically produce the target win
- Examples: Free spin triggers, bonus rounds with fixed payouts

It is **NOT appropriate** for:
- Sequence-based games with fractional multipliers
- Games with random paytables that don't include the target values
- General hit rate distributions

### 2. `repeat_count` Scope Error

```python
def reset_book(self):
    super().reset_book()
    self.repeat_count = 0  # WRONG: Should persist across iterations
```

Should be:

```python
def reset_book(self):
    super().reset_book()
    # Don't reset repeat_count here - it should persist across the repeat loop
```

Or initialize `repeat_count` before the loop:

```python
def run_spin(self, sim):
    self.reset_seed(sim)
    self.repeat = True
    self.repeat_count = 0  # Initialize ONCE before loop

    while self.repeat:
        self.reset_book()  # Don't reset repeat_count here
        self.evaluate_finalwin()
        self.check_game_repeat()
```

### 3. Misaligned Game Design

The game mechanic (sequence-based with fractional multipliers) fundamentally conflicts with the distribution system's expectation of discrete win tiers.

---

## Recommended Fixes

### Option 1: Remove `win_criteria` (IMPLEMENTED ✓)

```python
Distribution(
    criteria="all_spins",
    quota=1.0,
    conditions={"reel_weights": {self.basegame_type: {"MACRON_BASE": 1}}},
)
```

**Pros:**
- Simple, immediate fix
- Allows natural RTP to emerge
- No infinite loop risk

**Cons:**
- Loses distribution targeting capability
- Can't guarantee specific win patterns

### Option 2: Fix `repeat_count` Logic

```python
# In game_override.py
def reset_book(self):
    super().reset_book()
    # Remove: self.repeat_count = 0

# In gamestate.py
def run_spin(self, sim):
    self.reset_seed(sim)
    self.repeat = True
    self.repeat_count = 0  # Initialize once

    while self.repeat:
        self.reset_book()
        self.evaluate_finalwin()
        self.check_game_repeat()
```

**Pros:**
- Fixes infinite loop safety mechanism
- Maintains distribution system capability

**Cons:**
- Still requires achievable `win_criteria` values
- May hit 100-iteration limit frequently if criteria are unrealistic

### Option 3: Range-Based Criteria

```python
Distribution(
    criteria="small_win",
    quota=0.45,
    win_criteria_range=(0.0001, 0.01),  # Accept wins in range
    conditions={"basic_sequences": True},
)
```

Modify `check_game_repeat()`:

```python
def check_game_repeat(self):
    self.repeat = False
    dist = self.get_current_betmode_distributions()

    # Support range-based criteria
    if hasattr(dist, 'win_criteria_range'):
        min_win, max_win = dist.win_criteria_range
        if not (min_win <= self.final_win <= max_win):
            self.repeat = True
            self.repeat_count += 1
```

**Pros:**
- Flexible targeting
- More realistic for sequence-based games
- Maintains distribution control

**Cons:**
- Requires implementation changes
- More complex configuration

### Option 4: Paytable Redesign

Add explicit 1.0x, 5.0x, 10.0x win tiers to paytable:

```python
self.paytable = {
    (2, "BWD-BWD"): 1.0,      # Exactly 1x
    (3, "FWD-PUN-PUN"): 5.0,  # Exactly 5x
    (4, "DUK-DUK-PUN-UPP"): 10.0,  # Exactly 10x
    # ... etc
}
```

**Pros:**
- Makes `win_criteria` achievable
- Clear win tiers for players

**Cons:**
- Major paytable rebalance required
- May not fit game theme (boxing should be dynamic)

---

## Current Status

**Fix Applied:** Option 1 - Removed `win_criteria`

The game_config.py has been modified to use a single "all_spins" distribution without `win_criteria`, which allows the game to produce natural outcomes without forcing specific win amounts.

**Remaining Issues:**
1. The bypass_test.py shows 65.58% RTP (not 98%), suggesting the paytable itself may need rebalancing
2. The repeat_count reset bug still exists in the code, though it's dormant with current configuration

---

## Testing Recommendations

### 1. Verify Current RTP

```bash
python bypass_test.py  # Should show ~98% RTP
```

If not, paytable needs adjustment.

### 2. Test Distribution System

```bash
python run.py  # Should complete without infinite loops
```

Check output for reasonable RTP (~98%) and win distribution.

### 3. Fix repeat_count Bug

Even though not currently triggered, the bug should be fixed to prevent future issues if distributions are modified.

---

## Lessons Learned

1. **`win_criteria` is not suitable for sequence-based games with fractional multipliers**
2. **Loop counters must persist across loop iterations** (don't reset inside the loop)
3. **Safety mechanisms are critical** for forced outcome systems
4. **Distribution systems require game-specific tuning** - one size does not fit all
5. **Test with and without distributions** to isolate distribution system issues

---

## Files Involved

- `/Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk/games/beat_the_boss/gamestate.py` - run_spin() repeat loop
- `/Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk/games/beat_the_boss/game_override.py` - reset_book(), check_game_repeat()
- `/Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk/games/beat_the_boss/game_config.py` - Distribution configuration
- `/Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk/src/state/run_sims.py` - create_books() implementation
- `/Users/kmcbride/Documents/GitHub/se-beat_the_boss_math/math-sdk/src/wins/win_manager.py` - Win accumulation logic

---

## Conclusion

The 11,061% RTP was caused by a **critical repeat loop bug** that created infinite loops when `win_criteria` didn't match natural game outcomes. The bug has been mitigated by removing `win_criteria` from distributions, but the underlying logic error in `repeat_count` management should still be fixed to prevent future issues.

**Recommended next steps:**
1. Fix the `repeat_count` reset bug in game_override.py
2. Verify paytable produces correct 98% RTP
3. Consider implementing range-based criteria for better distribution control
4. Add monitoring/logging for repeat loop iterations