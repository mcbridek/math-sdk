"""Generate configuration files only (skip simulation)."""

from gamestate import GameState
from game_config import GameConfig
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)

    print("\n" + "="*60)
    print("GENERATING CONFIGURATION FILES")
    print("="*60 + "\n")

    generate_configs(gamestate)

    print("\n" + "="*60)
    print("CONFIGURATION GENERATION COMPLETE")
    print("="*60 + "\n")