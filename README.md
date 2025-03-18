# Stack Game (pygame Recreation)

## Overview
**Stack!** is a simple yet engaging stacking game where players must place platforms on top of each other as accurately as possible. The game features sound effects, colorful gradients, and a scoring system that rewards precision.

## How to Play
1. Run the game using:
   ```sh
   python src/main.py
   ```
2. **Click** or press the **spacebar** to stop the moving block.
3. Stack blocks precisely to avoid reducing the platform size.
4. Continue stacking to reach the highest score!
5. The game ends when the block becomes too small to continue.

## Controls
- **Mouse Click** / **Spacebar** - Places the moving block

## Project Structure
```
.
├── src
│   ├── main.py                # entry point for the game
│   ├── constants.py           # constant values used throughout the game
│   ├── classes
│   │   ├── background.py      # background management
│   │   ├── gradient.py        # gradient handling
│   │   ├── platform.py        # platform representation
│   │   ├── tower.py           # tower management
│   │   ├── game.py            # game logic
│   └── utils
│       ├── utils.py           # general utility functions
│       ├── system_utils.py    # system-related utilities
├── assets
│   └── SFX
│       ├── normalStack        # sound effects for normal stacking
│       │   ├── stack1.wav
│       │   ├── stack2.wav
│       ├── perfectStack       # sound effects for perfect stacking
│       │   ├── perfect1.wav
│       │   ├── perfect2.wav
│       │   ├── ... (more sounds)
│       ├── expandPlatform     # sound effects for platform expansion
│       │   ├── expand1.wav
│       │   ├── expand2.wav
├── .gitignore                 # git ignore file
├── README.md                  # project documentation
```

## Installation
Make sure you have **Python 3** installed on your system. Then, install the required dependencies by running in your terminal:

```sh
pip install pygame numpy pywin32
```

## Contributing
Want to help improve Stack? You can:
- Report issues
- Suggest new features
- Improve game mechanics
- Optimize performance
- Add new features/game modes

## License
This project is open-source and licensed under the **MIT License**.

