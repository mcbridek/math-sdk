"""
Boxing Game - Stake Engine Distribution Configuration
Integrates boxing mechanics with Stake's proven math framework
"""

from stakeengine import Config, BetMode, Distribution
import json

class BoxingGameStakeConfig(Config):
    """Boxing Game configuration using Stake Engine framework"""
    
    def __init__(self):
        super().__init__()
        
        # Basic Stake Engine configuration
        self.game_id = "boxing_champion_v1"
        self.provider_number = 2001
        self.working_name = "Boxing Champion"
        self.wincap = 5000.0  # 5000x maximum win
        self.win_type = "sequence_based"  # Custom win type for boxing
        self.rtp = 0.96
        
        # Grid configuration (represents the "ring")
        self.num_reels = 6  # Maximum sequence length
        self.num_rows = [8, 8, 8, 8, 8, 8]  # 8 possible moves per position
        
        # Include padding for move positioning
        self.include_padding = True
        
        # Define special symbols (boxing moves)
        self.special_symbols = {
            "attack_moves": ["PUN", "UPP"],
            "defense_moves": ["DUK", "BWD"], 
            "positioning": ["FWD"],
            "damage_states": ["HRT", "DIZ"],
            "finisher": ["KO"]
        }
        
        # Boxing-specific triggers (equivalent to free spin triggers)
        self.freespin_triggers = {
            "knockout_round": {3: 5, 4: 8, 5: 12},  # KO triggers bonus rounds
            "combo_streak": {3: 3, 4: 5, 5: 8},     # Long combos trigger bonus
        }
        
        # Define paytable for boxing sequences
        self.paytable = self._build_boxing_paytable()
        
        # Define reel sets (move probability distributions)
        self.reels = self._define_boxing_reels()
        
        # Configure bet modes with distributions
        self.bet_modes = [
            self._create_base_betting_mode(),
            self._create_aggressive_betting_mode(), 
            self._create_defensive_betting_mode(),
            self._create_championship_mode()
        ]
    
    def _build_boxing_paytable(self):
        """Build paytable mapping boxing sequences to payouts"""
        return {
            # Basic sequences (2 moves)
            (2, "FWD-PUN"): 1.5,
            (2, "BWD-PUN"): 2.5, 
            (2, "PUN-PUN"): 2.0,
            (2, "DUK-PUN"): 3.0,
            
            # Power sequences (3 moves)
            (3, "FWD-PUN-UPP"): 8.0,
            (3, "DUK-PUN-UPP"): 12.0,
            (3, "BWD-FWD-UPP"): 10.0,
            (3, "PUN-PUN-UPP"): 8.0,
            
            # Defense to attack (3-4 moves)
            (3, "DUK-DUK-UPP"): 15.0,
            (4, "BWD-DUK-FWD-UPP"): 20.0,
            (4, "DUK-BWD-DUK-UPP"): 25.0,
            
            # Knockout sequences (variable length)
            (2, "UPP-KO"): 25.0,
            (2, "DUK-KO"): 50.0,
            (3, "PUN-UPP-KO"): 35.0,
            (4, "DUK-DUK-UPP-KO"): 75.0,
            (5, "BWD-DUK-FWD-UPP-KO"): 150.0,
            
            # Perfect sequences (max payout)
            (5, "DUK-DUK-DUK-UPP-KO"): 5000.0,  # The perfect fight
            (4, "HRT-DIZ-UPP-KO"): 100.0,        # Comeback victory
            
            # Defensive preservation (multiplier bonuses)
            (2, "BWD-BWD"): 0.5,  # Preserves multiplier
            (1, "DUK"): 1.0,      # Dodge bonus
        }
    
    def _define_boxing_reels(self):
        """Define reel strips for different fighting styles"""
        
        # Base game reels (balanced fighting)
        basegame_balanced = {
            "reel_0": ["FWD", "BWD", "PUN", "DUK", "FWD", "PUN", "BWD", "HRT"] * 5,
            "reel_1": ["PUN", "FWD", "DUK", "PUN", "BWD", "UPP", "PUN", "DIZ"] * 5, 
            "reel_2": ["UPP", "PUN", "DUK", "FWD", "PUN", "BWD", "UPP", "HRT"] * 5,
            "reel_3": ["PUN", "UPP", "DUK", "BWD", "PUN", "FWD", "KO", "DIZ"] * 5,
            "reel_4": ["KO", "UPP", "DUK", "PUN", "BWD", "FWD", "PUN", "HRT"] * 5,
            "reel_5": ["KO", "KO", "UPP", "DUK", "PUN", "BWD", "FWD", "DIZ"] * 5,
        }
        
        # Aggressive reels (more attacks, higher variance)
        aggressive_reels = {
            "reel_0": ["FWD", "FWD", "PUN", "FWD", "UPP", "PUN", "BWD", "HRT"] * 5,
            "reel_1": ["PUN", "PUN", "UPP", "PUN", "FWD", "UPP", "DUK", "DIZ"] * 5,
            "reel_2": ["UPP", "PUN", "UPP", "PUN", "UPP", "DUK", "BWD", "HRT"] * 5, 
            "reel_3": ["PUN", "UPP", "UPP", "PUN", "UPP", "KO", "DUK", "DIZ"] * 5,
            "reel_4": ["KO", "UPP", "KO", "UPP", "PUN", "KO", "BWD", "HRT"] * 5,
            "reel_5": ["KO", "KO", "UPP", "KO", "UPP", "KO", "DUK", "DIZ"] * 5,
        }
        
        # Defensive reels (more dodges/counters, lower variance but consistent wins)
        defensive_reels = {
            "reel_0": ["BWD", "DUK", "BWD", "DUK", "FWD", "BWD", "PUN", "HRT"] * 5,
            "reel_1": ["DUK", "BWD", "DUK", "PUN", "DUK", "BWD", "FWD", "DIZ"] * 5,
            "reel_2": ["DUK", "DUK", "UPP", "DUK", "BWD", "PUN", "FWD", "HRT"] * 5,
            "reel_3": ["UPP", "DUK", "UPP", "DUK", "BWD", "UPP", "PUN", "DIZ"] * 5, 
            "reel_4": ["KO", "UPP", "DUK", "UPP", "DUK", "BWD", "PUN", "HRT"] * 5,
            "reel_5": ["KO", "KO", "UPP", "KO", "DUK", "UPP", "BWD", "DIZ"] * 5,
        }
        
        return {
            "basegame_balanced": basegame_balanced,
            "basegame_aggressive": aggressive_reels, 
            "basegame_defensive": defensive_reels,
            "freegame_knockout": aggressive_reels  # Bonus rounds use aggressive reels
        }
    
    def _create_base_betting_mode(self):
        """Standard betting mode - balanced fighting style"""
        return BetMode(
            name="standard",
            cost=1.0,
            rtp=self.rtp,
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=False,
            is_buybonus=False,
            distributions=[
                # Perfect fight wins (extremely rare, max payout)
                Distribution(
                    criteria="perfect_fight",
                    quota=0.0001,  # 0.01% chance
                    win_criteria=self.wincap,
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"standard": 1},
                            "freegame_knockout": {"perfect": 1},
                        },
                        "sequence_requirements": ["DUK-DUK-DUK-UPP-KO"],
                        "health_conditions": {"dodge_all": True, "perfect_counter": True},
                        "force_wincap": True,
                        "force_perfect_sequence": True,
                    },
                ),
                
                # Knockout wins (rare, high payout) 
                Distribution(
                    criteria="knockout",
                    quota=0.002,  # 0.2% chance
                    win_criteria=100.0,  # 100x+ multiplier
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"aggressive": 1},
                            "freegame_knockout": {"standard": 1},
                        },
                        "knockout_sequences": ["UPP-KO", "DUK-KO", "PUN-UPP-KO"],
                        "health_conditions": {"opponent_low": True},
                        "force_freegame": True,
                    },
                ),
                
                # Combo wins (uncommon, medium-high payout)
                Distribution(
                    criteria="combo_victory", 
                    quota=0.05,  # 5% chance
                    win_criteria=10.0,  # 10x+ multiplier
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"standard": 70, "aggressive": 30},
                        },
                        "combo_sequences": ["FWD-PUN-UPP", "DUK-PUN-UPP", "BWD-FWD-UPP"],
                        "min_sequence_length": 3,
                    },
                ),
                
                # Standard wins (common, low-medium payout)
                Distribution(
                    criteria="standard_win",
                    quota=0.25,  # 25% chance
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"standard": 100},
                        },
                        "basic_sequences": ["FWD-PUN", "PUN-PUN", "BWD-PUN"],
                        "min_multiplier": 1.5,
                        "max_multiplier": 5.0,
                    },
                ),
                
                # Close fights (common, small wins)
                Distribution(
                    criteria="close_fight",
                    quota=0.35,  # 35% chance
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"defensive": 60, "standard": 40},
                        },
                        "defensive_sequences": ["DUK", "BWD-BWD", "DUK-PUN"],
                        "max_multiplier": 2.0,
                    },
                ),
                
                # Losses (common, no payout)
                Distribution(
                    criteria="loss",
                    quota=0.35,  # 35% chance  
                    win_criteria=0.0,
                    conditions={
                        "reel_weights": {
                            "basegame_balanced": {"standard": 100},
                        },
                        "damage_sequences": ["HRT", "DIZ", "HRT-DIZ"],
                        "no_successful_attacks": True,
                    },
                ),
            ],
        )
    
    def _create_aggressive_betting_mode(self):
        """High-risk, high-reward betting mode"""
        return BetMode(
            name="aggressive",
            cost=2.0,  # 2x bet cost
            rtp=0.96,  # Same RTP but higher volatility
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=True,
            is_buybonus=False,
            distributions=[
                # More knockout opportunities
                Distribution(
                    criteria="knockout",
                    quota=0.01,  # 1% chance (10x more likely than base)
                    win_criteria=50.0,
                    conditions={
                        "reel_weights": {
                            "basegame_aggressive": {"high_attack": 1},
                            "freegame_knockout": {"aggressive": 1},
                        },
                        "force_freegame": True,
                        "aggressive_multiplier": 2.0,
                    },
                ),
                
                # Big combo wins
                Distribution(
                    criteria="big_combo",
                    quota=0.08,  # 8% chance
                    win_criteria=20.0,
                    conditions={
                        "reel_weights": {
                            "basegame_aggressive": {"combo_focus": 1},
                        },
                        "min_sequence_length": 4,
                        "combo_multiplier": 1.5,
                    },
                ),
                
                # Higher loss rate (volatility trade-off)
                Distribution(
                    criteria="loss",
                    quota=0.6,  # 60% loss rate
                    win_criteria=0.0,
                    conditions={
                        "reel_weights": {
                            "basegame_aggressive": {"high_risk": 1},
                        },
                        "aggressive_penalty": True,
                    },
                ),
                
                # Moderate wins
                Distribution(
                    criteria="moderate_win",
                    quota=0.31,  # 31% chance
                    conditions={
                        "reel_weights": {
                            "basegame_aggressive": {"standard": 1},
                        },
                    },
                ),
            ],
        )
    
    def _create_defensive_betting_mode(self):
        """Low-risk, consistent returns betting mode"""
        return BetMode(
            name="defensive",
            cost=0.5,  # 0.5x bet cost
            rtp=0.96,  # Same RTP but lower volatility
            max_win=500.0,  # Lower max win (10% of standard)
            auto_close_disabled=False,
            is_feature=True, 
            is_buybonus=False,
            distributions=[
                # Rare but consistent counter-attack wins
                Distribution(
                    criteria="counter_attack",
                    quota=0.15,  # 15% chance
                    win_criteria=5.0,
                    conditions={
                        "reel_weights": {
                            "basegame_defensive": {"counter_focus": 1},
                        },
                        "defensive_sequences": ["DUK-UPP", "BWD-PUN", "DUK-DUK-UPP"],
                        "defensive_multiplier": 1.0,
                    },
                ),
                
                # Small consistent wins
                Distribution(
                    criteria="small_win",
                    quota=0.6,  # 60% chance
                    conditions={
                        "reel_weights": {
                            "basegame_defensive": {"safe_play": 1},
                        },
                        "max_multiplier": 3.0,
                        "consistent_returns": True,
                    },
                ),
                
                # Lower loss rate
                Distribution(
                    criteria="loss", 
                    quota=0.25,  # 25% loss rate (much lower)
                    win_criteria=0.0,
                    conditions={
                        "reel_weights": {
                            "basegame_defensive": {"safe_defensive": 1},
                        },
                    },
                ),
            ],
        )
    
    def _create_championship_mode(self):
        """Premium mode - buy bonus for guaranteed exciting round"""
        return BetMode(
            name="championship",
            cost=100.0,  # 100x bet cost
            rtp=0.96,
            max_win=self.wincap,
            auto_close_disabled=False,
            is_feature=False,
            is_buybonus=True,  # This is a buy bonus mode
            distributions=[
                # Guaranteed big fight
                Distribution(
                    criteria="championship_fight",
                    quota=1.0,  # 100% chance of special round
                    win_criteria=50.0,  # Minimum 50x win
                    conditions={
                        "reel_weights": {
                            "freegame_knockout": {"championship": 1},
                        },
                        "guaranteed_sequences": ["UPP-KO", "DUK-UPP-KO", "FWD-FWD-UPP-KO"],
                        "championship_multipliers": {2: 50, 3: 100, 4: 250, 5: 1000},
                        "force_freegame": True,
                        "min_guaranteed_win": 50.0,
                    },
                ),
            ],
        )

# Optimization configuration for the boxing game
def create_boxing_optimization_config():
    """Create optimization parameters for the boxing game"""
    
    opt_params = {
        "standard": {
            "conditions": {
                "target_rtp": 0.96,
                "max_win_exposure": 0.001,  # 0.1% of spins can hit max win
                "volatility_target": "medium",
            },
            "scaling": {
                "knockout_sequences": {"min": 0.0001, "max": 0.002, "step": 0.0001},
                "combo_sequences": {"min": 0.02, "max": 0.08, "step": 0.005},
                "basic_sequences": {"min": 0.15, "max": 0.35, "step": 0.02},
            },
            "parameters": {
                "health_multiplier_impact": {"min": 1.0, "max": 2.0, "step": 0.1},
                "streak_bonus_scaling": {"min": 0.1, "max": 0.8, "step": 0.05},
                "comeback_multiplier": {"min": 1.2, "max": 3.0, "step": 0.1},
            }
        },
        
        "aggressive": {
            "conditions": {
                "target_rtp": 0.96,
                "volatility_target": "high",
                "max_loss_streak": 20,  # Higher acceptable loss streaks
            },
            "scaling": {
                "knockout_frequency": {"min": 0.005, "max": 0.02, "step": 0.001},
                "loss_rate": {"min": 0.5, "max": 0.7, "step": 0.02},
            }
        },
        
        "defensive": {
            "conditions": {
                "target_rtp": 0.96,
                "volatility_target": "low", 
                "max_win_cap": 500.0,
            },
            "scaling": {
                "consistent_win_rate": {"min": 0.5, "max": 0.8, "step": 0.02},
                "loss_rate": {"min": 0.15, "max": 0.35, "step": 0.02},
            }
        },
        
        "championship": {
            "conditions": {
                "target_rtp": 0.96,
                "guaranteed_excitement": True,
                "min_win_guarantee": 50.0,
            },
            "scaling": {
                "championship_multipliers": {"min": 25.0, "max": 200.0, "step": 5.0},
                "perfect_fight_chance": {"min": 0.001, "max": 0.01, "step": 0.0005},
            }
        }
    }
    
    return opt_params

# Example usage and testing
def test_boxing_configuration():
    """Test the boxing game configuration"""
    
    config = BoxingGameStakeConfig()
    
    print("Boxing Game - Stake Engine Configuration")
    print("=" * 50)
    print(f"Game ID: {config.game_id}")
    print(f"RTP: {config.rtp}")
    print(f"Max Win: {config.wincap}x")
    print(f"Win Type: {config.win_type}")
    
    print(f"\nBet Modes: {len(config.bet_modes)}")
    for mode in config.bet_modes:
        print(f"  - {mode.name}: {mode.cost}x cost, {len(mode.distributions)} distributions")
    
    print(f"\nPaytable Entries: {len(config.paytable)}")
    # Show some high-value sequences
    high_value = [(k, v) for k, v in config.paytable.items() if v >= 25.0]
    print("High-value sequences:")
    for (length, sequence), payout in sorted(high_value, key=lambda x: x[1], reverse=True):
        print(f"  {sequence}: {payout}x")
    
    print(f"\nReel Sets: {len(config.reels)}")
    for reel_name in config.reels:
        print(f"  - {reel_name}")
    
    # Show optimization parameters
    opt_config = create_boxing_optimization_config()
    print(f"\nOptimization Modes: {len(opt_config)}")
    for mode_name, params in opt_config.items():
        conditions_count = len(params.get("conditions", {}))
        scaling_count = len(params.get("scaling", {}))
        print(f"  - {mode_name}: {conditions_count} conditions, {scaling_count} scaling parameters")

if __name__ == "__main__":
    test_boxing_configuration()

# Export configuration for Stake Engine integration
def export_stake_config():
    """Export configuration in format ready for Stake Engine"""
    config = BoxingGameStakeConfig()
    opt_params = create_boxing_optimization_config()
    
    return {
        "game_config": config,
        "optimization_params": opt_params,
        "integration_notes": {
            "custom_win_evaluation": "Boxing sequences require custom win evaluation logic",
            "health_system": "Fighter health affects multiplier calculations", 
            "sequence_matching": "Move sequences map to traditional paylines",
            "special_events": "Knockout and combo events trigger bonus mechanics",
        }
    }
