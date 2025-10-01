"""Trace the actual bug causing 11,061% RTP."""

from gamestate import GameState
from game_config import GameConfig
import random

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Set mode
    gamestate.betmode = "macron"
    gamestate.criteria = "all_spins"

    print("\n" + "="*80)
    print("BUG TRACE - Following the repeat loop")
    print("="*80)

    # Run multiple spins and track wins
    total_rtp = 0.0
    num_spins = 100

    win_distribution = {}
    repeat_counts = []

    for sim in range(num_spins):
        # Reset and run spin
        gamestate.run_spin(sim)

        win = gamestate.final_win
        total_rtp += win / num_spins

        # Track win amounts
        win_key = f"{win:.4f}x"
        win_distribution[win_key] = win_distribution.get(win_key, 0) + 1

        # Track repeat counts
        repeat_counts.append(gamestate.repeat_count)

        if sim < 10 or win > 1.0:
            print(f"\nSpin {sim}:")
            print(f"  Criteria: {gamestate.criteria}")
            print(f"  Final Win: {win}")
            print(f"  Move Sequence: {gamestate.move_sequence}")
            print(f"  Repeat Count: {gamestate.repeat_count}")
            print(f"  Boss Health: {gamestate.boss_health}")
            print(f"  Knockout: {gamestate.knockout_achieved}")

    print(f"\n{'='*80}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*80}")
    print(f"RTP: {total_rtp * 100:.2f}%")
    print(f"Average Repeat Count: {sum(repeat_counts)/len(repeat_counts):.2f}")
    print(f"Max Repeat Count: {max(repeat_counts)}")
    print(f"\nWin Distribution (top 20):")
    sorted_wins = sorted(win_distribution.items(), key=lambda x: x[1], reverse=True)
    for win_amt, count in sorted_wins[:20]:
        print(f"  {win_amt}: {count} spins ({count/num_spins*100:.1f}%)")
    print(f"{'='*80}\n")