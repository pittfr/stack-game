# Stack Game (Pygame Recreation)

## Overview
Stack Game is a simple yet engaging stacking game where players must place platforms on top of each other as accurately as possible. The game features sound effects, colorful gradients, and a scoring system that rewards precision.

## How to Play
1. Run the game using:
   ```sh
   python src/main.py
   ```
2. Press the **spacebar** or **mouse click** to stop the moving block.
3. Stack blocks precisely to avoid reducing the platform size.
4. Continue stacking to reach the highest score!
5. The game ends when the block becomes too small to continue.

## Controls
- **Spacebar** / **Mouse Click** - Places the moving block

## Project Structure
```
.
├── src                        # source code
│   ├── main.py                # entry point for the game
│   ├── constants.py           # constant values used throughout the game
│   ├── classes                # game-related classes
│   │   ├── background.py      # background management
│   │   ├── game.py            # game logic
│   │   ├── gradient.py        # gradient handling
│   │   ├── platform.py        # platform representation
│   │   ├── tower.py           # tower management
│   │   ├── ui                 # UI handling
│   │   │   ├── button.py      # button handling
│   │   │   ├── ui_manager.py  # UI management
│   ├── utils                  # utility functions
│   │   ├── utils.py           # general utilities
│   │   ├── system_utils.py    # system-related utilities
├── assets                     # game assets
│   ├── SFX                    # sound effects
│   │   ├── expandPlatform     # sounds for platform expansion
│   │   │   ├── expand1.wav
│   │   │   ├── expand2.wav
│   │   ├── normalStack        # sounds for normal stacking
│   │   │   ├── stack1.wav
│   │   │   ├── stack2.wav
│   │   ├── perfectStack       # sounds for perfect stacking
│   │   │   ├── perfect1.wav
│   │   │   ├── perfect2.wav
│   │   │   ├── ... (more sounds)
│   │   ├── pauseGame          # sounds for pausing the game
│   │   │   ├── pause1.wav
│   │   ├── buttonClick        # sounds for button clicks
│   │   │   ├── click1.wav
│   ├── fonts                  # font files
│   │   ├── Arial-Black.ttf
│   ├── images                 # image assets
│   │   ├── settingsIcon       # settings icons
│   │   │   ├── gear_solid.png
│   │   │   ├── gear_solid_hover.png
├── .gitignore                 # git ignore file
├── README.md                  # project documentation
```

## Installation
Make sure you have **Python 3** installed on your system. Then, install the required dependencies:

```sh
pip install pygame numpy pywin32
```

## Contributing
Want to help improve Stack Game? You can:
- Report issues
- Suggest new features
- Improve game mechanics
- Optimize performance

## License
This project is open-source under the **MIT License**.

