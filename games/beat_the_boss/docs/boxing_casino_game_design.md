# Boxing Casino Game Design using Stake Engine Math SDK

## Game Overview

A casino game based on boxing mechanics where players control a fighter through sequences of moves. Each move sequence acts as a "payline" with different combinations yielding different multipliers and payouts.

## Core Boxing Mechanics Mapped to Casino Framework

### Available Moves (Symbols)
- **FWD** - Move Forward (Low risk, positioning)
- **BWD** - Move Backward (Defensive, multiplier preservation)  
- **PUN** - Punch (Base attack, standard payout)
- **UPP** - Uppercut (High damage, high multiplier)
- **DUK** - Duck (Defensive, dodge incoming attacks)
- **HRT** - Hurt (Damage taken, negative effect)
- **DIZ** - Dizzy (Stunned state, vulnerability)
- **KO** - Knockout (Ultimate win condition, max multiplier)

### Health Bar System
- **Player Health**: 100 HP (decreases with HRT/DIZ moves)
- **Opponent Health**: 100 HP (decreases with successful PUN/UPP moves)
- **Health affects multipliers**: Lower health = higher risk/reward

## Payline System (Move Sequences)

### 1. Basic Attack Sequences
```python
basic_sequences = {
    # Standard attack combos
    "FWD-PUN-PUN": {"multiplier": 2x, "damage": 15, "description": "Basic combo"},
    "FWD-FWD-PUN": {"multiplier": 1.5x, "damage": 10, "description": "Pressure punch"},
    "BWD-PUN-FWD": {"multiplier": 2.5x, "damage": 12, "description": "Counter attack"},
    
    # Power sequences
    "FWD-UPP": {"multiplier": 5x, "damage": 25, "description": "Power uppercut"},
    "PUN-PUN-UPP": {"multiplier": 8x, "damage": 35, "description": "Combo uppercut"},
    "DUK-UPP": {"multiplier": 12x, "damage": 40, "description": "Counter uppercut"},
}
```

### 2. Defensive Sequences (Multiplier Preservation)
```python
defensive_sequences = {
    # Perfect defense (multiplier bonuses)
    "DUK-DUK-UPP": {"multiplier": 15x, "damage": 50, "description": "Perfect dodge combo"},
    "BWD-DUK-FWD-UPP": {"multiplier": 20x, "damage": 60, "description": "Matrix dodge uppercut"},
    "DUK-BWD-DUK-KO": {"multiplier": 100x, "damage": 100, "description": "Legendary sequence"},
    
    # Multiplier preservation
    "BWD-BWD": {"multiplier": "preserve+0.5x", "damage": 0, "description": "Safe positioning"},
    "DUK": {"multiplier": "preserve+1x", "damage": 0, "description": "Successful dodge"},
}
```

### 3. High-Risk High-Reward Sequences
```python
knockout_sequences = {
    # One-shot sequences (player's ultimate goal)
    "DUK-KO": {"multiplier": 50x, "condition": "dodge_all_previous", "description": "Perfect dodge KO"},
    "UPP-KO": {"multiplier": 25x, "condition": "critical_hit", "description": "Uppercut knockout"},
    "FWD-FWD-FWD-UPP-KO": {"multiplier": 75x, "condition": "aggressive_buildup", "description": "Relentless assault"},
    
    # Comeback sequences (low health bonus)
    "HRT-DIZ-UPP-KO": {"multiplier": 100x, "condition": "health<20", "description": "Miracle comeback"},
}
```

## Stake Engine Implementation

### Game Configuration
```python
class BoxingGameConfig(Config):
    def __init__(self):
        super().__init__()
        self.game_id = "boxing_champion"
        self.working_name = "Boxing Champion"
        self.win_type = "sequence_based"
        self.wincap = 5000  # 5000x max win
        self.rtp = 0.96
        
        # Boxing specific parameters
        self.max_rounds = 12
        self.health_multiplier_bonus = True
        self.comeback_mechanics = True
        
        # Define move sequences as "paylines"
        self.move_sequences = self.define_boxing_sequences()
        
        # Paytable mapping sequences to payouts
        self.paytable = self.build_boxing_paytable()
```

### BetMode Distributions
```python
boxing_betmode = BetMode(
    name="boxing_match",
    cost=1.0,
    rtp=0.96,
    max_win=5000,
    distributions=[
        # Knockout wins (rare, high payout)
        Distribution(
            criteria="knockout",
            quota=0.001,  # 0.1% chance
            win_criteria=1000,  # 1000x+ wins
            conditions={
                "sequence_weights": {"KO_sequences": 1},
                "health_requirement": "<20",
                "force_knockout": True,
            }
        ),
        
        # Perfect defense wins (very rare, maximum payout) 
        Distribution(
            criteria="perfect_defense",
            quota=0.0005,  # 0.05% chance
            win_criteria=5000,  # Maximum win
            conditions={
                "sequence_weights": {"perfect_dodge_sequences": 1},
                "dodge_all_attacks": True,
                "single_uppercut_ko": True,
            }
        ),
        
        # Standard winning rounds
        Distribution(
            criteria="round_win",
            quota=0.25,  # 25% chance
            conditions={
                "sequence_weights": {"attack_combos": 70, "defense_combos": 30},
                "health_advantage": True,
            }
        ),
        
        # Close fights (moderate wins)
        Distribution(
            criteria="close_fight",
            quota=0.35,  # 35% chance
            conditions={
                "sequence_weights": {"balanced_sequences": 100},
                "health_differential": "<20",
            }
        ),
        
        # Losses/No significant damage
        Distribution(
            criteria="loss",
            quota=0.4,  # 40% chance
            win_criteria=0.0,
            conditions={
                "sequence_weights": {"defensive_only": 60, "failed_attacks": 40},
            }
        ),
    ]
)
```

### Win Calculation System
```python
class BoxingWinCalculator:
    def __init__(self, config):
        self.config = config
        self.player_health = 100
        self.opponent_health = 100
        self.current_multiplier = 1.0
        self.dodge_streak = 0
        self.attack_streak = 0
    
    def evaluate_sequence(self, moves):
        """Evaluate a sequence of boxing moves for wins"""
        sequence_key = "-".join(moves)
        base_win = 0
        multiplier = 1.0
        
        # Check for exact sequence matches
        if sequence_key in self.config.move_sequences:
            sequence_data = self.config.move_sequences[sequence_key]
            base_win = sequence_data.get("damage", 0)
            multiplier = sequence_data.get("multiplier", 1.0)
            
            # Apply health-based bonuses
            if self.player_health < 25:  # Desperation bonus
                multiplier *= 1.5
            elif self.player_health > 75:  # Healthy fighter bonus  
                multiplier *= 1.2
                
            # Perfect defense bonus
            if self.dodge_streak >= 3:
                multiplier *= (1 + self.dodge_streak * 0.5)
                
            # Aggressive bonus
            if self.attack_streak >= 3:
                multiplier *= (1 + self.attack_streak * 0.3)
        
        return {
            "base_win": base_win,
            "multiplier": multiplier,
            "final_win": base_win * multiplier,
            "sequence": sequence_key,
            "health_bonus": self.get_health_bonus(),
        }
    
    def update_health(self, move, damage_taken=0, damage_dealt=0):
        """Update health based on moves"""
        self.player_health = max(0, self.player_health - damage_taken)
        self.opponent_health = max(0, self.opponent_health - damage_dealt)
        
        # Update streaks
        if move in ["DUK", "BWD"]:
            self.dodge_streak += 1
            self.attack_streak = 0
        elif move in ["PUN", "UPP"]:
            self.attack_streak += 1
            self.dodge_streak = 0
        else:
            self.attack_streak = 0
            self.dodge_streak = 0
```

## Event System for Boxing Rounds

### Boxing Event Types
```python
boxing_events = {
    "round_start": {"type": "reveal", "board": "fighter_positions"},
    "move_sequence": {"type": "winInfo", "moves": [], "damage": 0, "multiplier": 1.0},
    "health_update": {"type": "healthUpdate", "player_hp": 100, "opponent_hp": 100},
    "combo_bonus": {"type": "comboBonus", "streak": 0, "multiplier": 1.0},
    "round_result": {"type": "setWin", "winner": "player/opponent", "method": "KO/decision"},
    "match_result": {"type": "finalWin", "total_multiplier": 1.0, "match_bonus": 0},
}
```

### Special Win Conditions

#### Maximum Multiplier Sequence (The Holy Grail)
```python
perfect_sequence = {
    # Dodge all opponent attacks, then land single KO uppercut
    "sequence": ["DUK", "DUK", "DUK", "DUK", "UPP", "KO"],
    "conditions": {
        "dodge_all_previous_attacks": True,
        "single_knockout_blow": True,
        "perfect_health": True,
    },
    "multiplier": 5000,  # Maximum possible win
    "probability": 0.0001,  # Extremely rare
    "description": "The Perfect Fight - dodge everything, one-punch KO"
}
```

#### Comeback Victory
```python
comeback_sequence = {
    "sequence": ["HRT", "HRT", "DIZ", "DUK", "UPP", "KO"], 
    "conditions": {
        "player_health": "<10",
        "opponent_health": ">50",
        "comeback_victory": True,
    },
    "multiplier": 2500,
    "probability": 0.0002,
    "description": "Miracle Comeback - from the brink of defeat"
}
```

## RTP Distribution Analysis

### Win Frequency Distribution
```
- No Win (Loss): 40% - 0x multiplier
- Small Wins: 35% - 0.1x to 2x multiplier  
- Medium Wins: 20% - 2x to 10x multiplier
- Big Wins: 4.5% - 10x to 100x multiplier
- Major Wins: 0.49% - 100x to 1000x multiplier
- Jackpot Wins: 0.01% - 1000x to 5000x multiplier
```

### Sequence Probability Weights
```python
sequence_weights = {
    # Basic combinations (high frequency, low payout)
    "basic_attacks": {
        "FWD-PUN": 15.0,
        "BWD-PUN": 12.0, 
        "PUN-PUN": 10.0,
        "weight_total": 37.0,
        "avg_multiplier": 1.5
    },
    
    # Advanced combinations (medium frequency, medium payout)
    "combo_attacks": {
        "FWD-PUN-UPP": 5.0,
        "DUK-PUN-PUN": 4.0,
        "BWD-FWD-UPP": 3.0,
        "weight_total": 12.0,
        "avg_multiplier": 8.0
    },
    
    # Expert sequences (low frequency, high payout)
    "expert_sequences": {
        "DUK-DUK-UPP-KO": 0.1,
        "BWD-DUK-FWD-UPP-KO": 0.05,
        "perfect_defense_ko": 0.01,
        "weight_total": 0.16,
        "avg_multiplier": 1500
    }
}
```

## Implementation Guidelines

### 1. Game Flow Integration
```python
def run_boxing_round(self, sim):
    """Run a complete boxing round simulation"""
    self.reset_seed(sim)
    self.reset_health_bars()
    
    round_complete = False
    move_sequence = []
    
    while not round_complete and len(move_sequence) < 10:
        # Generate next move based on current conditions
        next_move = self.generate_move()
        move_sequence.append(next_move)
        
        # Evaluate current sequence for wins
        win_data = self.evaluate_sequence(move_sequence)
        
        # Update health and check for round end conditions
        if self.check_knockout_condition() or self.check_round_limit():
            round_complete = True
            
        # Update win manager
        self.win_manager.update_spinwin(win_data["final_win"])
        
    self.evaluate_final_round_result()
```

### 2. Frontend Integration
The boxing game can use Stake's Web SDK for visual representation:
- Animated fighters showing move sequences
- Health bars with real-time updates  
- Move sequence display showing current "payline"
- Multiplier meters building up during combos
- Dramatic knockout animations for big wins

### 3. Balancing Considerations
- **Skill vs Luck**: While moves are generated randomly, players feel agency through the boxing theme
- **Volatility Control**: Health-based multipliers create natural volatility scaling
- **Engagement**: Multiple small wins (successful punches) leading to potential big wins (knockouts)
- **Maximum Win Protection**: Strict conditions on 5000x sequences prevent excessive payouts

## Summary

This boxing casino game leverages Stake Engine's proven math framework while creating an engaging, thematic experience. The key innovation is treating boxing move sequences as "paylines" with health-based multiplier modifiers, creating natural drama and player engagement while maintaining rigorous mathematical controls for RTP and maximum win exposure.

The system supports:
- ✅ Traditional casino math (RTP, volatility, max win caps)
- ✅ Engaging boxing theme with meaningful move sequences  
- ✅ Multiple paths to victory (defensive, aggressive, comeback)
- ✅ Scalable difficulty and payout structures
- ✅ Integration with Stake's existing infrastructure

The "perfect fight" scenario (dodge all attacks, single uppercut KO) serves as the ultimate jackpot sequence, providing the maximum multiplier while maintaining extremely low probability to protect the house edge.
