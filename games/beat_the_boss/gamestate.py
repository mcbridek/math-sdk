"""Beat the Boss - Game state with boxing round mechanics."""

from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Handle boxing game logic and event updates for simulations."""

    def run_spin(self, sim):
        """
        Run a complete boxing round.
        Each spin represents a fight round with move sequences.
        """
        self.reset_seed(sim)
        self.repeat = True
        self.repeat_count = 0  # Initialize once per spin (not per loop iteration)

        while self.repeat:
            self.reset_book()

            # Execute boxing round - evaluate move sequences and calculate wins
            self.evaluate_finalwin()

            # Check if we need to repeat for distribution targets
            self.check_game_repeat()

        # Finalize wins for this round
        self.imprint_wins()

    def run_freespin(self):
        """
        Beat the Boss doesn't use traditional freespins.
        Instead, knockouts might trigger bonus rounds.
        This can be customized later for bonus features.
        """
        # Optional: Implement bonus rounds after knockout
        pass

    def imprint_wins(self):
        """Record wins and boxing round data."""
        super().imprint_wins()

        # Add boxing-specific data to book
        self.book.boxing_data = {
            "move_sequence": self.move_sequence,
            "player_health_final": self.player_health,
            "boss_health_final": self.boss_health,
            "knockout": self.knockout_achieved,
            "damage_dealt": self.damage_dealt,
            "damage_taken": self.damage_taken,
            "sequence_wins": self.sequence_wins,
        }