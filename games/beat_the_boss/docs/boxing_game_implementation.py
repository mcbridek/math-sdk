"""
Boxing Casino Game - Practical Implementation
Using Stake Engine Math SDK Framework
"""

from typing import Dict, List, Tuple, Optional
import random
from dataclasses import dataclass
from enum import Enum

class BoxingMove(Enum):
    """Boxing moves that serve as our 'symbols' in the slot framework"""
    FORWARD = "FWD"    # Move forward (positioning)
    BACKWARD = "BWD"   # Move backward (defensive)
    PUNCH = "PUN"      # Basic punch attack
    UPPERCUT = "UPP"   # Power uppercut
    DUCK = "DUK"       # Duck/dodge
    HURT = "HRT"       # Take damage
    DIZZY = "DIZ"      # Stunned state
    KNOCKOUT = "KO"    # Knockout blow

@dataclass
class SequenceResult:
    """Result of evaluating a move sequence (equivalent to line win)"""
    sequence: str
    base_damage: float
    multiplier: float
    final_win: float
    description: str
    special_conditions: List[str]

@dataclass
class FighterState:
    """Current state of fighters (health bars)"""
    player_health: float = 100.0
    opponent_health: float = 100.0
    player_stamina: float = 100.0
    dodge_streak: int = 0
    attack_streak: int = 0
    round_number: int = 1

class BoxingGameConfig:
    """Configuration class following Stake Engine patterns"""
    
    def __init__(self):
        # Basic game configuration
        self.game_id = "boxing_champion"
        self.provider_number = 1001
        self.working_name = "Boxing Champion"
        self.wincap = 5000.0  # 5000x maximum win
        self.rtp = 0.96
        self.win_type = "sequence_based"
        
        # Boxing-specific settings
        self.max_sequence_length = 6
        self.health_bonus_threshold = 25.0
        self.comeback_threshold = 10.0
        
        # Define move sequences (our "paylines")
        self.move_sequences = self._define_sequences()
        
        # Paytable mapping sequences to base payouts
        self.paytable = self._build_paytable()
        
        # Distribution weights for move generation
        self.move_weights = self._define_move_weights()
    
    def _define_sequences(self) -> Dict[str, Dict]:
        """Define winning move sequences (equivalent to paylines)"""
        return {
            # Basic Attack Sequences (Common, Low Payout)
            "FWD-PUN": {
                "damage": 10, "multiplier": 1.5, "frequency": "common",
                "description": "Forward punch combo"
            },
            "PUN-PUN": {
                "damage": 15, "multiplier": 2.0, "frequency": "common",
                "description": "Double punch"
            },
            "BWD-PUN": {
                "damage": 12, "multiplier": 2.5, "frequency": "common", 
                "description": "Counter punch"
            },
            
            # Power Sequences (Uncommon, Medium Payout)
            "FWD-UPP": {
                "damage": 25, "multiplier": 5.0, "frequency": "uncommon",
                "description": "Forward uppercut"
            },
            "PUN-PUN-UPP": {
                "damage": 35, "multiplier": 8.0, "frequency": "uncommon",
                "description": "Combo uppercut"
            },
            "DUK-UPP": {
                "damage": 40, "multiplier": 12.0, "frequency": "rare",
                "description": "Counter uppercut", "special": "perfect_counter"
            },
            
            # Perfect Defense Sequences (Rare, High Payout)
            "DUK-DUK-UPP": {
                "damage": 50, "multiplier": 15.0, "frequency": "rare",
                "description": "Perfect dodge combo", "special": "perfect_defense"
            },
            "BWD-DUK-FWD-UPP": {
                "damage": 60, "multiplier": 20.0, "frequency": "very_rare",
                "description": "Matrix dodge combo", "special": "matrix_style"
            },
            "DUK-BWD-DUK-UPP-KO": {
                "damage": 100, "multiplier": 100.0, "frequency": "legendary",
                "description": "Perfect defense knockout", "special": "legendary_sequence"
            },
            
            # Knockout Sequences (Very Rare, Maximum Payout)
            "UPP-KO": {
                "damage": 100, "multiplier": 25.0, "frequency": "very_rare",
                "description": "Uppercut knockout", "special": "knockout"
            },
            "DUK-KO": {
                "damage": 100, "multiplier": 50.0, "frequency": "legendary", 
                "description": "Counter knockout", "special": "perfect_counter_ko",
                "conditions": ["dodge_previous_attack"]
            },
            
            # The Holy Grail (Maximum Win)
            "DUK-DUK-DUK-UPP-KO": {
                "damage": 100, "multiplier": 5000.0, "frequency": "mythical",
                "description": "The Perfect Fight", "special": "perfect_fight",
                "conditions": ["dodge_all_attacks", "single_knockout_blow"]
            },
            
            # Comeback Sequences (Conditional High Payout)
            "HRT-DIZ-UPP-KO": {
                "damage": 100, "multiplier": 100.0, "frequency": "legendary",
                "description": "Miracle comeback", "special": "comeback_victory",
                "conditions": ["health_below_20"]
            },
        }
    
    def _build_paytable(self) -> Dict[Tuple[int, str], float]:
        """Build paytable following Stake Engine format"""
        paytable = {}
        
        for sequence, data in self.move_sequences.items():
            # Convert sequence to (length, sequence_name) format
            length = len(sequence.split('-'))
            paytable[(length, sequence)] = data["damage"] * data["multiplier"]
        
        return paytable
    
    def _define_move_weights(self) -> Dict[str, Dict]:
        """Define probability weights for move generation"""
        return {
            "aggressive": {
                BoxingMove.FORWARD.value: 25.0,
                BoxingMove.PUNCH.value: 30.0,
                BoxingMove.UPPERCUT.value: 10.0,
                BoxingMove.DUCK.value: 15.0,
                BoxingMove.BACKWARD.value: 10.0,
                BoxingMove.HURT.value: 8.0,
                BoxingMove.DIZZY.value: 2.0,
            },
            "defensive": {
                BoxingMove.BACKWARD.value: 25.0,
                BoxingMove.DUCK.value: 30.0,
                BoxingMove.PUNCH.value: 15.0,
                BoxingMove.FORWARD.value: 10.0,
                BoxingMove.UPPERCUT.value: 5.0,
                BoxingMove.HURT.value: 12.0,
                BoxingMove.DIZZY.value: 3.0,
            },
            "balanced": {
                BoxingMove.FORWARD.value: 20.0,
                BoxingMove.BACKWARD.value: 15.0,
                BoxingMove.PUNCH.value: 25.0,
                BoxingMove.UPPERCUT.value: 8.0,
                BoxingMove.DUCK.value: 20.0,
                BoxingMove.HURT.value: 10.0,
                BoxingMove.DIZZY.value: 2.0,
            }
        }

class BoxingWinManager:
    """Manages win calculations and health states (extends Stake's WinManager)"""
    
    def __init__(self, config: BoxingGameConfig):
        self.config = config
        self.fighter_state = FighterState()
        self.current_sequence = []
        self.total_win = 0.0
        self.round_wins = []
        
    def generate_move(self, style: str = "balanced") -> str:
        """Generate next move based on current fighter state and strategy"""
        weights = self.config.move_weights[style]
        
        # Adjust weights based on current state
        adjusted_weights = self._adjust_weights_by_state(weights)
        
        # Random selection based on weights
        moves = list(adjusted_weights.keys())
        probabilities = list(adjusted_weights.values())
        total_weight = sum(probabilities)
        probabilities = [p/total_weight for p in probabilities]
        
        return random.choices(moves, weights=probabilities)[0]
    
    def _adjust_weights_by_state(self, base_weights: Dict[str, float]) -> Dict[str, float]:
        """Adjust move weights based on current fighter state"""
        weights = base_weights.copy()
        
        # Low health increases defensive moves
        if self.fighter_state.player_health < 30:
            weights[BoxingMove.DUCK.value] *= 1.5
            weights[BoxingMove.BACKWARD.value] *= 1.3
            
        # High health increases aggressive moves  
        if self.fighter_state.player_health > 70:
            weights[BoxingMove.FORWARD.value] *= 1.3
            weights[BoxingMove.UPPERCUT.value] *= 1.2
            
        # Opponent low on health increases finishing moves
        if self.fighter_state.opponent_health < 30:
            weights[BoxingMove.UPPERCUT.value] *= 2.0
            # Add knockout possibility
            weights[BoxingMove.KNOCKOUT.value] = 2.0
            
        return weights
    
    def evaluate_sequence(self, moves: List[str]) -> Optional[SequenceResult]:
        """Evaluate current move sequence for wins"""
        sequence_key = "-".join(moves)
        
        # Check for exact sequence match
        if sequence_key in self.config.move_sequences:
            sequence_data = self.config.move_sequences[sequence_key]
            
            # Check special conditions
            if not self._check_special_conditions(sequence_data.get("conditions", [])):
                return None
                
            base_damage = sequence_data["damage"]
            base_multiplier = sequence_data["multiplier"]
            
            # Apply state-based multiplier bonuses
            final_multiplier = self._calculate_final_multiplier(base_multiplier)
            
            final_win = base_damage * final_multiplier
            
            return SequenceResult(
                sequence=sequence_key,
                base_damage=base_damage,
                multiplier=final_multiplier,
                final_win=final_win,
                description=sequence_data["description"],
                special_conditions=sequence_data.get("conditions", [])
            )
        
        return None
    
    def _check_special_conditions(self, conditions: List[str]) -> bool:
        """Check if special sequence conditions are met"""
        for condition in conditions:
            if condition == "dodge_previous_attack" and self.fighter_state.dodge_streak < 1:
                return False
            elif condition == "dodge_all_attacks" and self.fighter_state.dodge_streak < 3:
                return False
            elif condition == "health_below_20" and self.fighter_state.player_health >= 20:
                return False
            elif condition == "single_knockout_blow" and self.fighter_state.opponent_health > 50:
                return False
                
        return True
    
    def _calculate_final_multiplier(self, base_multiplier: float) -> float:
        """Calculate final multiplier with all bonuses"""
        multiplier = base_multiplier
        
        # Health-based bonuses
        if self.fighter_state.player_health < 25:  # Desperation bonus
            multiplier *= 1.5
        elif self.fighter_state.player_health > 75:  # Healthy fighter bonus
            multiplier *= 1.2
            
        # Streak bonuses
        if self.fighter_state.dodge_streak >= 3:
            multiplier *= (1 + self.fighter_state.dodge_streak * 0.5)
            
        if self.fighter_state.attack_streak >= 3:
            multiplier *= (1 + self.fighter_state.attack_streak * 0.3)
            
        # Round progression bonus
        if self.fighter_state.round_number > 5:
            multiplier *= (1 + (self.fighter_state.round_number - 5) * 0.1)
            
        return multiplier
    
    def update_fighter_state(self, move: str, result: Optional[SequenceResult] = None):
        """Update fighter states based on move and result"""
        # Update streaks
        if move in ["DUK", "BWD"]:
            self.fighter_state.dodge_streak += 1
            self.fighter_state.attack_streak = 0
        elif move in ["PUN", "UPP"]:
            self.fighter_state.attack_streak += 1
            self.fighter_state.dodge_streak = 0
        else:
            self.fighter_state.dodge_streak = 0
            self.fighter_state.attack_streak = 0
            
        # Apply damage/healing based on move
        if move == "HRT":
            self.fighter_state.player_health = max(0, self.fighter_state.player_health - 15)
        elif move == "DIZ":
            self.fighter_state.player_health = max(0, self.fighter_state.player_health - 10)
            self.fighter_state.player_stamina = max(0, self.fighter_state.player_stamina - 20)
            
        # Apply result damage to opponent
        if result:
            damage = result.base_damage
            self.fighter_state.opponent_health = max(0, self.fighter_state.opponent_health - damage)

class BoxingGameState:
    """Main game state manager (extends Stake's GameState)"""
    
    def __init__(self, config: BoxingGameConfig):
        self.config = config
        self.win_manager = BoxingWinManager(config)
        self.current_round = []
        self.round_complete = False
        self.match_result = None
        
        # Stake Engine integration
        self.library = []  # Stores completed simulations
        self.current_book = {}  # Current simulation data
        self.events = []  # Game events for frontend
        
    def run_simulation(self, sim_id: int) -> Dict:
        """Run complete boxing match simulation"""
        # Reset for new simulation
        self._reset_simulation()
        
        # Generate fight sequence
        fight_result = self._simulate_boxing_match()
        
        # Create book entry (following Stake format)
        book = {
            "id": sim_id,
            "payoutMultiplier": fight_result["total_multiplier"],
            "events": self.events,
            "criteria": fight_result["win_type"],
            "baseGameWins": fight_result["base_wins"],
            "freeGameWins": fight_result["bonus_wins"],  # Knockout rounds
            "matchResult": fight_result
        }
        
        self.library.append(book)
        return book
    
    def _reset_simulation(self):
        """Reset all state for new simulation"""
        self.win_manager.fighter_state = FighterState()
        self.current_round = []
        self.round_complete = False
        self.events = []
        self.win_manager.total_win = 0.0
        
    def _simulate_boxing_match(self) -> Dict:
        """Simulate complete boxing match"""
        total_multiplier = 0.0
        base_wins = 0.0
        bonus_wins = 0.0
        match_events = []
        
        # Generate moves until fight ends
        while not self._is_fight_over() and len(self.current_round) < self.config.max_sequence_length:
            # Generate next move
            move = self.win_manager.generate_move()
            self.current_round.append(move)
            
            # Check for winning sequences
            win_result = self.win_manager.evaluate_sequence(self.current_round)
            
            if win_result:
                # Add win to totals
                if win_result.special_conditions:
                    bonus_wins += win_result.final_win
                else:
                    base_wins += win_result.final_win
                    
                total_multiplier += win_result.multiplier
                
                # Create win event
                self._add_win_event(win_result)
                
                # Check for knockout
                if "KO" in move or self.win_manager.fighter_state.opponent_health <= 0:
                    self._add_knockout_event(win_result)
                    break
            
            # Update fighter states
            self.win_manager.update_fighter_state(move, win_result)
            
            # Add move event
            self._add_move_event(move)
        
        # Determine final result
        win_type = self._determine_win_type(total_multiplier)
        
        return {
            "total_multiplier": total_multiplier,
            "base_wins": base_wins, 
            "bonus_wins": bonus_wins,
            "win_type": win_type,
            "final_sequence": "-".join(self.current_round),
            "player_health": self.win_manager.fighter_state.player_health,
            "opponent_health": self.win_manager.fighter_state.opponent_health
        }
    
    def _is_fight_over(self) -> bool:
        """Check if fight should end"""
        return (self.win_manager.fighter_state.player_health <= 0 or 
                self.win_manager.fighter_state.opponent_health <= 0 or
                "KO" in self.current_round)
    
    def _determine_win_type(self, multiplier: float) -> str:
        """Determine win category based on multiplier"""
        if multiplier >= 1000:
            return "knockout"
        elif multiplier >= 100:
            return "dominant_victory"
        elif multiplier >= 10:
            return "clear_victory"
        elif multiplier > 0:
            return "close_victory"
        else:
            return "loss"
    
    def _add_win_event(self, result: SequenceResult):
        """Add win event following Stake format"""
        event = {
            "index": len(self.events),
            "type": "winInfo",
            "totalWin": result.final_win,
            "wins": [{
                "sequence": result.sequence,
                "damage": result.base_damage,
                "multiplier": result.multiplier,
                "win": result.final_win,
                "description": result.description,
                "meta": {
                    "playerHealth": self.win_manager.fighter_state.player_health,
                    "opponentHealth": self.win_manager.fighter_state.opponent_health,
                    "specialConditions": result.special_conditions
                }
            }]
        }
        self.events.append(event)
    
    def _add_move_event(self, move: str):
        """Add individual move event"""
        event = {
            "index": len(self.events),
            "type": "move",
            "move": move,
            "playerHealth": self.win_manager.fighter_state.player_health,
            "opponentHealth": self.win_manager.fighter_state.opponent_health,
            "currentSequence": "-".join(self.current_round)
        }
        self.events.append(event)
    
    def _add_knockout_event(self, result: SequenceResult):
        """Add knockout event"""
        event = {
            "index": len(self.events),
            "type": "knockout",
            "winner": "player" if self.win_manager.fighter_state.opponent_health <= 0 else "opponent",
            "method": "knockout",
            "finalMultiplier": result.multiplier,
            "sequence": result.sequence
        }
        self.events.append(event)

# Usage Example and Testing
def run_boxing_game_simulation():
    """Example of running the boxing game simulation"""
    
    # Initialize game
    config = BoxingGameConfig()
    game = BoxingGameState(config)
    
    # Run multiple simulations to test distribution
    results = []
    win_frequencies = {"loss": 0, "close_victory": 0, "clear_victory": 0, "dominant_victory": 0, "knockout": 0}
    
    for sim_id in range(1000):  # Run 1000 simulations
        result = game.run_simulation(sim_id)
        results.append(result)
        
        # Track win frequencies
        win_type = result["matchResult"]["win_type"]
        win_frequencies[win_type] += 1
    
    # Print results
    print("Boxing Game Simulation Results (1000 rounds)")
    print("=" * 50)
    
    total_rtp = 0
    for win_type, count in win_frequencies.items():
        frequency = count / 1000 * 100
        print(f"{win_type.replace('_', ' ').title()}: {count} ({frequency:.1f}%)")
    
    # Calculate average multipliers
    multipliers = [r["payoutMultiplier"] for r in results]
    avg_multiplier = sum(multipliers) / len(multipliers)
    max_multiplier = max(multipliers)
    
    print(f"\nAverage Multiplier: {avg_multiplier:.2f}x")
    print(f"Maximum Multiplier: {max_multiplier:.2f}x")
    print(f"Estimated RTP: {avg_multiplier/100*96:.2f}%")
    
    # Show some example winning sequences
    big_wins = [r for r in results if r["payoutMultiplier"] > 10]
    print(f"\nBig Wins (>10x): {len(big_wins)}")
    
    for win in big_wins[:5]:  # Show first 5 big wins
        match_result = win["matchResult"]
        print(f"  Sequence: {match_result['final_sequence']} - {win['payoutMultiplier']:.1f}x")

if __name__ == "__main__":
    run_boxing_game_simulation()
