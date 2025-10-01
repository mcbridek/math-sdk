"""Test Putin mode bypassing distribution system entirely."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Set Putin mode and criteria directly (mimicking distribution system)
    gamestate.betmode = "putin"
    gamestate.criteria = "all_spins"  # Use the all_spins criteria

    total_rtp = 0.0
    num_spins = 100000
    wins_count = 0
    max_win = 0.0

    print(f"\n{'='*60}")
    print(f"PUTIN MODE TEST - Balanced Fighter")
    print(f"Cost: 2x | Max Win: 7500x | Style: Tactical & Unpredictable")
    print(f"{'='*60}")
    print(f"\nRunning {num_spins:,} spins WITHOUT distribution system...")

    for sim in range(num_spins):
        gamestate.run_spin(sim)

        win = gamestate.final_win
        total_rtp += win / num_spins

        if win > 0:
            wins_count += 1
            if win > max_win:
                max_win = win

        if (sim + 1) % 10000 == 0:
            print(f"Progress: {sim+1:,}/{num_spins:,} - Current RTP: {total_rtp * 100:.2f}% - Max Win: {max_win:.2f}x")

    hit_rate = (wins_count / num_spins) * 100
    print(f"\n{'='*60}")
    print(f"PUTIN MODE - FINAL RESULTS")
    print(f"{'='*60}")
    print(f"RTP: {total_rtp * 100:.2f}%")
    print(f"Hit Rate: {hit_rate:.2f}%")
    print(f"Wins Found: {wins_count:,}/{num_spins:,}")
    print(f"Max Win: {max_win:.2f}x")
    print(f"{'='*60}\n")