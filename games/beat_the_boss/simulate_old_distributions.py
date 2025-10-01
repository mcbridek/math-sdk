"""Simulate the bug with OLD distribution system that had win_criteria."""

from gamestate import GameState
from game_config import GameConfig
from src.config.distributions import Distribution
import random

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    # Temporarily modify distribution to have win_criteria (simulate old system)
    print("\n" + "="*80)
    print("SIMULATING OLD DISTRIBUTION SYSTEM BUG")
    print("="*80)
    print("\nModifying distributions to include win_criteria...")

    # Replace macron mode distributions with old-style ones
    old_distributions = [
        Distribution(
            criteria="loss",
            quota=0.30,
            win_criteria=0.0,  # Force 0x wins
            conditions={
                "reel_weights": {
                    config.basegame_type: {"MACRON_BASE": 1},
                },
            },
        ),
        Distribution(
            criteria="small_win",
            quota=0.45,
            win_criteria=1.0,  # Force 1x wins
            conditions={
                "reel_weights": {
                    config.basegame_type: {"MACRON_BASE": 1},
                },
                "basic_sequences": True,
            },
        ),
    ]

    # Replace distributions
    for betmode in config.bet_modes:
        if betmode.get_name() == "macron":
            betmode._distributions = old_distributions
            break

    gamestate.betmode = "macron"

    # Test both criteria
    test_cases = [
        ("loss", 5, 0.0),
        ("small_win", 10, 1.0),
    ]

    for criteria_name, seed, expected_win in test_cases:
        print(f"\n{'='*80}")
        print(f"Testing criteria: {criteria_name} (expected win: {expected_win}x)")
        print(f"{'='*80}")

        gamestate.criteria = criteria_name
        random.seed(seed)
        gamestate.reset_seed(seed)

        # Manually trace the repeat loop
        gamestate.repeat = True
        iteration = 0
        max_iterations = 100

        print(f"\nStarting repeat loop...")

        while gamestate.repeat and iteration < max_iterations:
            iteration += 1

            print(f"\n  Iteration {iteration}:")
            print(f"    Before reset_book():")
            print(f"      spin_win = {gamestate.win_manager.spin_win}")
            print(f"      running_bet_win = {gamestate.win_manager.running_bet_win}")

            gamestate.reset_book()

            print(f"    After reset_book():")
            print(f"      spin_win = {gamestate.win_manager.spin_win}")
            print(f"      running_bet_win = {gamestate.win_manager.running_bet_win}")

            gamestate.evaluate_finalwin()

            print(f"    After evaluate_finalwin():")
            print(f"      final_win = {gamestate.final_win}")
            print(f"      spin_win = {gamestate.win_manager.spin_win}")
            print(f"      running_bet_win = {gamestate.win_manager.running_bet_win}")
            print(f"      repeat = {gamestate.repeat}")

            gamestate.check_game_repeat()

            print(f"    After check_game_repeat():")
            print(f"      repeat = {gamestate.repeat}")
            print(f"      repeat_count = {gamestate.repeat_count}")

            if iteration >= 10:
                print(f"\n  Stopping after 10 iterations to prevent infinite loop")
                break

        print(f"\n  Final Results:")
        print(f"    Iterations: {iteration}")
        print(f"    Final win: {gamestate.final_win}x")
        print(f"    Expected: {expected_win}x")
        print(f"    Match: {gamestate.final_win == expected_win}")
        print(f"    running_bet_win: {gamestate.win_manager.running_bet_win}x")

        if iteration >= max_iterations:
            print(f"\n  WARNING: Hit max iterations! Infinite loop detected!")

    print(f"\n{'='*80}")
    print(f"SIMULATION COMPLETE")
    print(f"{'='*80}\n")