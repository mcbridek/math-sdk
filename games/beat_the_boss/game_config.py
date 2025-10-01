"""Beat the Boss - Boxing-themed casino game configuration."""

from src.config.config import Config
from src.config.distributions import Distribution
from src.config.config import BetMode


class GameConfig(Config):
    """Beat the Boss game configuration with three boss modes."""

    def __init__(self):
        super().__init__()

        # Basic game info
        self.game_id = "beat_the_boss"
        self.provider_number = 1001
        self.working_name = "Beat the Boss"
        self.wincap = 5000  # Base mode max win
        self.win_type = "sequence_based"
        self.rtp = 0.98  # 98% RTP for all modes
        self.construct_paths()

        # Game dimensions (treating as 6-reel sequence generator)
        self.num_reels = 6  # Max sequence length
        self.num_rows = [1] * self.num_reels  # Single move per position

        # Boxing moves (our symbols)
        self.boxing_moves = {
            "FWD": "Forward",      # Positioning
            "BWD": "Backward",     # Defensive
            "PUN": "Punch",        # Basic attack
            "UPP": "Uppercut",     # Power attack
            "DUK": "Duck",         # Dodge
            "HRT": "Hurt",         # Damage taken
            "DIZ": "Dizzy",        # Stunned
            "KO":  "Knockout",     # Finisher
        }

        # Move sequences paytable (sequence -> payout multiplier)
        # Optimized with 1.0603x scaling to achieve 98% RTP
        # Minimum 0.0212x to avoid SDK rounding losses
        self.paytable = {
            # Basic 2-move combos (very common, small visible wins)
            (2, "FWD-PUN"): 0.053,
            (2, "PUN-PUN"): 0.053,
            (2, "BWD-PUN"): 0.0636,
            (2, "FWD-UPP"): 0.1484,
            (2, "PUN-UPP"): 0.0954,
            (2, "BWD-UPP"): 0.1166,
            (2, "BWD-BWD"): 0.0212,
            (2, "DUK-DUK"): 0.053,
            (2, "BWD-DUK"): 0.053,
            (2, "DUK-BWD"): 0.053,
            (2, "BWD-FWD"): 0.0212,
            (2, "FWD-BWD"): 0.0212,
            (2, "FWD-FWD"): 0.053,
            (2, "DUK-PUN"): 0.053,
            (2, "DUK-FWD"): 0.053,

            # 3-move combos (uncommon, medium wins)
            (3, "PUN-PUN-UPP"): 0.2757,
            (3, "FWD-PUN-UPP"): 0.3287,
            (2, "DUK-UPP"): 0.4241,
            (3, "BWD-FWD-UPP"): 0.4665,
            (3, "FWD-FWD-PUN"): 0.2121,
            (3, "BWD-BWD-PUN"): 0.159,
            (3, "DUK-DUK-PUN"): 0.2333,
            (3, "FWD-PUN-PUN"): 0.2333,
            (3, "BWD-PUN-UPP"): 0.2757,

            # 4-move expert combos (rare, larger wins)
            (3, "DUK-DUK-UPP"): 0.6574,
            (4, "BWD-DUK-FWD-UPP"): 1.3996,
            (4, "PUN-PUN-PUN-UPP"): 1.0709,
            (4, "FWD-FWD-PUN-UPP"): 0.9331,
            (4, "DUK-DUK-DUK-UPP"): 2.0994,
            (4, "FWD-FWD-FWD-PUN"): 0.7952,

            # Knockout sequences (very rare, big wins)
            (2, "UPP-KO"): 23.369,
            (2, "DUK-KO"): 46.7274,
            (2, "PUN-KO"): 14.0278,
            (3, "PUN-UPP-KO"): 35.0429,
            (3, "DUK-UPP-KO"): 70.1071,
            (4, "DUK-DUK-UPP-KO"): 116.8345,
            (5, "BWD-DUK-FWD-UPP-KO"): 233.6584,
            (4, "FWD-FWD-UPP-KO"): 93.4655,

            # Legendary sequences (mythical, huge wins)
            (4, "HRT-DIZ-UPP-KO"): 467.3274,
            (5, "DUK-DUK-DUK-UPP-KO"): 2336.6264,
            (5, "FWD-FWD-FWD-UPP-KO"): 2336.6264,
            (6, "DUK-DUK-DUK-DUK-UPP-KO"): 2336.6264,
        }

        self.include_padding = False
        self.special_symbols = {
            "knockout": ["KO"],
            "defensive": ["DUK", "BWD"],
            "offensive": ["PUN", "UPP"],
            "damage": ["HRT", "DIZ"],
        }

        # Mode-specific RTP adjustments to achieve 98% RTP per mode
        # Each mode has different reel strips, so multipliers compensate
        self.mode_rtp_adjustments = {
            "macron": 1.0390,  # 94.32% → 98%
            "putin": 1.0432,   # 93.94% → 98%
            "trump": 0.9179,   # 106.77% → 98%
        }

        # No traditional freespins - continuous round system
        self.freespin_triggers = {self.basegame_type: {}, self.freegame_type: {}}
        self.anticipation_triggers = {self.basegame_type: 0, self.freegame_type: 0}

        # Boss-specific reels (different move distributions per boss)
        reels = {
            # Macron (Defensive) - Base game - v4 tuned for 98% RTP
            "MACRON_BASE": "macron_base_v6.csv",
            "MACRON_ROUND": "macron_round.csv",

            # Putin (Balanced) - Medium volatility - v4 tuned for 98% RTP
            "PUTIN_BASE": "putin_base_v6.csv",
            "PUTIN_ROUND": "putin_round.csv",

            # Trump (Aggressive) - High volatility - v4 tuned for 98% RTP
            "TRUMP_BASE": "trump_base_final.csv",
            "TRUMP_ROUND": "trump_round.csv",
        }

        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(str.join("/", [self.reels_path, f]))

        # Remove CSV header "symbol" from each reel strip
        for reel_name in self.reels:
            for strip_idx in range(len(self.reels[reel_name])):
                # Filter out the header value
                self.reels[reel_name][strip_idx] = [
                    symbol for symbol in self.reels[reel_name][strip_idx]
                    if symbol.lower() != "symbol"
                ]

        # Boss characteristics
        self.boss_config = {
            "macron": {
                "health": 150,
                "max_win": 5000,
                "hit_rate_target": 0.70,
                "style": "defensive",
                "description": "Strategic and defensive fighter",
            },
            "putin": {
                "health": 125,
                "max_win": 7500,
                "hit_rate_target": 0.50,
                "style": "balanced",
                "description": "Tactical and unpredictable fighter",
            },
            "trump": {
                "health": 100,
                "max_win": 10000,
                "hit_rate_target": 0.35,
                "style": "aggressive",
                "description": "Aggressive and chaotic fighter",
            },
        }

        # Three bet modes - one for each boss
        self.bet_modes = [
            # Macron Mode - Base (1x cost, 5000x max)
            BetMode(
                name="macron",
                cost=1.0,
                rtp=self.rtp,
                max_win=5000,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Natural distribution - let the game run and categorize results
                    # Quota represents target hit rate: 70% winning spins
                    Distribution(
                        criteria="all_spins",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"MACRON_BASE": 1},
                            },
                        },
                    ),
                ],
            ),

            # Putin Mode - Medium (2x cost, 7500x max)
            BetMode(
                name="putin",
                cost=2.0,
                rtp=self.rtp,
                max_win=7500,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Natural distribution - let the game run and categorize results
                    # Quota represents target hit rate: 50% winning spins
                    Distribution(
                        criteria="all_spins",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"PUTIN_BASE": 1},
                            },
                        },
                    ),
                ],
            ),

            # Trump Mode - High (3x cost, 10000x max)
            BetMode(
                name="trump",
                cost=3.0,
                rtp=self.rtp,
                max_win=10000,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Natural distribution - let the game run and categorize results
                    # Quota represents target hit rate: 35% winning spins
                    Distribution(
                        criteria="all_spins",
                        quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"TRUMP_BASE": 1},
                            },
                        },
                    ),
                ],
            ),
        ]