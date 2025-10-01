"""Debug test to understand what's happening in the game."""

from gamestate import GameState
from game_config import GameConfig

if __name__ == "__main__":
    # Initialize
    config = GameConfig()
    gamestate = GameState(config)

    # Set to macron mode
    gamestate.betmode = "macron"
    gamestate.criteria = "small_win"

    print("\n" + "="*60)
    print("DEBUG TEST - Single Spin")
    print("="*60)

    # Check paytable
    print("\nPaytable entries:")
    for key, value in list(config.paytable.items())[:10]:
        print(f"  {key}: {value}x")

    # Check reels
    print(f"\nMACRON_BASE reel has {len(config.reels['MACRON_BASE'][0])} symbols")
    print(f"First 10 symbols: {config.reels['MACRON_BASE'][0][:10]}")

    # Run a single spin manually
    print("\n" + "-"*60)
    print("Running single spin...")
    print("-"*60)

    gamestate.reset_seed(1)
    gamestate.reset_book()

    # Generate moves
    print(f"\nGenerating {gamestate.max_sequence_length} moves:")
    for i in range(gamestate.max_sequence_length):
        move = gamestate.generate_move()
        gamestate.move_sequence.append(move)
        print(f"  Move {i+1}: {move}")

        # Check for matches after each move
        if len(gamestate.move_sequence) >= 2:
            result = gamestate.evaluate_move_sequence()
            if result:
                print(f"    ✓ MATCH FOUND: {result['sequence']} = {result['final_multiplier']}x")

    print(f"\nFinal sequence: {'-'.join(gamestate.move_sequence)}")
    print(f"Total sequence wins: {len(gamestate.sequence_wins)}")

    if gamestate.sequence_wins:
        print("\nWins found:")
        for win in gamestate.sequence_wins:
            print(f"  {win['sequence']}: {win['final_multiplier']}x")
    else:
        print("\n⚠ No wins found - checking why...")

        # Try to manually check some sequences
        print("\nManual sequence checks:")
        seq = gamestate.move_sequence
        for length in range(2, len(seq) + 1):
            subseq = seq[:length]
            subseq_str = "-".join(subseq)
            key = (length, subseq_str)
            if key in config.paytable:
                print(f"  Found match: {key} = {config.paytable[key]}x")
            else:
                print(f"  No match: {key}")

    print("\n" + "="*60)