"""Detailed analysis of why Trump RTP is low."""

from gamestate import GameState
from game_config import GameConfig
import random

if __name__ == "__main__":
    # Set seed for reproducibility
    random.seed(42)

    config = GameConfig()

    modes = ["macron", "putin", "trump"]

    print("\n" + "="*60)
    print("DETAILED RTP ANALYSIS")
    print("="*60)

    num_spins = 10000

    for mode in modes:
        gamestate = GameState(config)
        gamestate.betmode = mode
        gamestate.criteria = "all_spins"

        total_multiplier = 0.0
        wins_count = 0
        wincap_hits = 0

        # Track win distribution
        win_buckets = {
            "0": 0,
            "0.01-0.1": 0,
            "0.1-0.5": 0,
            "0.5-2": 0,
            "2-10": 0,
            "10+": 0,
        }

        for sim in range(num_spins):
            gamestate.run_spin(sim)
            win = gamestate.final_win

            total_multiplier += win
            if win > 0:
                wins_count += 1

                # Check wincap
                if hasattr(gamestate, 'wincap_triggered') and gamestate.wincap_triggered:
                    wincap_hits += 1

                # Bucket wins
                if win < 0.01:
                    win_buckets["0"] += 1
                elif win < 0.1:
                    win_buckets["0.01-0.1"] += 1
                elif win < 0.5:
                    win_buckets["0.1-0.5"] += 1
                elif win < 2:
                    win_buckets["0.5-2"] += 1
                elif win < 10:
                    win_buckets["2-10"] += 1
                else:
                    win_buckets["10+"] += 1

        rtp = (total_multiplier / num_spins) * 100
        hit_rate = (wins_count / num_spins) * 100

        print(f"\n{mode.upper()} Mode:")
        print(f"  RTP: {rtp:.2f}%")
        print(f"  Hit Rate: {hit_rate:.2f}%")
        print(f"  Avg Multiplier: {total_multiplier/num_spins:.4f}x")
        print(f"  Wincap hits: {wincap_hits}")

        print(f"\n  Win Distribution:")
        for bucket, count in win_buckets.items():
            if count > 0:
                pct = (count / num_spins) * 100
                print(f"    {bucket:10s}: {count:5,} ({pct:5.2f}%)")

        print(f"{'='*60}")