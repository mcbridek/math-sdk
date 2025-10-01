"""Test optimized RTPs using the generated lookup tables."""

from gamestate import GameState
from game_config import GameConfig
import random

if __name__ == "__main__":
    config = GameConfig()

    # Set seed for reproducibility
    random.seed(42)

    modes = ["macron", "putin", "trump"]

    print("\n" + "="*60)
    print("TESTING OPTIMIZED CONFIGURATIONS")
    print("="*60)

    num_spins = 100000

    for mode in modes:
        print(f"\n{mode.upper()} Mode - Optimized Configuration:")
        print("="*60)

        gamestate = GameState(config)
        gamestate.betmode = mode
        gamestate.criteria = "all_spins"

        total_multiplier = 0.0
        wins_count = 0

        for sim in range(num_spins):
            gamestate.run_spin(sim)
            win = gamestate.final_win

            total_multiplier += win
            if win > 0:
                wins_count += 1

            if (sim + 1) % 20000 == 0:
                current_rtp = (total_multiplier / (sim + 1)) * 100
                print(f"  Progress: {sim+1:,}/{num_spins:,} - Current RTP: {current_rtp:.2f}%")

        rtp = (total_multiplier / num_spins) * 100
        hit_rate = (wins_count / num_spins) * 100

        print(f"\nFinal Results:")
        print(f"  RTP: {rtp:.2f}% (target: 98.00%)")
        print(f"  Hit Rate: {hit_rate:.2f}%")
        print(f"  Avg Multiplier: {total_multiplier/num_spins:.4f}x")
        print(f"  Deviation from target: {rtp - 98:.2f}%")
        print("="*60)

    print("\n" + "="*60)
    print("OPTIMIZATION VERIFICATION COMPLETE")
    print("="*60 + "\n")