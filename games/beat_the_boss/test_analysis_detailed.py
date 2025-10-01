"""Detailed analysis comparing all three boss modes."""

from gamestate import GameState
from game_config import GameConfig
from collections import Counter

def analyze_mode(mode_name, num_spins=100000):
    """Run comprehensive analysis for a specific mode."""
    config = GameConfig()
    gamestate = GameState(config)

    gamestate.betmode = mode_name
    gamestate.criteria = "all_spins"

    total_rtp = 0.0
    wins_count = 0
    max_win = 0.0
    win_amounts = []
    sequences_found = Counter()

    print(f"\n{'='*60}")
    print(f"{mode_name.upper()} MODE - DETAILED ANALYSIS")
    print(f"{'='*60}")

    for sim in range(num_spins):
        gamestate.run_spin(sim)

        win = gamestate.final_win
        total_rtp += win / num_spins

        if win > 0:
            wins_count += 1
            win_amounts.append(win)
            if win > max_win:
                max_win = win

            # Track sequences
            sequence = "-".join(gamestate.move_sequence)
            sequences_found[sequence] += 1

        if (sim + 1) % 20000 == 0:
            print(f"Progress: {sim+1:,}/{num_spins:,} - RTP: {total_rtp * 100:.2f}%")

    hit_rate = (wins_count / num_spins) * 100

    # Calculate win distribution
    win_amounts.sort()
    avg_win = sum(win_amounts) / len(win_amounts) if win_amounts else 0

    # Find common winning sequences
    top_sequences = sequences_found.most_common(10)

    print(f"\n{'-'*60}")
    print(f"RESULTS:")
    print(f"  RTP: {total_rtp * 100:.2f}%")
    print(f"  Hit Rate: {hit_rate:.2f}%")
    print(f"  Total Wins: {wins_count:,}/{num_spins:,}")
    print(f"  Max Win: {max_win:.2f}x")
    print(f"  Avg Win (when winning): {avg_win:.4f}x")
    print(f"\nTop 10 Winning Sequences:")
    for seq, count in top_sequences[:10]:
        print(f"  {count:>6,}x - {seq[:50]}...")

    return {
        "mode": mode_name,
        "rtp": total_rtp * 100,
        "hit_rate": hit_rate,
        "max_win": max_win,
        "avg_win": avg_win,
        "total_wins": wins_count,
    }

if __name__ == "__main__":
    results = []

    # Test all three modes
    results.append(analyze_mode("macron", 100000))
    results.append(analyze_mode("putin", 100000))
    results.append(analyze_mode("trump", 100000))

    # Summary comparison
    print(f"\n{'='*60}")
    print(f"COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Mode':<10} {'RTP':<10} {'Hit Rate':<12} {'Max Win':<12} {'Avg Win':<12}")
    print(f"{'-'*60}")
    for r in results:
        print(f"{r['mode']:<10} {r['rtp']:>6.2f}%   {r['hit_rate']:>6.2f}%     {r['max_win']:>8.2f}x   {r['avg_win']:>8.4f}x")
    print(f"{'='*60}\n")