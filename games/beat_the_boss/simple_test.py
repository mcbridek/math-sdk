"""Simple single-threaded test to verify win calculation."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Set mode
    gamestate.betmode = "macron"
    gamestate.criteria = "small_win"

    print("\n" + "="*60)
    print("SINGLE-THREADED TEST")
    print("="*60)

    total_rtp = 0.0
    num_spins = 10000

    wins_found = 0
    for sim in range(num_spins):
        gamestate.run_spin(sim)

        win = gamestate.final_win
        rtp_contribution = win / num_spins
        total_rtp += rtp_contribution

        if win > 0:
            wins_found += 1

        # Print progress every 1000 spins
        if (sim + 1) % 1000 == 0:
            print(f"Progress: {sim+1}/{num_spins} spins - Current RTP: {total_rtp * 100:.4f}%")

    hit_rate = (wins_found / num_spins) * 100
    print(f"\n{'='*60}")
    print(f"RTP across {num_spins} spins: {total_rtp * 100:.4f}%")
    print(f"Hit Rate: {hit_rate:.2f}%")
    print(f"Wins Found: {wins_found}/{num_spins}")
    print(f"{'='*60}\n")