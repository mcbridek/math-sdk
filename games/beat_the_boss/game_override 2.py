"""Beat the Boss - Game state override with boxing mechanics."""

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
import random


class GameStateOverride(GameExecutables):
    """
    Override game state with boxing-specific mechanics:
    - Move sequence evaluation
    - Health bar management
    - Dynamic multipliers based on health
    - Knockout detection
    """

    def reset_book(self):
        """Reset boxing-specific properties for each spin."""
        super().reset_book()

        # Boxing game state
        self.move_sequence = []  # Current sequence of moves
        self.max_sequence_length = 6

        # Health bars
        self.player_health = 100.0
        self.boss_health = self.get_boss_health()

        # Combat statistics
        self.dodge_streak = 0
        self.attack_streak = 0
        self.damage_dealt = 0
        self.damage_taken = 0

        # Win tracking
        self.knockout_achieved = False
        self.sequence_wins = []

    def get_boss_health(self):
        """Get boss health based on current bet mode."""
        try:
            current_mode = self.get_current_betmode()
            boss_name = current_mode.get_name()

            if boss_name in self.config.boss_config:
                return self.config.boss_config[boss_name]["health"]
        except (AttributeError, KeyError):
            pass
        return 100.0  # Default

    def assign_special_sym_function(self):
        """Define special symbol functions for boxing moves."""
        self.special_symbol_functions = {
            "KO": [self.handle_knockout_move],
            "DUK": [self.handle_defensive_move],
            "HRT": [self.handle_damage_move],
            "DIZ": [self.handle_stun_move],
        }

    def handle_knockout_move(self, symbol):
        """Handle knockout move - only possible if boss health is low."""
        if self.boss_health <= 30:
            self.knockout_achieved = True
            symbol.special_effect = "knockout_enabled"
        else:
            symbol.special_effect = "knockout_failed"

    def handle_defensive_move(self, symbol):
        """Handle defensive moves - increment dodge streak."""
        self.dodge_streak += 1
        self.attack_streak = 0
        symbol.special_effect = f"dodge_streak_{self.dodge_streak}"

    def handle_damage_move(self, symbol):
        """Handle damage taken - affects player health."""
        damage = random.randint(10, 20)
        self.player_health = max(0, self.player_health - damage)
        self.damage_taken += damage
        symbol.damage = damage

    def handle_stun_move(self, symbol):
        """Handle stun - temporary vulnerability."""
        damage = random.randint(5, 15)
        self.player_health = max(0, self.player_health - damage)
        self.damage_taken += damage
        symbol.special_effect = "stunned"
        symbol.damage = damage

    def generate_move(self):
        """Generate next boxing move from current reel."""
        # Get appropriate reel for current boss and game mode
        current_mode = self.get_current_betmode()
        boss_name = current_mode.get_name().upper()
        reel_name = f"{boss_name}_BASE"

        if reel_name in self.config.reels:
            # Reels are a list of reel strips (one per column)
            # We only have one column, so access [0]
            reel_strip = self.config.reels[reel_name][0]
            move = random.choice(reel_strip)
            return move
        return "PUN"  # Fallback

    def evaluate_move_sequence(self):
        """Evaluate current move sequence for wins."""
        if len(self.move_sequence) < 2:
            return None

        sequence_str = "-".join(self.move_sequence)

        # Check all possible subsequences (from longest to shortest)
        for length in range(min(len(self.move_sequence), 6), 1, -1):
            # Get the last 'length' moves
            subseq = self.move_sequence[-length:]
            subseq_str = "-".join(subseq)

            # Check if this subsequence is in paytable
            paytable_key = (length, subseq_str)
            if paytable_key in self.config.paytable:
                base_multiplier = self.config.paytable[paytable_key]
                return self.calculate_sequence_win(subseq_str, base_multiplier, length)

        return None

    def calculate_sequence_win(self, sequence, base_multiplier, length):
        """Calculate win amount from base paytable multiplier."""
        # Apply mode-specific RTP adjustment to achieve 98% RTP per mode
        current_mode = self.get_current_betmode()
        mode_name = current_mode.get_name()
        adjustment = getattr(self.config, 'mode_rtp_adjustments', {}).get(mode_name, 1.0)
        multiplier = base_multiplier * adjustment

        # Health bonuses disabled for RTP tuning
        # TODO: Re-enable small bonuses once base RTP is correct

        # Calculate damage to boss
        damage = base_multiplier * 2  # Damage scaling
        self.boss_health = max(0, self.boss_health - damage)
        self.damage_dealt += damage

        # Update streaks based on sequence
        if "DUK" in sequence or "BWD" in sequence:
            self.dodge_streak += 1
            self.attack_streak = 0
        elif "PUN" in sequence or "UPP" in sequence:
            self.attack_streak += 1
            self.dodge_streak = 0

        return {
            "sequence": sequence,
            "length": length,
            "base_multiplier": base_multiplier,
            "final_multiplier": multiplier,
            "damage": damage,
            "boss_health": self.boss_health,
            "player_health": self.player_health,
        }

    def evaluate_finalwin(self):
        """Evaluate final win for the spin (boxing round) - BEST win only."""
        best_win = 0.0
        best_win_result = None

        # Generate move sequence
        for _ in range(self.max_sequence_length):
            move = self.generate_move()
            self.move_sequence.append(move)

            # Evaluate after each move
            win_result = self.evaluate_move_sequence()
            if win_result:
                win_amount = win_result["final_multiplier"]

                # Only keep the BEST win found (highest multiplier)
                if win_amount > best_win:
                    best_win = win_amount
                    best_win_result = win_result
                    self.sequence_wins.append(win_result)

            # Check for knockout or health depletion
            if self.boss_health <= 0:
                self.knockout_achieved = True
                # Knockout bonus if we already have a win
                if best_win > 0:
                    knockout_bonus = best_win * 0.5  # 50% bonus for knockout
                    best_win += knockout_bonus
                break

            if self.player_health <= 0:
                # Player loses - no further wins
                best_win = 0
                break

        # Apply win cap
        current_mode = self.get_current_betmode()
        if best_win > current_mode.get_wincap():
            best_win = current_mode.get_wincap()
            self.wincap_triggered = True

        # Record the best win
        if best_win > 0:
            self.win_manager.update_spinwin(best_win)

        self.final_win = best_win
        self.book.payout_multiplier = self.final_win  # Record win to book
        self.repeat = False

    def check_game_repeat(self):
        """Check if game needs to repeat for distribution targets."""
        # Default to not repeating
        self.repeat = False

        # Only repeat if we have specific win_criteria that must be matched
        win_criteria = self.get_current_betmode_distributions().get_win_criteria()
        if win_criteria is not None and self.final_win != win_criteria:
            # Check if we're close enough to target win
            tolerance = win_criteria * 0.1  # 10% tolerance
            if abs(self.final_win - win_criteria) > tolerance:
                self.repeat = True
                self.repeat_count += 1

                # Prevent infinite loops
                if self.repeat_count > 100:
                    self.repeat = False