"""Quick test run for Beat the Boss with minimal simulations."""

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    # Minimal test settings
    num_threads = 2
    batching_size = 100
    compression = False
    profiling = False

    # 1000 simulations for better RTP estimate
    num_sim_args = {
        "macron": 1000,
    }

    # Initialize
    config = GameConfig()
    gamestate = GameState(config)

    print("\n" + "="*60)
    print("BEAT THE BOSS - QUICK TEST RUN")
    print("="*60)
    print(f"Simulations: {num_sim_args}")
    print("="*60 + "\n")

    # Run minimal simulations
    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")