"""Debug script to understand distribution system behavior."""

from gamestate import GameState
from game_config import GameConfig
import random

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Set mode
    gamestate.betmode = "macron"

    # Test with different criteria (updated to match current config)
    test_cases = [
        ("all_spins", 0),
        ("all_spins", 1),
        ("all_spins", 2),
        ("all_spins", 3),
        ("all_spins", 4),
    ]

    print("\n" + "="*80)
    print("DISTRIBUTION DEBUG TEST")
    print("="*80)

    for criteria, seed in test_cases:
        print(f"\n--- Testing criteria: {criteria} ---")

        gamestate.criteria = criteria

        # Get distribution info
        try:
            dist = gamestate.get_current_betmode_distributions()
            win_criteria = dist.get_win_criteria()
            conditions = dist.get_conditions()
            print(f"Win Criteria: {win_criteria}")
            print(f"Conditions: {conditions}")
        except Exception as e:
            print(f"ERROR getting distribution: {e}")
            continue

        # Run a single spin
        random.seed(seed)
        gamestate.reset_seed(seed)
        gamestate.repeat = True
        iteration = 0

        while gamestate.repeat and iteration < 10:
            iteration += 1
            gamestate.reset_book()
            gamestate.evaluate_finalwin()

            print(f"\n  Iteration {iteration}:")
            print(f"    Move Sequence: {gamestate.move_sequence}")
            print(f"    Final Win: {gamestate.final_win}")
            print(f"    Boss Health: {gamestate.boss_health}")
            print(f"    Knockout: {gamestate.knockout_achieved}")
            print(f"    Repeat Count: {gamestate.repeat_count}")

            # Check repeat logic
            gamestate.check_game_repeat()
            print(f"    Repeat Flag: {gamestate.repeat}")

        if iteration >= 10:
            print(f"\n  WARNING: Hit max iterations without satisfying criteria!")

        print(f"\n  Final Result:")
        print(f"    Win Amount: {gamestate.final_win}")
        print(f"    Expected: {win_criteria}")
        print(f"    Match: {gamestate.final_win == win_criteria if win_criteria else 'N/A'}")

    print("\n" + "="*80)
    print("DEBUG TEST COMPLETE")
    print("="*80 + "\n")