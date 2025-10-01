"""Test all three boss modes to check current RTP and hit rates."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    config = GameConfig()

    # Test all three modes
    test_modes = ["macron", "putin", "trump"]

    print(f"\n{'='*60}")
    print("TESTING ALL BOSS MODES")
    print(f"{'='*60}\n")

    num_spins = 100000  # Larger sample for stable RTP measurement

    for mode in test_modes:
        print(f"\nTesting {mode.upper()} mode...")
        print(f"{'='*60}")

        gamestate = GameState(config)
        gamestate.betmode = mode
        gamestate.criteria = "all_spins"

        # Get bet cost for this mode
        bet_cost = config.boss_config[mode]["max_win"] / 5000  # Hacky way to get cost
        # Actually, let's get it properly
        for bet_mode in config.bet_modes:
            if bet_mode.get_name() == mode:
                bet_cost = bet_mode.get_cost()
                break

        total_wins = 0.0
        total_bets = 0.0
        wins_count = 0

        for sim in range(num_spins):
            gamestate.run_spin(sim)
            win_multiplier = gamestate.final_win

            # RTP is calculated directly from multipliers
            # Multipliers are always relative to the bet, so RTP = avg multiplier
            total_wins += win_multiplier

            if win_multiplier > 0:
                wins_count += 1

            if (sim + 1) % 10000 == 0:
                print(f"Progress: {sim+1:,}/{num_spins:,}")

        hit_rate = (wins_count / num_spins) * 100
        avg_multiplier = total_wins / num_spins
        rtp = avg_multiplier * 100

        print(f"\nResults for {mode.upper()}:")
        print(f"  Bet Cost: {bet_cost}x")
        print(f"  RTP: {rtp:.2f}%")
        print(f"  Hit Rate: {hit_rate:.2f}%")
        print(f"  Target Hit Rate: {config.boss_config[mode]['hit_rate_target'] * 100:.0f}%")
        print(f"  Wins: {wins_count:,}/{num_spins:,}")
        print(f"  Avg Multiplier: {avg_multiplier:.4f}x")
        print(f"{'='*60}\n")