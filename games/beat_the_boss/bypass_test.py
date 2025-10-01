"""Test that bypasses distribution system entirely."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Set mode and criteria directly (mimicking distribution system)
    gamestate.betmode = "macron"
    gamestate.criteria = "all_spins"  # Use the all_spins criteria

    total_rtp = 0.0
    num_spins = 100000
    wins_count = 0

    print(f"\nRunning {num_spins:,} spins WITHOUT distribution system...")

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