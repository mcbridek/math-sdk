"""Debug Trump mode to understand why RTP is low."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)
    gamestate.betmode = "trump"
    gamestate.criteria = "all_spins"

    print("\n" + "="*60)
    print("DEBUGGING TRUMP MODE")
    print("="*60)

    # Get bet mode details
    current_mode = gamestate.get_current_betmode()
    print(f"\nBet Mode: {current_mode.get_name()}")
    print(f"Bet Cost: {current_mode.get_cost()}")
    print(f"Win Cap: {current_mode.get_wincap()}")

    # Run 10 spins and check sequences
    print("\n" + "="*60)
    print("Sample Spins:")
    print("="*60)

    for i in range(10):
        gamestate.run_spin(i)

        print(f"\nSpin {i+1}:")
        print(f"  Sequence: {'-'.join(gamestate.move_sequence)}")
        print(f"  Final Win: {gamestate.final_win:.4f}x")
        print(f"  Boss Health: {gamestate.boss_health:.1f}")

        if len(gamestate.sequence_wins) > 0:
            print(f"  Winning sequences found: {len(gamestate.sequence_wins)}")
            for win_info in gamestate.sequence_wins:
                print(f"    - {win_info['sequence']}: base={win_info['base_multiplier']:.4f}x, final={win_info['final_multiplier']:.4f}x")

    print("\n" + "="*60)