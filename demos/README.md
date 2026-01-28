# Library Demos

Test each library to see which works best with emoji in your terminal.

## Run the demos

```bash
# From the bunny-scroller directory:

# Test blessed
poetry run python demos/demo_blessed.py

# Test asciimatics
poetry run python demos/demo_asciimatics.py

# Test curses
poetry run python demos/demo_curses.py
```

## What to check

1. **Emoji alignment** - Does the box border on the right align properly?
2. **Colors** - Do you see different colors?
3. **Movement** - Can you move the character with WASD/arrows?
4. **No flickering** - Is the display smooth?
5. **Emoji switching** - Press SPACE to cycle through different emoji

## Controls

- `W` / `↑` - Move up
- `S` / `↓` - Move down
- `A` / `←` - Move left
- `D` / `→` - Move right
- `SPACE` - Change character
- `Q` - Quit

## Report back

Let me know:
- Which demo looked best?
- Did emoji borders align?
- Any glitches or issues?
