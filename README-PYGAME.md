# STICKSTRIKE Pygame

A neon stick-figure fighting game built with Pygame.

## Features

- Movement, jumping, and light attacks
- CPU opponent with Easy, Normal, and Hard difficulty
- Multi-round matches
- Character colors, head shapes, aura, and headband customization
- Main menu, options, pause, restart, and rematch flows

## Run

```powershell
pip install -r requirements.txt
python main.py
```

## Controls

- `A` / `D` or arrow keys: move
- `W` or Up: jump
- `J`: light punch
- `K`: heavy punch
- `U`: light kick
- `I`: heavy kick
- `L` or Right Shift: guard
- `O`: ultimate attack when the gold meter is full
- `Esc`: pause

## Combos

- `J, J, K`: Rapid Break
- `U, U, I`: Cyclone Kick
- `J, U, K`: Neon Finish

Enter each sequence quickly before the combo window expires.

## Publish updates

```powershell
.\push_updates.ps1
```

The script commits the Pygame files and pushes them to `agent/pygame-game-updates`.
