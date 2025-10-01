"""Main file for generating results for Beat the Boss boxing game."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    # Performance settings
    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True  # Compress books for smaller file size
    profiling = False

    # Simulation counts for each boss mode
    num_sim_args = {
        "macron": int(1e5),   # 100,000 simulations for base mode
        "putin": int(1e5),    # 100,000 simulations for medium mode
        "trump": int(1e5),    # 100,000 simulations for high mode
    }

    # Control which steps to run
    run_conditions = {
        "run_sims": True,           # Generate simulation books
        "run_optimization": False,  # Skip optimization (already done)
        "run_analysis": False,      # Generate analytics
        "upload_data": False,       # Upload to AWS (requires credentials)
    }

    # Target all three boss modes
    target_modes = ["macron", "putin", "trump"]

    # Initialize game configuration and state
    config = GameConfig()
    gamestate = GameState(config)

    # Setup optimization parameters
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    # Step 1: Generate simulation books
    if run_conditions["run_sims"]:
        print("\n" + "="*60)
        print("BEAT THE BOSS - SIMULATION START")
        print("="*60)
        print(f"Modes: {target_modes}")
        print(f"Simulations per mode: {num_sim_args}")
        print(f"Threads: {num_threads}")
        print(f"Compression: {compression}")
        print("="*60 + "\n")

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
        print("SIMULATION COMPLETE")
        print("="*60 + "\n")

    # Step 2: Generate configuration files and lookup tables
    print("Generating configuration files...")
    generate_configs(gamestate)
    print("Configuration files generated.\n")

    # Step 3: Run optimization (optional - requires Rust setup)
    if run_conditions["run_optimization"]:
        print("\n" + "="*60)
        print("OPTIMIZATION START")
        print("="*60 + "\n")

        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)

        # Regenerate configs with optimized reel weights
        generate_configs(gamestate)

        print("\n" + "="*60)
        print("OPTIMIZATION COMPLETE")
        print("="*60 + "\n")

    # Step 4: Generate analytics (optional)
    if run_conditions["run_analysis"]:
        print("\n" + "="*60)
        print("ANALYTICS START")
        print("="*60 + "\n")

        custom_keys = [
            {"move": "KO"},      # Knockout sequences
            {"move": "DUK"},     # Defensive moves
            {"move": "UPP"},     # Power attacks
        ]

        create_stat_sheet(config.game_id, custom_keys=custom_keys)

        print("\n" + "="*60)
        print("ANALYTICS COMPLETE")
        print("="*60 + "\n")

    # Step 5: Upload to AWS (requires credentials and setup)
    if run_conditions["upload_data"]:
        print("\n" + "="*60)
        print("AWS UPLOAD START")
        print("="*60 + "\n")

        try:
            from utils.aws_upload import upload_to_aws

            upload_items = {
                "books": True,
                "lookup_tables": True,
                "force_files": True,
                "config_files": True,
            }

            upload_to_aws(
                gamestate,
                target_modes,
                upload_items,
            )

            print("\n" + "="*60)
            print("AWS UPLOAD COMPLETE")
            print("="*60 + "\n")
        except ImportError:
            print("AWS upload not available (module not found)")
        except Exception as e:
            print(f"AWS upload failed: {e}")

    print("\n" + "="*60)
    print("BEAT THE BOSS - ALL TASKS COMPLETE")
    print("="*60)
    print(f"\nOutput files location: games/beat_the_boss/output/")
    print("="*60 + "\n")