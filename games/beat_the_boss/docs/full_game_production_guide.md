# Beat the Boss - Full Production Game Guide

## Overview

This comprehensive guide details all requirements for building a **production-ready** Beat the Boss game frontend that integrates with the Stake Engine platform. This is NOT a simple test—it's a complete, polished casino game.

**Estimated Development Time:** 6-12 weeks (2-3 developers)
**Technology Stack:** Svelte 5 + PixiJS + TurboRepo
**Target Platforms:** Desktop (Chrome, Firefox, Safari) + Mobile (iOS Safari, Android Chrome)

---

## Table of Contents

1. [Technical Architecture](#1-technical-architecture)
2. [Project Setup](#2-project-setup)
3. [Core Game Systems](#3-core-game-systems)
4. [UI Components](#4-ui-components)
5. [Animation Requirements](#5-animation-requirements)
6. [Audio System](#6-audio-system)
7. [RGS Integration](#7-rgs-integration)
8. [Event Processing](#8-event-processing)
9. [Responsive Design](#9-responsive-design)
10. [Localization](#10-localization)
11. [Performance Optimization](#11-performance-optimization)
12. [Testing Strategy](#12-testing-strategy)
13. [Deployment Checklist](#13-deployment-checklist)
14. [Compliance Requirements](#14-compliance-requirements)

---

## 1. Technical Architecture

### Frontend Technology Stack

#### Core Framework
```json
{
  "framework": "SvelteKit",
  "version": "Svelte 5 (runes)",
  "rendering": "PixiJS v8",
  "integration": "pixi-svelte (Stake Engine package)",
  "monorepo": "TurboRepo",
  "package-manager": "pnpm v10.5.0",
  "node-version": "18.18.0"
}
```

#### Required Packages

**Stake Engine Packages:**
- `@stake-engine/pixi-svelte` - Core PixiJS + Svelte integration
- `@stake-engine/utils-event-emitter` - Event-driven architecture
- `@stake-engine/utils-xstate` - Betting state machine
- `@stake-engine/utils-layout` - Responsive layout system
- `@stake-engine/components-ui-pixi` - Pre-built PixiJS UI components
- `@stake-engine/components-ui-html` - HTML overlay components
- `@stake-engine/utils-motion` - Animation utilities
- `@stake-engine/utils-formatting` - Currency/number formatting

**Third-Party Packages:**
- `xstate` - Finite state machines
- `@pixi/spine` - Spine animation support
- `@lingui/core` - Internationalization
- `gsap` - Advanced animations
- `howler.js` - Audio management

### Monorepo Structure

```
beat-the-boss/
├── apps/
│   └── beat-the-boss/             # Main game application
│       ├── src/
│       │   ├── routes/
│       │   │   └── +page.svelte   # Entry point
│       │   ├── components/
│       │   │   ├── Game.svelte    # Main game component
│       │   │   ├── combat/        # Combat components
│       │   │   ├── ui/            # UI overlays
│       │   │   └── modals/        # Modal screens
│       │   ├── game/
│       │   │   ├── context.ts     # Context setup
│       │   │   ├── eventEmitter.ts
│       │   │   ├── bookEventHandlerMap.ts
│       │   │   ├── typesBookEvent.ts
│       │   │   └── typesEmitterEvent.ts
│       │   ├── assets/
│       │   │   ├── images/
│       │   │   ├── spines/        # Spine animations
│       │   │   └── sounds/
│       │   ├── stories/           # Storybook stories
│       │   │   ├── data/
│       │   │   └── *.stories.svelte
│       │   └── lib/
│       │       ├── constants.ts
│       │       └── utils.ts
│       └── package.json
│
├── packages/                      # Shared packages (if needed)
└── turbo.json                    # TurboRepo config
```

### Context System

The Stake Engine uses Svelte's context API to share state across components. Four major contexts:

```typescript
// game/context.ts
import { setContext } from 'svelte';
import { createEventEmitter } from '@stake-engine/utils-event-emitter';
import { createGameActor } from '@stake-engine/utils-xstate';
import { createLayout } from '@stake-engine/utils-layout';
import { createApp } from '@stake-engine/pixi-svelte';

export const setGameContext = () => {
  // 1. Event Emitter Context
  const { eventEmitter } = createEventEmitter<EmitterEvent>();
  setContextEventEmitter({ eventEmitter });

  // 2. XState Context (betting state machine)
  const gameActor = createGameActor();
  setContextXstate({
    stateXstate: gameActor.state,
    stateXstateDerived: {
      isIdle: () => gameActor.state.value === 'idle',
      isPlaying: () => gameActor.state.matches({ playing: 'playing' }),
      isBetting: () => gameActor.state.matches('bet'),
      isAutoBetting: () => gameActor.state.matches('autoBet'),
    }
  });

  // 3. Layout Context (responsive)
  const { stateLayout, stateLayoutDerived } = createLayout();
  setContextLayout({ stateLayout, stateLayoutDerived });

  // 4. App Context (PixiJS)
  const stateApp = createApp();
  setContextApp({ stateApp });
};
```

---

## 2. Project Setup

### Initial Setup Commands

```bash
# 1. Create new game from template
cd apps/
pnpm create stake-engine-game beat-the-boss

# 2. Install dependencies
cd beat-the-boss
pnpm install

# 3. Start development server
pnpm dev

# 4. Open Storybook for component development
pnpm storybook
```

### Environment Configuration

Create `.env` file:
```env
VITE_RGS_URL=https://dev-team.cdn.stake-engine.com
VITE_GAME_ID=beat_the_boss
VITE_GAME_VERSION=1.0.0
VITE_DEBUG_MODE=true
```

### TypeScript Configuration

Ensure strict typing:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "paths": {
      "$lib/*": ["./src/lib/*"],
      "$game/*": ["./src/game/*"],
      "$components/*": ["./src/components/*"]
    }
  }
}
```

---

## 3. Core Game Systems

### 3.1 Event System Architecture

Beat the Boss uses **event-driven architecture** to coordinate between components:

```
RGS Book → bookEventHandler → emitterEvents → Component Handlers → UI Updates
```

#### Book Event Types

Define all possible events from the backend:

```typescript
// game/typesBookEvent.ts

export type BookEventReveal = {
  index: number;
  type: 'reveal';
  move_sequence: string[];           // ["FWD", "PUN", "UPP"]
  player_health: number;
  boss_health: number;
  gameType: 'basegame';
};

export type BookEventMoveGenerated = {
  index: number;
  type: 'moveGenerated';
  move: string;                      // "PUN"
  sequence_index: number;            // 0-5
  move_class: 'offensive' | 'defensive' | 'damage' | 'knockout';
};

export type BookEventHealthUpdate = {
  index: number;
  type: 'healthUpdate';
  player_health: number;
  boss_health: number;
  damage_to_boss?: number;
  damage_to_player?: number;
};

export type BookEventComboDetected = {
  index: number;
  type: 'comboDetected';
  sequence: string;                  // "FWD-PUN-UPP"
  length: number;
  base_multiplier: number;
  final_multiplier: number;
};

export type BookEventKnockout = {
  index: number;
  type: 'knockout';
  knockout_bonus: number;
};

export type BookEventFinalWin = {
  index: number;
  type: 'finalWin';
  amount: number;
  best_sequence: string;
};

export type BookEvent =
  | BookEventReveal
  | BookEventMoveGenerated
  | BookEventHealthUpdate
  | BookEventComboDetected
  | BookEventKnockout
  | BookEventFinalWin;
```

#### Emitter Event Types

Define frontend-internal events:

```typescript
// game/typesEmitterEvent.ts

export type EmitterEventCombat =
  | { type: 'roundStart'; boss: string }
  | { type: 'moveAnimate'; move: string; moveIndex: number }
  | { type: 'healthBarUpdate'; target: 'player' | 'boss'; health: number; maxHealth: number }
  | { type: 'damageNumberShow'; target: 'player' | 'boss'; amount: number }
  | { type: 'comboFlash'; sequence: string; multiplier: number }
  | { type: 'knockoutSequence' }
  | { type: 'roundComplete' };

export type EmitterEventUI =
  | { type: 'winCounterUpdate'; amount: number }
  | { type: 'winCounterAnimate'; from: number; to: number }
  | { type: 'winCelebration'; tier: 'small' | 'medium' | 'big' | 'legendary' }
  | { type: 'balanceUpdate'; balance: number };

export type EmitterEvent = EmitterEventCombat | EmitterEventUI;
```

#### Book Event Handler Map

```typescript
// game/bookEventHandlerMap.ts
import { eventEmitter } from './eventEmitter';

export const bookEventHandlerMap: BookEventHandlerMap = {
  reveal: async (bookEvent: BookEventOfType<'reveal'>) => {
    // Initialize round
    await eventEmitter.broadcastAsync({
      type: 'roundStart',
      boss: bookEvent.boss_name
    });

    // Reset health bars
    eventEmitter.broadcast({
      type: 'healthBarUpdate',
      target: 'player',
      health: bookEvent.player_health,
      maxHealth: 100
    });

    eventEmitter.broadcast({
      type: 'healthBarUpdate',
      target: 'boss',
      health: bookEvent.boss_health,
      maxHealth: bookEvent.boss_max_health
    });
  },

  moveGenerated: async (bookEvent: BookEventOfType<'moveGenerated'>) => {
    // Animate fighter performing move
    await eventEmitter.broadcastAsync({
      type: 'moveAnimate',
      move: bookEvent.move,
      moveIndex: bookEvent.sequence_index
    });
  },

  healthUpdate: async (bookEvent: BookEventOfType<'healthUpdate'>) => {
    // Update health bars
    eventEmitter.broadcast({
      type: 'healthBarUpdate',
      target: 'player',
      health: bookEvent.player_health,
      maxHealth: 100
    });

    eventEmitter.broadcast({
      type: 'healthBarUpdate',
      target: 'boss',
      health: bookEvent.boss_health,
      maxHealth: bookEvent.boss_max_health
    });

    // Show damage numbers
    if (bookEvent.damage_to_boss) {
      eventEmitter.broadcast({
        type: 'damageNumberShow',
        target: 'boss',
        amount: bookEvent.damage_to_boss
      });
    }

    if (bookEvent.damage_to_player) {
      eventEmitter.broadcast({
        type: 'damageNumberShow',
        target: 'player',
        amount: bookEvent.damage_to_player
      });
    }
  },

  comboDetected: async (bookEvent: BookEventOfType<'comboDetected'>) => {
    // Flash combo sequence
    await eventEmitter.broadcastAsync({
      type: 'comboFlash',
      sequence: bookEvent.sequence,
      multiplier: bookEvent.final_multiplier
    });

    // Update win counter
    eventEmitter.broadcast({
      type: 'winCounterUpdate',
      amount: bookEvent.final_multiplier
    });
  },

  knockout: async (bookEvent: BookEventOfType<'knockout'>) => {
    // Play knockout cinematic
    await eventEmitter.broadcastAsync({
      type: 'knockoutSequence'
    });
  },

  finalWin: async (bookEvent: BookEventOfType<'finalWin'>) => {
    // Animate win counter
    await eventEmitter.broadcastAsync({
      type: 'winCounterAnimate',
      from: 0,
      to: bookEvent.amount
    });

    // Determine celebration tier
    const betAmount = getCurrentBet();
    const multiplier = bookEvent.amount / betAmount;
    let tier: 'small' | 'medium' | 'big' | 'legendary';

    if (multiplier >= 1000) tier = 'legendary';
    else if (multiplier >= 100) tier = 'big';
    else if (multiplier >= 10) tier = 'medium';
    else tier = 'small';

    // Play celebration
    await eventEmitter.broadcastAsync({
      type: 'winCelebration',
      tier
    });

    // Complete round
    eventEmitter.broadcast({ type: 'roundComplete' });
  }
};
```

### 3.2 State Management (XState)

Use XState for betting logic:

```typescript
// game/bettingMachine.ts
import { createMachine, assign } from 'xstate';

export const bettingMachine = createMachine({
  id: 'betting',
  initial: 'rendering',
  context: {
    balance: 0,
    bet: 1.0,
    selectedBoss: 'macron',
    autoPlayCount: 0,
    roundsCompleted: 0
  },
  states: {
    rendering: {
      on: {
        ASSETS_LOADED: 'idle'
      }
    },
    idle: {
      on: {
        PLACE_BET: {
          target: 'bet',
          guard: 'hasSufficientBalance'
        },
        START_AUTO_BET: 'autoBet',
        SELECT_BOSS: {
          actions: assign({
            selectedBoss: ({ event }) => event.boss
          })
        }
      }
    },
    bet: {
      initial: 'placingBet',
      states: {
        placingBet: {
          invoke: {
            src: 'callWalletPlay',
            onDone: 'playing',
            onError: 'error'
          }
        },
        playing: {
          invoke: {
            src: 'playBookEvents',
            onDone: 'endingRound',
            onError: 'error'
          }
        },
        endingRound: {
          invoke: {
            src: 'callWalletEndRound',
            onDone: 'complete',
            onError: 'error'
          }
        },
        complete: {
          type: 'final'
        },
        error: {
          on: {
            RETRY: 'placingBet',
            CANCEL: '#betting.idle'
          }
        }
      },
      onDone: {
        target: 'idle',
        actions: assign({
          roundsCompleted: ({ context }) => context.roundsCompleted + 1
        })
      }
    },
    autoBet: {
      // Similar structure with loop logic
    }
  }
});
```

### 3.3 RGS Communication Layer

```typescript
// game/rgsClient.ts
import { getParam } from '$lib/utils';

export class RGSClient {
  private sessionID: string;
  private rgsUrl: string;
  private balance: number = 0;

  constructor() {
    this.sessionID = getParam('sessionID') || '';
    this.rgsUrl = getParam('rgs_url') || '';
  }

  async authenticate(): Promise<AuthResponse> {
    const response = await this.post('/wallet/authenticate', {
      sessionID: this.sessionID,
      language: getParam('lang') || 'en'
    });

    this.balance = response.balance.amount / 1000000;
    return response;
  }

  async play(mode: string, amount: number): Promise<PlayResponse> {
    const response = await this.post('/wallet/play', {
      sessionID: this.sessionID,
      mode: mode.toUpperCase(),
      amount: Math.round(amount * 1000000)
    });

    this.balance = response.balance.amount / 1000000;
    return response;
  }

  async endRound(): Promise<EndRoundResponse> {
    const response = await this.post('/wallet/end-round', {
      sessionID: this.sessionID
    });

    this.balance = response.balance.amount / 1000000;
    return response;
  }

  async getBalance(): Promise<number> {
    const response = await this.post('/wallet/balance', {
      sessionID: this.sessionID
    });

    this.balance = response.balance.amount / 1000000;
    return this.balance;
  }

  private async post(endpoint: string, body: any): Promise<any> {
    const url = `https://${this.rgsUrl}${endpoint}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new RGSError(error.code, error.message);
    }

    return response.json();
  }

  getBalance(): number {
    return this.balance;
  }
}

class RGSError extends Error {
  constructor(public code: string, message: string) {
    super(message);
    this.name = 'RGSError';
  }
}
```

---

## 4. UI Components

### 4.1 Boss Selection Screen

```svelte
<!-- components/BossSelection.svelte -->
<script lang="ts">
  import { getContext } from '$game/context';
  import { bossConfig } from '$lib/constants';

  const context = getContext();
  let selectedBoss = $state('macron');

  function selectBoss(boss: string) {
    selectedBoss = boss;
    context.eventEmitter.broadcast({
      type: 'bossSelected',
      boss
    });
  }

  function startFight() {
    context.eventEmitter.broadcast({
      type: 'startFight',
      boss: selectedBoss
    });
  }
</script>

<div class="boss-selection">
  <h1>Choose Your Opponent</h1>

  <div class="boss-cards">
    {#each Object.entries(bossConfig) as [bossName, config]}
      <div
        class="boss-card"
        class:selected={selectedBoss === bossName}
        onclick={() => selectBoss(bossName)}
      >
        <div class="boss-portrait">
          <img src="/assets/bosses/{bossName}.png" alt={config.displayName} />
        </div>

        <h2>{config.displayName}</h2>
        <p class="boss-description">{config.description}</p>

        <div class="boss-stats">
          <div class="stat">
            <span class="label">Bet Cost</span>
            <span class="value">{config.costMultiplier}x</span>
          </div>
          <div class="stat">
            <span class="label">Health</span>
            <span class="value">{config.health} HP</span>
          </div>
          <div class="stat">
            <span class="label">Max Win</span>
            <span class="value">{config.maxWin}x</span>
          </div>
          <div class="stat">
            <span class="label">Hit Rate</span>
            <span class="value">{config.hitRate}%</span>
          </div>
        </div>

        <div class="volatility">
          Volatility: {config.volatility}
        </div>
      </div>
    {/each}
  </div>

  <button class="fight-btn" onclick={startFight} disabled={!selectedBoss}>
    FIGHT!
  </button>
</div>

<style>
  .boss-selection {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
  }

  .boss-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
    margin: 40px 0;
  }

  .boss-card {
    background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
    border: 3px solid transparent;
    border-radius: 15px;
    padding: 25px;
    cursor: pointer;
    transition: all 0.3s;
  }

  .boss-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 30px rgba(255,255,255,0.1);
  }

  .boss-card.selected {
    border-color: #4ecdc4;
    box-shadow: 0 0 30px rgba(78,205,196,0.5);
  }

  .boss-portrait {
    width: 200px;
    height: 200px;
    margin: 0 auto 20px;
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid #444;
  }

  .boss-portrait img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .boss-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 20px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    padding: 10px;
    background: #1a1a1a;
    border-radius: 5px;
  }

  .stat .label {
    font-size: 12px;
    color: #888;
    margin-bottom: 5px;
  }

  .stat .value {
    font-size: 18px;
    font-weight: bold;
    color: #4ecdc4;
  }

  .fight-btn {
    margin-top: 40px;
    padding: 20px 80px;
    font-size: 24px;
    font-weight: bold;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s;
  }

  .fight-btn:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 10px 40px rgba(102,126,234,0.6);
  }

  .fight-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
</style>
```

### 4.2 Combat Arena (Main Game Screen)

```svelte
<!-- components/combat/CombatArena.svelte -->
<script lang="ts">
  import { Canvas } from '@stake-engine/pixi-svelte';
  import { getContext } from '$game/context';
  import HealthBar from './HealthBar.svelte';
  import MoveSequence from './MoveSequence.svelte';
  import WinDisplay from './WinDisplay.svelte';
  import Fighter from './Fighter.svelte';

  const context = getContext();

  let playerHealth = $state(100);
  let bossHealth = $state(150);
  let currentBoss = $state('macron');
  let moveSequence = $state<string[]>([]);
  let currentWin = $state(0);

  // Subscribe to emitter events
  context.eventEmitter.subscribeOnMount({
    healthBarUpdate: (event) => {
      if (event.target === 'player') {
        playerHealth = event.health;
      } else {
        bossHealth = event.health;
      }
    },
    comboFlash: (event) => {
      currentWin = event.multiplier;
    },
    roundStart: (event) => {
      currentBoss = event.boss;
      moveSequence = [];
      currentWin = 0;
    },
    moveAnimate: (event) => {
      moveSequence = [...moveSequence, event.move];
    }
  });
</script>

<div class="combat-arena">
  <!-- PixiJS Canvas -->
  <Canvas width={1920} height={1080}>
    <!-- Background -->
    <sprite
      texture="/assets/backgrounds/{currentBoss}_ring.png"
      x={0}
      y={0}
    />

    <!-- Player Fighter -->
    <Fighter
      side="player"
      x={400}
      y={600}
      moves={moveSequence}
    />

    <!-- Boss Fighter -->
    <Fighter
      side="boss"
      boss={currentBoss}
      x={1520}
      y={600}
      health={bossHealth}
    />
  </Canvas>

  <!-- HTML Overlays -->
  <div class="ui-overlay">
    <!-- Health Bars -->
    <HealthBar
      label="Player"
      health={playerHealth}
      maxHealth={100}
      position="top-left"
    />

    <HealthBar
      label={currentBoss.toUpperCase()}
      health={bossHealth}
      maxHealth={bossConfig[currentBoss].health}
      position="top-right"
    />

    <!-- Move Sequence Display -->
    <MoveSequence moves={moveSequence} />

    <!-- Win Display -->
    <WinDisplay amount={currentWin} />
  </div>
</div>

<style>
  .combat-arena {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .ui-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
</style>
```

### 4.3 Health Bar Component

```svelte
<!-- components/combat/HealthBar.svelte -->
<script lang="ts">
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';

  type Props = {
    label: string;
    health: number;
    maxHealth: number;
    position: 'top-left' | 'top-right';
  };

  let { label, health, maxHealth, position }: Props = $props();

  const percentage = $derived((health / maxHealth) * 100);
  const healthTween = tweened(100, {
    duration: 500,
    easing: cubicOut
  });

  $effect(() => {
    healthTween.set(percentage);
  });

  const barColor = $derived(() => {
    if (percentage < 30) return '#e74c3c';
    if (percentage < 60) return '#f39c12';
    return '#2ecc71';
  });
</script>

<div class="health-bar {position}">
  <div class="health-label">
    <span class="label-text">{label}</span>
    <span class="health-value">{Math.round(health)} / {maxHealth}</span>
  </div>

  <div class="health-bar-container">
    <div class="health-bar-bg">
      <div
        class="health-bar-fill"
        style:width="{$healthTween}%"
        style:background-color={barColor}
      >
        <span class="percentage">{Math.round($healthTween)}%</span>
      </div>
    </div>
  </div>

  {#if percentage < 30}
    <div class="warning-pulse"></div>
  {/if}
</div>

<style>
  .health-bar {
    position: absolute;
    width: 400px;
  }

  .health-bar.top-left {
    top: 40px;
    left: 40px;
  }

  .health-bar.top-right {
    top: 40px;
    right: 40px;
  }

  .health-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: bold;
    color: #fff;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
  }

  .health-bar-container {
    position: relative;
  }

  .health-bar-bg {
    width: 100%;
    height: 40px;
    background: rgba(0,0,0,0.6);
    border-radius: 20px;
    overflow: hidden;
    border: 2px solid rgba(255,255,255,0.3);
  }

  .health-bar-fill {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.3s;
    font-weight: bold;
    color: #fff;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
  }

  .warning-pulse {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 3px solid #e74c3c;
    border-radius: 20px;
    animation: pulse 1s ease-in-out infinite;
    pointer-events: none;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.05); }
  }
</style>
```

### 4.4 Move Sequence Display

```svelte
<!-- components/combat/MoveSequence.svelte -->
<script lang="ts">
  import { fly, scale } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  type Props = {
    moves: string[];
  };

  let { moves }: Props = $props();

  const moveClasses = {
    FWD: 'offensive',
    BWD: 'defensive',
    PUN: 'offensive',
    UPP: 'offensive',
    DUK: 'defensive',
    HRT: 'damage',
    DIZ: 'damage',
    KO: 'knockout'
  };
</script>

<div class="move-sequence">
  {#if moves.length === 0}
    <div class="empty-state">Awaiting combat...</div>
  {:else}
    {#each moves as move, i (i)}
      <div
        class="move-icon {moveClasses[move]}"
        in:fly={{ y: -50, duration: 300, delay: i * 100 }}
        in:scale={{ start: 0.5, duration: 300 }}
      >
        {move}
      </div>

      {#if i < moves.length - 1}
        <div class="arrow" in:scale={{ duration: 200, delay: (i * 100) + 150 }}>
          →
        </div>
      {/if}
    {/each}
  {/if}
</div>

<style>
  .move-sequence {
    position: absolute;
    bottom: 100px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 20px 40px;
    background: rgba(0,0,0,0.8);
    border-radius: 20px;
    border: 2px solid rgba(255,255,255,0.2);
    min-width: 400px;
    justify-content: center;
  }

  .empty-state {
    color: #888;
    font-style: italic;
  }

  .move-icon {
    padding: 15px 20px;
    border-radius: 10px;
    font-weight: bold;
    font-size: 18px;
    color: #fff;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  }

  .move-icon.offensive {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
  }

  .move-icon.defensive {
    background: linear-gradient(135deg, #3498db, #2980b9);
  }

  .move-icon.damage {
    background: linear-gradient(135deg, #e67e22, #d35400);
  }

  .move-icon.knockout {
    background: linear-gradient(135deg, #9b59b6, #8e44ad);
    font-size: 22px;
    animation: knockout-pulse 1s ease-in-out infinite;
  }

  @keyframes knockout-pulse {
    0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(155,89,182,0.5); }
    50% { transform: scale(1.1); box-shadow: 0 0 40px rgba(155,89,182,1); }
  }

  .arrow {
    font-size: 24px;
    color: #888;
  }
</style>
```

---

## 5. Animation Requirements

### 5.1 Character Animation System

Use **Spine animations** for characters:

```svelte
<!-- components/combat/Fighter.svelte -->
<script lang="ts">
  import { Spine } from '@stake-engine/pixi-svelte';
  import { getContext } from '$game/context';

  type Props = {
    side: 'player' | 'boss';
    boss?: string;
    x: number;
    y: number;
    moves?: string[];
    health?: number;
  };

  let { side, boss, x, y, moves = [], health = 100 }: Props = $props();

  const context = getContext();
  let currentAnimation = $state('idle');
  let spineRef = $state<any>(null);

  // Map moves to animations
  const animationMap = {
    FWD: 'move_forward',
    BWD: 'move_backward',
    PUN: 'punch',
    UPP: 'uppercut',
    DUK: 'duck',
    HRT: 'hit_react',
    DIZ: 'dizzy',
    KO: 'knockout'
  };

  // Subscribe to move animations
  context.eventEmitter.subscribeOnMount({
    moveAnimate: async (event) => {
      if (side === 'player') {
        const animation = animationMap[event.move];
        if (animation && spineRef) {
          await playAnimation(animation);
        }
      }
    },
    knockoutSequence: async () => {
      if (side === 'boss') {
        await playAnimation('knockout_received');
      } else {
        await playAnimation('victory_pose');
      }
    }
  });

  async function playAnimation(name: string): Promise<void> {
    return new Promise((resolve) => {
      if (!spineRef) {
        resolve();
        return;
      }

      currentAnimation = name;
      spineRef.state.setAnimation(0, name, false);

      // Return to idle after animation
      spineRef.state.addListener({
        complete: () => {
          currentAnimation = 'idle';
          spineRef.state.setAnimation(0, 'idle', true);
          resolve();
        }
      });
    });
  }

  // Health-based animations
  $effect(() => {
    if (health < 30 && currentAnimation === 'idle') {
      currentAnimation = 'low_health_idle';
      spineRef?.state.setAnimation(0, 'low_health_idle', true);
    }
  });
</script>

<Spine
  bind:this={spineRef}
  x={x}
  y={y}
  scale={side === 'player' ? 1 : -1}
  skeleton="/assets/spines/{side === 'player' ? 'fighter' : boss}/skeleton.json"
  atlas="/assets/spines/{side === 'player' ? 'fighter' : boss}/atlas.atlas"
  animation={currentAnimation}
  loop={currentAnimation === 'idle' || currentAnimation === 'low_health_idle'}
/>
```

### 5.2 Required Spine Animations

**Player Fighter:**
- `idle` - Standing ready (looping)
- `move_forward` - Step forward
- `move_backward` - Step back
- `punch` - Quick jab
- `uppercut` - Power uppercut
- `duck` - Dodge down
- `hit_react` - Take damage
- `dizzy` - Stunned state (looping)
- `knockout` - Deliver finishing blow
- `victory_pose` - Celebration
- `defeat` - Knocked out
- `low_health_idle` - Tired/wounded stance (looping)

**Boss Characters** (3 sets - Macron, Putin, Trump):
- `idle` - Boss-specific idle (looping)
- `attack` - Boss attacks player
- `defensive_stance` - Blocking
- `hit_react` - Take damage
- `stagger` - Low health wobble
- `knockout_received` - Knocked out
- `taunt` - Boss-specific taunt

### 5.3 Particle Effects

Use PixiJS particle emitters for:

```typescript
// lib/particleEffects.ts
import { Emitter } from '@pixi/particle-emitter';

export function createHitEffect(x: number, y: number) {
  return new Emitter(container, {
    lifetime: { min: 0.1, max: 0.5 },
    frequency: 0.001,
    emitterLifetime: 0.1,
    maxParticles: 20,
    addAtBack: false,
    pos: { x, y },
    behaviors: [
      {
        type: 'alpha',
        config: {
          alpha: { list: [{ value: 1, time: 0 }, { value: 0, time: 1 }] }
        }
      },
      {
        type: 'scale',
        config: {
          scale: { list: [{ value: 0.5, time: 0 }, { value: 0.1, time: 1 }] }
        }
      },
      {
        type: 'color',
        config: {
          color: { list: [{ value: 'ffff00', time: 0 }, { value: 'ff0000', time: 1 }] }
        }
      },
      {
        type: 'moveSpeed',
        config: { speed: { list: [{ value: 200, time: 0 }, { value: 50, time: 1 }] } }
      },
      {
        type: 'rotationStatic',
        config: { min: 0, max: 360 }
      },
      {
        type: 'spawnShape',
        config: {
          type: 'burst',
          data: { x: 0, y: 0, radius: 10 }
        }
      }
    ]
  });
}

export function createKnockoutEffect(x: number, y: number) {
  // More intense particle burst for knockouts
  // ... similar configuration with more particles, longer lifetime
}

export function createComboFlash(x: number, y: number, width: number, height: number) {
  // Screen flash effect for combo detection
  // ... use PIXI.Graphics with alpha tween
}
```

### 5.4 UI Animations

Use GSAP for smooth UI animations:

```typescript
// components/combat/WinDisplay.svelte
import gsap from 'gsap';

async function animateWinCounter(from: number, to: number): Promise<void> {
  return new Promise((resolve) => {
    const counter = { value: from };

    gsap.to(counter, {
      value: to,
      duration: 1.5,
      ease: 'power2.out',
      onUpdate: () => {
        winAmount = counter.value;
      },
      onComplete: resolve
    });
  });
}

async function celebrationAnimation(tier: string): Promise<void> {
  const timeline = gsap.timeline();

  if (tier === 'legendary') {
    // Scale pulse
    timeline.to('.win-display', {
      scale: 1.5,
      duration: 0.3,
      ease: 'back.out'
    });

    // Rotate
    timeline.to('.win-display', {
      rotation: 360,
      duration: 1,
      ease: 'power2.out'
    }, '-=0.3');

    // Particle burst
    // ...

    // Return to normal
    timeline.to('.win-display', {
      scale: 1,
      duration: 0.5,
      ease: 'elastic.out'
    });
  }
  // ... similar for other tiers

  return timeline.play();
}
```

---

## 6. Audio System

### 6.1 Audio Manager

```typescript
// lib/audioManager.ts
import { Howl, Howler } from 'howler';

class AudioManager {
  private sounds: Map<string, Howl> = new Map();
  private music: Map<string, Howl> = new Map();
  private soundVolume = 0.7;
  private musicVolume = 0.5;
  private muted = false;

  constructor() {
    this.loadAudio();
  }

  private loadAudio() {
    // Load SFX
    this.sounds.set('punch', new Howl({ src: ['/assets/sounds/punch.mp3'], volume: 0.8 }));
    this.sounds.set('uppercut', new Howl({ src: ['/assets/sounds/uppercut.mp3'], volume: 0.9 }));
    this.sounds.set('duck', new Howl({ src: ['/assets/sounds/duck.mp3'], volume: 0.6 }));
    this.sounds.set('hit', new Howl({ src: ['/assets/sounds/hit.mp3'], volume: 0.7 }));
    this.sounds.set('knockout', new Howl({ src: ['/assets/sounds/knockout.mp3'], volume: 1.0 }));
    this.sounds.set('combo', new Howl({ src: ['/assets/sounds/combo.mp3'], volume: 0.8 }));
    this.sounds.set('win_small', new Howl({ src: ['/assets/sounds/win_small.mp3'] }));
    this.sounds.set('win_medium', new Howl({ src: ['/assets/sounds/win_medium.mp3'] }));
    this.sounds.set('win_big', new Howl({ src: ['/assets/sounds/win_big.mp3'] }));
    this.sounds.set('win_legendary', new Howl({ src: ['/assets/sounds/win_legendary.mp3'] }));

    // Load Music
    this.music.set('macron', new Howl({
      src: ['/assets/music/macron_theme.mp3'],
      loop: true,
      volume: 0.5
    }));
    this.music.set('putin', new Howl({
      src: ['/assets/music/putin_theme.mp3'],
      loop: true,
      volume: 0.5
    }));
    this.music.set('trump', new Howl({
      src: ['/assets/music/trump_theme.mp3'],
      loop: true,
      volume: 0.5
    }));
  }

  playSound(name: string) {
    if (this.muted) return;
    const sound = this.sounds.get(name);
    sound?.play();
  }

  playMusic(boss: string) {
    // Stop all music
    this.music.forEach(m => m.stop());

    // Play boss theme
    const music = this.music.get(boss);
    if (music && !this.muted) {
      music.play();
    }
  }

  stopMusic() {
    this.music.forEach(m => m.stop());
  }

  setSoundVolume(volume: number) {
    this.soundVolume = volume;
    this.sounds.forEach(s => s.volume(volume));
  }

  setMusicVolume(volume: number) {
    this.musicVolume = volume;
    this.music.forEach(m => m.volume(volume));
  }

  toggleMute() {
    this.muted = !this.muted;
    Howler.mute(this.muted);
  }

  isMuted(): boolean {
    return this.muted;
  }
}

export const audioManager = new AudioManager();
```

### 6.2 Audio Integration with Events

```typescript
// game/bookEventHandlerMap.ts additions
import { audioManager } from '$lib/audioManager';

export const bookEventHandlerMap: BookEventHandlerMap = {
  // ... other handlers

  moveGenerated: async (bookEvent) => {
    // Play move sound
    const moveSound = {
      PUN: 'punch',
      UPP: 'uppercut',
      DUK: 'duck',
      HRT: 'hit',
      KO: 'knockout'
    };

    audioManager.playSound(moveSound[bookEvent.move] || 'punch');

    // ... rest of handler
  },

  comboDetected: async (bookEvent) => {
    audioManager.playSound('combo');
    // ... rest of handler
  },

  finalWin: async (bookEvent) => {
    const betAmount = getCurrentBet();
    const multiplier = bookEvent.amount / betAmount;

    let soundTier: string;
    if (multiplier >= 1000) soundTier = 'win_legendary';
    else if (multiplier >= 100) soundTier = 'win_big';
    else if (multiplier >= 10) soundTier = 'win_medium';
    else soundTier = 'win_small';

    audioManager.playSound(soundTier);

    // ... rest of handler
  }
};
```

---

## 7. RGS Integration

### 7.1 Book Event Processing

The core of RGS integration is **sequential event processing**:

```typescript
// game/playBookEvents.ts
import { sequence } from '@stake-engine/utils';
import { bookEventHandlerMap } from './bookEventHandlerMap';

export async function playBookEvents(bookEvents: BookEvent[]): Promise<void> {
  // Process events one by one
  await sequence(
    bookEvents.map(bookEvent =>
      () => playBookEvent(bookEvent, { bookEvents })
    )
  );
}

async function playBookEvent(
  bookEvent: BookEvent,
  context: { bookEvents: BookEvent[] }
): Promise<void> {
  const handler = bookEventHandlerMap[bookEvent.type];

  if (!handler) {
    console.warn(`No handler for event type: ${bookEvent.type}`);
    return;
  }

  // Execute handler (may be async)
  await handler(bookEvent, context);
}

// Helper: Run promises sequentially
async function sequence<T>(promises: Array<() => Promise<T>>): Promise<T[]> {
  const results: T[] = [];

  for (const promise of promises) {
    results.push(await promise());
  }

  return results;
}
```

### 7.2 Complete Game Flow

```typescript
// game/gameFlow.ts
import { rgsClient } from './rgsClient';
import { playBookEvents } from './playBookEvents';
import { eventEmitter } from './eventEmitter';

export async function playRound(boss: string, betAmount: number): Promise<void> {
  try {
    // 1. Call /wallet/play
    eventEmitter.broadcast({ type: 'roundStarting' });

    const playResponse = await rgsClient.play(boss, betAmount);

    // Update balance
    eventEmitter.broadcast({
      type: 'balanceUpdate',
      balance: playResponse.balance.amount / 1000000
    });

    // 2. Process book events
    await playBookEvents(playResponse.round.events);

    // 3. Call /wallet/end-round
    const endResponse = await rgsClient.endRound();

    // Update balance after payout
    eventEmitter.broadcast({
      type: 'balanceUpdate',
      balance: endResponse.balance.amount / 1000000
    });

    // 4. Round complete
    eventEmitter.broadcast({ type: 'roundComplete' });

  } catch (error) {
    if (error instanceof RGSError) {
      handleRGSError(error);
    } else {
      console.error('Unexpected error:', error);
      eventEmitter.broadcast({
        type: 'errorOccurred',
        message: 'An unexpected error occurred. Please try again.'
      });
    }
  }
}

function handleRGSError(error: RGSError) {
  const errorMessages = {
    ERR_IPB: 'Insufficient balance. Please add funds.',
    ERR_IS: 'Your session has expired. Please refresh the page.',
    ERR_ATE: 'Authentication failed. Please log in again.',
    ERR_GLE: 'You have reached your gambling limit.',
    ERR_MAINTENANCE: 'The game is currently under maintenance. Please try again later.',
  };

  const message = errorMessages[error.code] || `Error: ${error.message}`;

  eventEmitter.broadcast({
    type: 'errorOccurred',
    code: error.code,
    message
  });
}
```

### 7.3 Session Recovery

Handle disconnections gracefully:

```typescript
// game/sessionRecovery.ts
export async function recoverSession(): Promise<void> {
  try {
    const authResponse = await rgsClient.authenticate();

    // Check for active round
    if (authResponse.round) {
      // Resume incomplete round
      eventEmitter.broadcast({
        type: 'sessionRecovered',
        message: 'Resuming your previous game...'
      });

      // Process remaining events
      await playBookEvents(authResponse.round.events);

      // Complete round
      await rgsClient.endRound();
    }

    // Update balance
    eventEmitter.broadcast({
      type: 'balanceUpdate',
      balance: authResponse.balance.amount / 1000000
    });

  } catch (error) {
    console.error('Session recovery failed:', error);
    eventEmitter.broadcast({
      type: 'sessionRecoveryFailed',
      message: 'Unable to recover your session. Please refresh the page.'
    });
  }
}
```

---

## 8. Event Processing

### 8.1 Event Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. User clicks "FIGHT" button                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. XState machine transitions to 'bet' state            │
│    - Validates balance                                   │
│    - Disables UI controls                               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Call RGS /wallet/play endpoint                       │
│    - Debit balance                                       │
│    - Receive book with events array                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Process book.events sequentially                     │
│    ┌────────────────────────────────────────────────┐  │
│    │ For each bookEvent:                            │  │
│    │ a. Find handler in bookEventHandlerMap        │  │
│    │ b. Execute handler (may be async)             │  │
│    │ c. Handler broadcasts emitterEvents           │  │
│    │ d. Components receive and react to events     │  │
│    │ e. Animations play                            │  │
│    │ f. Wait for completion before next event      │  │
│    └────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. All events complete                                   │
│    - Display final win                                   │
│    - Play celebration animation                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Call RGS /wallet/end-round endpoint                  │
│    - Credit winnings                                     │
│    - Update balance                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 7. XState machine transitions to 'idle'                 │
│    - Re-enable UI controls                              │
│    - Ready for next round                               │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Example Book Event Sequence

```json
{
  "id": 12345,
  "payoutMultiplier": 3504,
  "events": [
    {
      "index": 0,
      "type": "reveal",
      "boss_name": "trump",
      "boss_health": 100,
      "player_health": 100,
      "boss_max_health": 100
    },
    {
      "index": 1,
      "type": "moveGenerated",
      "move": "PUN",
      "sequence_index": 0,
      "move_class": "offensive"
    },
    {
      "index": 2,
      "type": "healthUpdate",
      "player_health": 100,
      "boss_health": 90,
      "damage_to_boss": 10
    },
    {
      "index": 3,
      "type": "moveGenerated",
      "move": "UPP",
      "sequence_index": 1,
      "move_class": "offensive"
    },
    {
      "index": 4,
      "type": "healthUpdate",
      "player_health": 100,
      "boss_health": 75,
      "damage_to_boss": 15
    },
    {
      "index": 5,
      "type": "comboDetected",
      "sequence": "PUN-UPP",
      "length": 2,
      "base_multiplier": 0.0954,
      "final_multiplier": 0.0876
    },
    {
      "index": 6,
      "type": "moveGenerated",
      "move": "KO",
      "sequence_index": 2,
      "move_class": "knockout"
    },
    {
      "index": 7,
      "type": "healthUpdate",
      "player_health": 100,
      "boss_health": 0,
      "damage_to_boss": 75
    },
    {
      "index": 8,
      "type": "comboDetected",
      "sequence": "PUN-UPP-KO",
      "length": 3,
      "base_multiplier": 35.0429,
      "final_multiplier": 32.16
    },
    {
      "index": 9,
      "type": "knockout",
      "knockout_bonus": 16.08
    },
    {
      "index": 10,
      "type": "finalWin",
      "amount": 48.24,
      "best_sequence": "PUN-UPP-KO"
    }
  ],
  "criteria": "all_spins",
  "baseGameWins": 48.24,
  "freeGameWins": 0.0
}
```

---

## 9. Responsive Design

### 9.1 Layout System

Use Stake Engine's layout utilities:

```typescript
// game/context.ts additions
import { createLayout } from '@stake-engine/utils-layout';

const { stateLayout, stateLayoutDerived } = createLayout();

// Available layout properties:
// - stateLayout.canvasWidth
// - stateLayout.canvasHeight
// - stateLayout.device ('mobile' | 'desktop')
// - stateLayout.orientation ('portrait' | 'landscape')
// - stateLayoutDerived.isMobile()
// - stateLayoutDerived.isPortrait()
```

### 9.2 Responsive Component Example

```svelte
<!-- components/ResponsiveGame.svelte -->
<script lang="ts">
  import { getContext } from '$game/context';

  const context = getContext();

  // Reactive layout values
  const canvasWidth = $derived(context.stateLayout.canvasWidth);
  const canvasHeight = $derived(context.stateLayout.canvasHeight);
  const isMobile = $derived(context.stateLayoutDerived.isMobile());
  const isPortrait = $derived(context.stateLayoutDerived.isPortrait());

  // Adjust UI scale based on device
  const uiScale = $derived(isMobile ? 0.7 : 1.0);

  // Position elements responsively
  const healthBarWidth = $derived(isMobile ? 200 : 400);
  const moveSequenceBottom = $derived(isPortrait ? 150 : 100);
</script>

<div class="game" class:mobile={isMobile} class:portrait={isPortrait}>
  <Canvas width={canvasWidth} height={canvasHeight}>
    <!-- Scaled UI -->
    <Container scale={uiScale}>
      <!-- Game content -->
    </Container>
  </Canvas>

  <!-- Responsive HTML overlay -->
  <div class="ui-overlay" style:--ui-scale={uiScale}>
    <!-- ... -->
  </div>
</div>

<style>
  .game {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .game.mobile {
    /* Mobile-specific styles */
  }

  .game.portrait {
    /* Portrait-specific styles */
  }

  .ui-overlay {
    transform: scale(var(--ui-scale));
    transform-origin: top left;
  }
</style>
```

### 9.3 Breakpoints

```css
/* global.css */
:root {
  /* Desktop (default) */
  --health-bar-width: 400px;
  --move-icon-size: 60px;
  --font-size-large: 24px;
  --padding-large: 40px;
}

@media (max-width: 768px) {
  /* Tablet */
  :root {
    --health-bar-width: 300px;
    --move-icon-size: 50px;
    --font-size-large: 20px;
    --padding-large: 30px;
  }
}

@media (max-width: 480px) {
  /* Mobile */
  :root {
    --health-bar-width: 200px;
    --move-icon-size: 40px;
    --font-size-large: 16px;
    --padding-large: 20px;
  }
}
```

---

## 10. Localization

### 10.1 Lingui Setup

```bash
# Install Lingui
pnpm add @lingui/core @lingui/detect-locale
pnpm add -D @lingui/cli @lingui/macro
```

```javascript
// lingui.config.js
module.exports = {
  locales: ['en', 'es', 'fr', 'de', 'ja', 'ko', 'zh', 'pt', 'ru', 'tr', 'ar', 'hi', 'id', 'pl', 'fi', 'vi'],
  sourceLocale: 'en',
  catalogs: [
    {
      path: 'src/locales/{locale}/messages',
      include: ['src']
    }
  ],
  format: 'po'
};
```

### 10.2 Translation Implementation

```typescript
// lib/i18n.ts
import { i18n } from '@lingui/core';
import { detectLocale } from '@lingui/detect-locale';
import { getParam } from './utils';

export async function setupI18n() {
  // Get language from URL or detect
  const locale = getParam('lang') || detectLocale({
    fallback: 'en'
  });

  // Load catalog
  const { messages } = await import(`../locales/${locale}/messages.js`);
  i18n.load(locale, messages);
  i18n.activate(locale);

  return i18n;
}

export { i18n };
```

```svelte
<!-- Usage in components -->
<script>
  import { Trans, t } from '@lingui/macro';
  import { i18n } from '$lib/i18n';
</script>

<h1><Trans>Choose Your Opponent</Trans></h1>
<p>{t`Select a boss to fight`}</p>

<!-- Dynamic translations -->
<span>{i18n._(t`Current Balance: ${balance}`)}</span>
```

### 10.3 Translation Files

```po
# locales/en/messages.po
msgid "Choose Your Opponent"
msgstr "Choose Your Opponent"

msgid "Current Balance: {balance}"
msgstr "Current Balance: {balance}"

msgid "Fight!"
msgstr "Fight!"

msgid "Knockout!"
msgstr "Knockout!"

# locales/es/messages.po
msgid "Choose Your Opponent"
msgstr "Elige a tu oponente"

msgid "Current Balance: {balance}"
msgstr "Saldo actual: {balance}"

msgid "Fight!"
msgstr "¡Pelea!"

msgid "Knockout!"
msgstr "¡Nocaut!"
```

### 10.4 Number/Currency Formatting

```typescript
// lib/formatting.ts
export function formatCurrency(amount: number, currency: string, locale: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}

export function formatNumber(value: number, locale: string): string {
  return new Intl.NumberFormat(locale, {
    maximumFractionDigits: 2
  }).format(value);
}

// Usage:
// formatCurrency(123.45, 'USD', 'en-US') => "$123.45"
// formatCurrency(123.45, 'EUR', 'de-DE') => "123,45 €"
// formatCurrency(123.45, 'JPY', 'ja-JP') => "¥123"
```

---

## 11. Performance Optimization

### 11.1 Asset Loading

```typescript
// lib/assetLoader.ts
import { Assets } from '@pixi/assets';

export async function preloadAssets(onProgress?: (progress: number) => void): Promise<void> {
  // Add assets to loader
  Assets.addBundle('bosses', {
    macron_portrait: '/assets/bosses/macron.png',
    putin_portrait: '/assets/bosses/putin.png',
    trump_portrait: '/assets/bosses/trump.png',
    macron_spine: '/assets/spines/macron/skeleton.json',
    putin_spine: '/assets/spines/putin/skeleton.json',
    trump_spine: '/assets/spines/trump/skeleton.json',
  });

  Assets.addBundle('ui', {
    health_bar_bg: '/assets/ui/health_bar_bg.png',
    move_icons: '/assets/ui/move_icons.png',
    // ... more UI assets
  });

  Assets.addBundle('backgrounds', {
    macron_ring: '/assets/backgrounds/macron_ring.png',
    putin_ring: '/assets/backgrounds/putin_ring.png',
    trump_ring: '/assets/backgrounds/trump_ring.png',
  });

  // Load bundles with progress
  const bundles = ['bosses', 'ui', 'backgrounds'];
  let loaded = 0;

  for (const bundle of bundles) {
    await Assets.loadBundle(bundle);
    loaded++;
    onProgress?.(loaded / bundles.length);
  }
}
```

### 11.2 Sprite Batching

```typescript
// Ensure related sprites use same texture atlas
// Group sprites in ParticleContainer for better performance
import { ParticleContainer } from '@pixi/particle-container';

const moveIcons = new ParticleContainer(100, {
  scale: true,
  position: true,
  rotation: true,
  uvs: true,
  alpha: true
});

// Add sprites to particle container
// Much faster rendering than individual sprites
```

### 11.3 Code Splitting

```typescript
// Dynamic imports for heavy features
const SpineAnimation = lazy(() => import('./components/SpineAnimation.svelte'));

// Lazy load boss-specific code
async function loadBossModule(boss: string) {
  const module = await import(`./bosses/${boss}.ts`);
  return module.default;
}
```

### 11.4 Memory Management

```typescript
// Destroy unused resources
function cleanupBoss(boss: string) {
  // Remove Spine animations
  spineInstances[boss]?.destroy();
  delete spineInstances[boss];

  // Unload textures
  Assets.unload(`/assets/spines/${boss}/skeleton.json`);
  Assets.unload(`/assets/backgrounds/${boss}_ring.png`);

  // Clear event listeners
  eventEmitter.removeListener(`boss_${boss}_*`);
}

// Call cleanup when switching bosses
onBossChange((newBoss) => {
  const oldBoss = currentBoss;
  if (oldBoss !== newBoss) {
    cleanupBoss(oldBoss);
  }
});
```

---

## 12. Testing Strategy

### 12.1 Storybook Stories

```typescript
// stories/ModeBaseBook.stories.svelte
import { Story } from '@storybook/addon-svelte-csf';
import Game from '../components/Game.svelte';
import { sampleBooks } from './data/base_books';

<Story name="Base Game - Random Book">
  <Game book={sampleBooks[Math.floor(Math.random() * sampleBooks.length)]} />
</Story>

<Story name="Base Game - Knockout Sequence">
  <Game book={knockoutBook} />
</Story>

<Story name="Base Game - Legendary Win">
  <Game book={legendaryWinBook} />
</Story>
```

```typescript
// stories/data/base_books.ts
export const sampleBooks: Book[] = [
  {
    id: 1,
    payoutMultiplier: 3504,
    events: [
      { index: 0, type: 'reveal', ... },
      { index: 1, type: 'moveGenerated', move: 'PUN', ... },
      // ...
    ]
  },
  // ... more sample books
];

export const knockoutBook: Book = {
  // Specific book with knockout sequence
};

export const legendaryWinBook: Book = {
  // Book with 2336x win
};
```

### 12.2 Unit Tests

```typescript
// tests/combos.test.ts
import { describe, it, expect } from 'vitest';
import { evaluateSequence } from '../lib/combos';

describe('Combo Evaluation', () => {
  it('should detect basic 2-move combo', () => {
    const result = evaluateSequence(['FWD', 'PUN']);
    expect(result).toEqual({
      sequence: 'FWD-PUN',
      length: 2,
      multiplier: 0.053
    });
  });

  it('should select best combo from sequence', () => {
    const result = evaluateSequence(['FWD', 'PUN', 'UPP']);
    expect(result.sequence).toBe('FWD-PUN-UPP');
    expect(result.multiplier).toBe(0.3287);
  });

  it('should detect knockout sequences', () => {
    const result = evaluateSequence(['PUN', 'UPP', 'KO'], { bossHealth: 25 });
    expect(result.sequence).toBe('PUN-UPP-KO');
    expect(result.multiplier).toBe(35.0429);
  });
});
```

### 12.3 Integration Tests

```typescript
// tests/rgs.integration.test.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { RGSClient } from '../game/rgsClient';

describe('RGS Integration', () => {
  let client: RGSClient;

  beforeAll(async () => {
    client = new RGSClient();
    await client.authenticate();
  });

  it('should authenticate successfully', async () => {
    expect(client.getBalance()).toBeGreaterThan(0);
  });

  it('should place bet and receive book', async () => {
    const response = await client.play('macron', 1.0);

    expect(response.round).toBeDefined();
    expect(response.round.events).toBeInstanceOf(Array);
    expect(response.round.events.length).toBeGreaterThan(0);
  });

  it('should process book events', async () => {
    const response = await client.play('trump', 1.0);
    const events = response.round.events;

    // Verify event structure
    expect(events[0].type).toBe('reveal');
    expect(events[events.length - 1].type).toBe('finalWin');
  });

  it('should update balance after end-round', async () => {
    const initialBalance = client.getBalance();
    await client.play('putin', 1.0);
    const afterPlayBalance = client.getBalance();
    await client.endRound();
    const finalBalance = client.getBalance();

    expect(afterPlayBalance).toBe(initialBalance - 2.0); // Putin costs 2x
    expect(finalBalance).toBeGreaterThanOrEqual(afterPlayBalance); // Payout
  });
});
```

### 12.4 RTP Verification

```typescript
// tests/rtp.test.ts
import { describe, it, expect } from 'vitest';
import { RGSClient } from '../game/rgsClient';

describe('RTP Verification (Long Running)', () => {
  it('should achieve ~98% RTP for Macron over 10k spins', async () => {
    const client = new RGSClient();
    await client.authenticate();

    let totalBet = 0;
    let totalWin = 0;
    const spins = 10000;

    for (let i = 0; i < spins; i++) {
      const playResponse = await client.play('macron', 1.0);
      totalBet += 1.0;

      const win = playResponse.round.payoutMultiplier / 100;
      totalWin += win;

      await client.endRound();
    }

    const rtp = (totalWin / totalBet);

    // Allow 2% variance
    expect(rtp).toBeGreaterThan(0.96);
    expect(rtp).toBeLessThan(1.00);

    console.log(`Macron RTP over ${spins} spins: ${(rtp * 100).toFixed(2)}%`);
  }, 600000); // 10 minute timeout
});
```

---

## 13. Deployment Checklist

### 13.1 Build Process

```bash
# 1. Install dependencies
pnpm install

# 2. Run linter
pnpm lint

# 3. Run type check
pnpm typecheck

# 4. Run tests
pnpm test

# 5. Build for production
pnpm build

# 6. Preview production build
pnpm preview
```

### 13.2 Production Checklist

**Code Quality:**
- [ ] All TypeScript errors resolved
- [ ] ESLint passes with no warnings
- [ ] All tests passing
- [ ] RTP verified (10k+ spins per mode)
- [ ] No console errors or warnings

**Assets:**
- [ ] All images optimized (WebP format where possible)
- [ ] Spine animations compressed
- [ ] Audio files compressed (MP3 or OGG)
- [ ] Texture atlases generated
- [ ] Font files subset to required characters

**Performance:**
- [ ] Lighthouse score >90 on mobile
- [ ] First Contentful Paint <2s
- [ ] Time to Interactive <3s
- [ ] Bundle size <2MB (gzipped)
- [ ] No memory leaks (tested with Chrome DevTools)

**Functionality:**
- [ ] All boss modes tested
- [ ] Knockout sequences working
- [ ] Health bars accurate
- [ ] Win calculations correct
- [ ] Balance updates properly
- [ ] Session recovery works
- [ ] Error handling tested

**Responsive Design:**
- [ ] Desktop (1920x1080) tested
- [ ] Tablet (768x1024) tested
- [ ] Mobile portrait (375x667) tested
- [ ] Mobile landscape (667x375) tested
- [ ] Ultra-wide (2560x1080) tested

**Localization:**
- [ ] All 16 languages tested
- [ ] Currency formatting correct
- [ ] RTL languages (Arabic) working
- [ ] Date/time formatting locale-aware

**Compliance:**
- [ ] Responsible gaming features implemented
- [ ] Reality checks working
- [ ] Loss limits enforced
- [ ] Age verification flow (if required)
- [ ] Terms & conditions linked
- [ ] Privacy policy linked

### 13.3 Upload to Stake Engine

```bash
# 1. Build production bundle
pnpm build

# 2. Create deployment package
cd build/
tar -czf beat-the-boss-v1.0.0.tar.gz *

# 3. Upload via ACP (Admin Control Panel)
# - Navigate to Games > Upload New Version
# - Select beat-the-boss-v1.0.0.tar.gz
# - Verify SHA-256 hash
# - Deploy to staging

# 4. Test on staging
# - URL: https://staging.cdn.stake-engine.com/beat_the_boss/1.0.0/

# 5. Deploy to production (if tests pass)
# - Promote staging build to production
# - URL: https://cdn.stake-engine.com/beat_the_boss/1.0.0/
```

### 13.4 Post-Deployment Monitoring

**Metrics to Monitor:**
- Player session duration
- Bet frequency per mode
- Win distribution (small/medium/big/legendary)
- Knockout frequency
- Error rates
- RTP deviation (should stay within ±0.5% of 98%)
- Drop-off points
- Most popular boss (Macron/Putin/Trump)
- Average multiplier per mode

**Alerts to Set:**
- RTP deviation >1% from target
- Error rate >1%
- Session timeout rate >5%
- Server response time >500ms
- Client crash rate >0.1%

---

## 14. Compliance Requirements

### 14.1 Responsible Gaming

```svelte
<!-- components/ResponsibleGaming.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';

  let playTime = $state(0);
  let sessionStartTime = $state(Date.now());
  let realityCheckInterval = 30; // minutes

  onMount(() => {
    // Track play time
    const timer = setInterval(() => {
      playTime = Math.floor((Date.now() - sessionStartTime) / 60000);

      // Reality check every 30 minutes
      if (playTime % realityCheckInterval === 0 && playTime > 0) {
        showRealityCheck();
      }
    }, 60000);

    return () => clearInterval(timer);
  });

  function showRealityCheck() {
    // Pause game
    eventEmitter.broadcast({ type: 'gamePaused' });

    // Show modal with session stats
    showModal({
      title: 'Reality Check',
      content: `You've been playing for ${playTime} minutes.
                Total wagered: ${totalWagered}
                Net result: ${totalWagered - totalWon}`,
      actions: [
        { label: 'Continue Playing', onClick: resumeGame },
        { label: 'Take a Break', onClick: exitGame }
      ]
    });
  }

  function resumeGame() {
    sessionStartTime = Date.now();
    playTime = 0;
    eventEmitter.broadcast({ type: 'gameResumed' });
  }

  function exitGame() {
    window.location.href = '/exit';
  }
</script>
```

### 14.2 Loss Limits

```typescript
// lib/lossLimits.ts
export class LossLimitManager {
  private dailyLimit: number = 0;
  private weeklyLimit: number = 0;
  private monthlyLimit: number = 0;

  private dailyLoss: number = 0;
  private weeklyLoss: number = 0;
  private monthlyLoss: number = 0;

  constructor(limits: { daily?: number; weekly?: number; monthly?: number }) {
    this.dailyLimit = limits.daily || Infinity;
    this.weeklyLimit = limits.weekly || Infinity;
    this.monthlyLimit = limits.monthly || Infinity;
  }

  canPlaceBet(amount: number): boolean {
    return (
      this.dailyLoss + amount <= this.dailyLimit &&
      this.weeklyLoss + amount <= this.weeklyLimit &&
      this.monthlyLoss + amount <= this.monthlyLimit
    );
  }

  recordLoss(amount: number) {
    this.dailyLoss += amount;
    this.weeklyLoss += amount;
    this.monthlyLoss += amount;
  }

  recordWin(amount: number) {
    this.dailyLoss = Math.max(0, this.dailyLoss - amount);
    this.weeklyLoss = Math.max(0, this.weeklyLoss - amount);
    this.monthlyLoss = Math.max(0, this.monthlyLoss - amount);
  }

  getLimitsStatus() {
    return {
      daily: {
        used: this.dailyLoss,
        limit: this.dailyLimit,
        remaining: this.dailyLimit - this.dailyLoss
      },
      weekly: {
        used: this.weeklyLoss,
        limit: this.weeklyLimit,
        remaining: this.weeklyLimit - this.weeklyLoss
      },
      monthly: {
        used: this.monthlyLoss,
        limit: this.monthlyLimit,
        remaining: this.monthlyLimit - this.monthlyLoss
      }
    };
  }
}
```

### 14.3 Age Verification

```svelte
<!-- components/AgeGate.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import Cookies from 'js-cookie';

  let verified = $state(false);
  let birthDate = $state('');

  onMount(() => {
    // Check if already verified
    const ageVerified = Cookies.get('age_verified');
    if (ageVerified === 'true') {
      verified = true;
    }
  });

  function verifyAge() {
    const birth = new Date(birthDate);
    const age = Math.floor((Date.now() - birth.getTime()) / (365.25 * 24 * 60 * 60 * 1000));

    if (age >= 18) {
      verified = true;
      Cookies.set('age_verified', 'true', { expires: 365 });
    } else {
      alert('You must be 18 or older to play.');
      window.location.href = '/underage';
    }
  }
</script>

{#if !verified}
  <div class="age-gate">
    <h1>Age Verification Required</h1>
    <p>You must be 18 or older to access this game.</p>

    <label>
      Date of Birth:
      <input type="date" bind:value={birthDate} />
    </label>

    <button onclick={verifyAge}>Verify</button>
  </div>
{:else}
  <slot />
{/if}
```

### 14.4 Jurisdiction Restrictions

```typescript
// lib/jurisdictionCheck.ts
export async function checkJurisdiction(ip: string): Promise<JurisdictionStatus> {
  // Call geolocation API
  const response = await fetch(`https://api.ipgeolocation.io/ipgeo?apiKey=${API_KEY}&ip=${ip}`);
  const data = await response.json();

  const country = data.country_code2;

  // Check restricted territories
  const restrictedCountries = ['US', 'UK', 'FR', 'AU']; // Example
  const isRestricted = restrictedCountries.includes(country);

  if (isRestricted) {
    return {
      allowed: false,
      country,
      message: `This game is not available in ${data.country_name}.`
    };
  }

  // Check for social casino requirements
  const socialCasinoCountries = ['US'];
  const socialCasinoRequired = socialCasinoCountries.includes(country);

  return {
    allowed: true,
    country,
    socialCasino: socialCasinoRequired,
    settings: {
      disableTurbo: socialCasinoRequired,
      disableFullscreen: socialCasinoRequired,
      requireRealityChecks: true
    }
  };
}
```

---

## Conclusion

This production guide provides a **comprehensive blueprint** for building Beat the Boss as a professional casino game on the Stake Engine platform.

**Key Takeaways:**

1. **Architecture**: Svelte 5 + PixiJS with event-driven communication
2. **Event System**: Sequential book event processing with async handlers
3. **UI Components**: Responsive health bars, move sequences, boss selection
4. **Animations**: Spine characters, GSAP UI animations, PixiJS particles
5. **Audio**: Howler.js with SFX and boss-specific themes
6. **RGS Integration**: Proper API flow with session recovery
7. **Responsive**: Mobile and desktop support with adaptive layouts
8. **Localization**: 16 languages with Lingui
9. **Performance**: Asset optimization, code splitting, sprite batching
10. **Testing**: Storybook, unit tests, integration tests, RTP verification
11. **Compliance**: Responsible gaming, age verification, jurisdiction checks

**Development Timeline Estimate:**

- **Week 1-2**: Project setup, RGS integration, basic UI
- **Week 3-4**: Combat system, health bars, move sequences
- **Week 5-6**: Character animations (Spine), particle effects
- **Week 7-8**: Audio integration, win celebrations
- **Week 9-10**: Responsive design, localization
- **Week 11**: Testing, optimization, bug fixes
- **Week 12**: Compliance features, deployment prep

**Total**: **6-12 weeks** with 2-3 developers

This is a **production-ready game specification** that meets all Stake Engine requirements and industry standards for online casino games.