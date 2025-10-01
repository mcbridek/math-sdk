"""Test redesigned paytable with 0.1x minimum."""

from gamestate import GameState
from game_config import GameConfig

# Temporarily override paytable with redesigned values
redesigned_paytable = {
    # Basic 2-move combos (common, visible wins)
    (2, "FWD-PUN"): 0.1,
    (2, "PUN-PUN"): 0.1,
    (2, "BWD-PUN"): 0.15,
    (2, "FWD-UPP"): 0.3,
    (2, "PUN-UPP"): 0.2,
    (2, "BWD-UPP"): 0.25,
    (2, "BWD-BWD"): 0.05,
    (2, "DUK-DUK"): 0.1,
    (2, "BWD-DUK"): 0.1,
    (2, "DUK-BWD"): 0.1,
    (2, "BWD-FWD"): 0.05,
    (2, "FWD-BWD"): 0.05,
    (2, "FWD-FWD"): 0.1,
    (2, "DUK-PUN"): 0.1,
    (2, "DUK-FWD"): 0.1,
    # 3-move combos (uncommon, medium wins)
    (3, "PUN-PUN-UPP"): 0.6,
    (3, "FWD-PUN-UPP"): 0.7,
    (2, "DUK-UPP"): 0.9,
    (3, "BWD-FWD-UPP"): 1.0,
    (3, "FWD-FWD-PUN"): 0.45,
    (3, "BWD-BWD-PUN"): 0.35,
    (3, "DUK-DUK-PUN"): 0.5,
    (3, "FWD-PUN-PUN"): 0.5,
    (3, "BWD-PUN-UPP"): 0.6,
    # 4-move expert combos (rare, larger wins)
    (3, "DUK-DUK-UPP"): 1.4,
    (4, "BWD-DUK-FWD-UPP"): 3.0,
    (4, "PUN-PUN-PUN-UPP"): 2.3,
    (4, "FWD-FWD-PUN-UPP"): 2.0,
    (4, "DUK-DUK-DUK-UPP"): 4.5,
    (4, "FWD-FWD-FWD-PUN"): 1.7,
    # Knockout sequences (very rare, big wins)
    (2, "UPP-KO"): 50.0,
    (2, "DUK-KO"): 100.0,
    (2, "PUN-KO"): 30.0,
    (3, "PUN-UPP-KO"): 75.0,
    (3, "DUK-UPP-KO"): 150.0,
    (4, "DUK-DUK-UPP-KO"): 250.0,
    (5, "BWD-DUK-FWD-UPP-KO"): 500.0,
    (4, "FWD-FWD-UPP-KO"): 200.0,
    # Legendary sequences (mythical, jackpot)
    (4, "HRT-DIZ-UPP-KO"): 1000.0,
    (5, "DUK-DUK-DUK-UPP-KO"): 5000.0,
    (5, "FWD-FWD-FWD-UPP-KO"): 5000.0,
    (6, "DUK-DUK-DUK-DUK-UPP-KO"): 5000.0,
}

if __name__ == "__main__":
    config = GameConfig()
    config.paytable = redesigned_paytable  # Override with redesigned values

    gamestate = GameState(config)
    gamestate.betmode = "macron"
    gamestate.criteria = "all_spins"

    total_rtp = 0.0
    num_spins = 100000
    wins_count = 0

    print(f"\n{'='*60}")
    print("TESTING REDESIGNED PAYTABLE (0.1x minimum)")
    print(f"{'='*60}\n")
    print(f"Running {num_spins:,} spins...")

    for sim in range(num_spins):
        gamestate.run_spin(sim)
        win = gamestate.final_win
        total_rtp += win / num_spins
        if win > 0:
            wins_count += 1

        if (sim + 1) % 10000 == 0:
            print(f"Progress: {sim+1:,}/{num_spins:,} - Current RTP: {total_rtp * 100:.2f}%")

    hit_rate = (wins_count / num_spins) * 100
    print(f"\n{'='*60}")
    print(f"RTP: {total_rtp * 100:.2f}%")
    print(f"Hit Rate: {hit_rate:.2f}%")
    print(f"Wins Found: {wins_count:,}/{num_spins:,}")
    print(f"{'='*60}\n")

    # Calculate adjustment needed
    if total_rtp * 100 != 98.0:
        adjustment = 98.0 / (total_rtp * 100)
        print(f"Adjustment needed: multiply paytable by {adjustment:.4f}")
        print(f"{'='*60}\n")