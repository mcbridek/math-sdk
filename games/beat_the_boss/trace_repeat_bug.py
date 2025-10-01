"""Trace the repeat loop bug in detail."""

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
    print("REPEAT LOOP BUG TRACE")
    print("="*80)

    # Manually trace through one spin with repeat loop
    sim = 42
    print(f"\nManually executing spin {sim} step by step:")
    print("-" * 80)

    # Step 1: reset_seed
    gamestate.reset_seed(sim)
    print(f"\n1. reset_seed({sim})")
    print(f"   win_manager.spin_win = {gamestate.win_manager.spin_win}")
    print(f"   win_manager.running_bet_win = {gamestate.win_manager.running_bet_win}")

    # Step 2: Set repeat = True
    gamestate.repeat = True
    print(f"\n2. Set repeat = True")

    # Step 3: Enter while loop
    iteration = 0
    while gamestate.repeat and iteration < 5:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"REPEAT LOOP ITERATION {iteration}")
        print(f"{'='*80}")

        # Step 3a: reset_book
        print(f"\n  3a. Before reset_book():")
        print(f"      win_manager.spin_win = {gamestate.win_manager.spin_win}")
        print(f"      win_manager.running_bet_win = {gamestate.win_manager.running_bet_win}")

        gamestate.reset_book()

        print(f"\n  3b. After reset_book():")
        print(f"      win_manager.spin_win = {gamestate.win_manager.spin_win}")
        print(f"      win_manager.running_bet_win = {gamestate.win_manager.running_bet_win}")

        # Step 3c: evaluate_finalwin
        print(f"\n  3c. Before evaluate_finalwin():")
        print(f"      win_manager.spin_win = {gamestate.win_manager.spin_win}")

        gamestate.evaluate_finalwin()

        print(f"\n  3d. After evaluate_finalwin():")
        print(f"      final_win = {gamestate.final_win}")
        print(f"      win_manager.spin_win = {gamestate.win_manager.spin_win}")
        print(f"      win_manager.running_bet_win = {gamestate.win_manager.running_bet_win}")
        print(f"      move_sequence = {gamestate.move_sequence}")

        # Step 3e: check_game_repeat
        print(f"\n  3e. Before check_game_repeat():")
        print(f"      repeat = {gamestate.repeat}")

        gamestate.check_game_repeat()

        print(f"\n  3f. After check_game_repeat():")
        print(f"      repeat = {gamestate.repeat}")
        print(f"      repeat_count = {gamestate.repeat_count}")

    # Step 4: imprint_wins
    print(f"\n{'='*80}")
    print(f"FINAL STEP: imprint_wins()")
    print(f"{'='*80}")
    print(f"\n  Before imprint_wins():")
    print(f"    final_win = {gamestate.final_win}")
    print(f"    win_manager.spin_win = {gamestate.win_manager.spin_win}")
    print(f"    win_manager.running_bet_win = {gamestate.win_manager.running_bet_win}")

    gamestate.imprint_wins()

    print(f"\n  After imprint_wins():")
    print(f"    win_manager.basegame_wins = {gamestate.win_manager.basegame_wins}")
    print(f"    win_manager.freegame_wins = {gamestate.win_manager.freegame_wins}")
    print(f"    win_manager.total_cumulative_wins = {gamestate.win_manager.total_cumulative_wins}")

    print(f"\n{'='*80}")
    print(f"FINAL RESULT:")
    print(f"  Final win recorded: {gamestate.final_win}x")
    print(f"  Iterations: {iteration}")
    print(f"{'='*80}\n")