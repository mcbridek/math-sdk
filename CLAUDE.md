# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Stake Engine Math SDK is a Python-based engine for defining slot game rules, simulating outcomes, and optimizing win distributions. It generates backend configuration files, lookup tables, and simulation results for slot games.

**Requirements:**
- Python >= 3.12 (important: default python3 may be older, use `python3.12` explicitly)
- Rust/Cargo (for optimization algorithm)

## Common Commands

**Setup:**
```bash
# Initial setup (creates virtual environment and installs dependencies)
make setup

# If default python3 is < 3.12, use:
make clean
python3.12 -m venv env
env/bin/python -m pip install --upgrade pip
env/bin/python -m pip install -r requirements.txt
env/bin/python -m pip install -e .

# Activate virtual environment
source env/bin/activate
```

**Running Games:**
```bash
# Run a specific game (generates books, configs, and optionally runs optimization)
make run GAME=<game_name>
# Example: make run GAME=beat_the_boss

# Run tests
make test

# Run multiple test games
make test_run

# Clean environment
make clean
```

## Architecture

### Game Structure

Each game lives in `games/<game_name>/` with required files:

1. **`run.py`** - Main execution script that orchestrates:
   - `create_books()` - Generate simulation data (books)
   - `generate_configs()` - Generate configuration files
   - `OptimizationExecution()` - Run Rust optimization algorithm
   - `upload_to_aws()` - Upload results to AWS

2. **`game_config.py`** - Extends `src.config.config.Config` with game-specific configuration:
   - Game metadata (game_id, RTP, wincap, provider)
   - Reels and paytables
   - Special symbols (wilds, scatters, multipliers)
   - Bet modes with distribution targets
   - Freespin triggers

3. **`gamestate.py`** - Extends `game_override.GameStateOverride`, implements:
   - `run_spin()` - Base game spin logic
   - `run_freespin()` - Free spin feature logic

4. **`game_override.py`** - Extends `src.state.state.GeneralGameState` with custom game logic:
   - Symbol evaluation functions
   - Win calculation overrides
   - Custom feature implementations

5. **`game_optimization.py`** - Extends `OptimizationSetup` to configure the Rust optimization algorithm with distribution targets

6. **`game_calculations.py`** - Custom calculation logic (if needed)
7. **`game_events.py`** - Custom event handlers (if needed)
8. **`game_executables.py`** - Custom executable functions (if needed)

### Core SDK Structure

**`src/` - Core engine components:**
- `config/` - Base configuration classes and bet mode definitions
- `state/` - Game state management and simulation execution
- `wins/` - Win evaluation and management
- `calculations/` - Symbol calculations and board evaluation
- `events/` - Event system for game actions
- `write_data/` - Data output and file generation

**`optimization_program/` - Rust-based optimization:**
- Contains Cargo.toml and Rust source for distribution optimization algorithm
- Invoked via `OptimizationExecution().run_all_modes()`

**`utils/` - Utilities:**
- `game_analytics/` - Statistics and analysis tools
- `rgs_verification.py` - RGS compliance testing
- `format_books_json.py` - Format output JSON files

### Game Execution Flow

1. **Configuration Phase**: `GameConfig()` initializes game parameters, reads reels from CSV files
2. **State Initialization**: `GameState(config)` creates the game state manager
3. **Simulation Phase**: `create_books()` runs N simulations per distribution criteria, generating "books" (simulation results)
4. **Config Generation**: `generate_configs()` creates backend configuration files and lookup tables
5. **Optimization Phase** (optional): Rust algorithm adjusts reel weights to hit distribution targets
6. **Analysis Phase** (optional): Generate statistical reports
7. **Upload Phase** (optional): Push artifacts to AWS

### Key Concepts

**Distributions**: Define win targets and quotas for optimization. Each bet mode has multiple distributions (e.g., "wincap", "freegame", "basegame", "0") with criteria like RTP contribution, hit rate, specific win amounts.

**Books**: Simulation output files containing spin results, stored as compressed or uncompressed JSON. Each book represents results for a specific distribution criteria.

**Bet Modes**: Different ways to play (e.g., "base", "buybonus"), each with distinct RTP, cost, and distributions.

**Game Types**: Typically "basegame" and "freegame", representing base game and free spin modes with separate reel sets.

**Reels**: Symbol strips defined in CSV files (e.g., `BR0.csv`, `FR0.csv`), referenced in `game_config.py`.

## Creating New Games

Use `games/template/` as starting point:
```bash
cp -r games/template games/<new_game_name>
```

Then customize the 8 game files, particularly:
1. Set game metadata in `game_config.py`
2. Create reel CSV files in `games/<game_name>/reels/`
3. Define paytable and special symbols
4. Implement spin logic in `gamestate.py` and `game_override.py`
5. Configure optimization targets in `game_optimization.py`
6. Adjust `run.py` settings (num_threads, compression, run_conditions)

## File Outputs

Games generate outputs in `games/<game_name>/output/`:
- `books/` - Simulation results (.json or .zst compressed)
- `lookup_tables/` - Precomputed game data
- `configs/` - Backend configuration files
- `analysis/` - Statistical reports (if generated)