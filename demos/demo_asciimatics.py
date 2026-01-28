"""
Demo: asciimatics library
Run: poetry run python demos/demo_asciimatics.py

Tests:
- Emoji rendering and alignment
- Colors and effects
- Keyboard input
- Built-in animation capabilities
"""

import sys
import os

# Fix Windows encoding for Unicode/emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.system('chcp 65001 > nul 2>&1')  # Set console to UTF-8

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from asciimatics.event import KeyboardEvent
import time


class GameDemo(Effect):
    """Main game demo effect."""

    def __init__(self, screen, **kwargs):
        super().__init__(screen, **kwargs)
        # Play area: x=2, y=14, width=40, height=6
        self.player_x = 20
        self.player_y = 14 + 6 - 2  # Start on top of ground
        self.player_char = '🐇'
        self.test_emoji = ['🐇', '🌲', '🐦', '💎', '🥕', '🐰', '🦋', '🍄']

    def reset(self):
        pass

    def _update(self, frame_no):
        # Clear
        self._screen.clear_buffer(7, 0, 0)

        # === HEADER ===
        title = ' ASCIIMATICS DEMO '
        self._screen.print_at(
            title.center(self._screen.width),
            0, 0,
            colour=Screen.COLOUR_WHITE,
            bg=Screen.COLOUR_BLUE,
            attr=Screen.A_BOLD
        )

        # === EMOJI ALIGNMENT TEST ===
        self._screen.print_at('Emoji Alignment Test:', 2, 2, colour=Screen.COLOUR_YELLOW)

        # Draw box with emoji
        # Box is 38 cols: ╔ + 36×═ + ╗
        box_y = 3
        self._screen.print_at('╔════════════════════════════════════╗', 2, box_y)

        # Emoji: 8×2=16 display cols, 7 spaces=7, total=23. Plus "║ "=2, need 38-2-23-1=12 padding
        emoji_content = ' '.join(self.test_emoji)
        line = '║ ' + emoji_content + ' ' * 12 + '║'
        self._screen.print_at(line, 2, box_y + 1)

        # Text line: needs to be 38 cols total
        self._screen.print_at('║ Does this border align? ------>    ║', 2, box_y + 2)
        self._screen.print_at('╚════════════════════════════════════╝', 2, box_y + 3)

        # === COLOR TEST ===
        self._screen.print_at('Color Test:', 2, 8, colour=Screen.COLOUR_YELLOW)

        colors = [
            (Screen.COLOUR_RED, 'Red'),
            (Screen.COLOUR_GREEN, 'Green'),
            (Screen.COLOUR_BLUE, 'Blue'),
            (Screen.COLOUR_CYAN, 'Cyan'),
            (Screen.COLOUR_MAGENTA, 'Magenta'),
            (Screen.COLOUR_YELLOW, 'Yellow'),
        ]

        x = 2
        for color, name in colors:
            self._screen.print_at(name + ' ', x, 9, colour=color)
            x += len(name) + 1

        # Background colors
        x = 2
        for color, _ in colors:
            self._screen.print_at('  ', x, 10, bg=color)
            x += 2
        self._screen.print_at(' Background colors', x, 10)

        # === MOVEMENT AREA ===
        self._screen.print_at('Movement Test (WASD or Arrows, Q to quit, Space to change char):', 2, 12, colour=Screen.COLOUR_YELLOW)

        # Draw area
        area_x, area_y = 2, 14
        area_w, area_h = 40, 6

        # Top border: ▀ half-block (green on cyan) - bunny stays below
        self._screen.print_at(' ', area_x, area_y, bg=Screen.COLOUR_GREEN)
        self._screen.print_at('▀' * (area_w - 2), area_x + 1, area_y, colour=Screen.COLOUR_GREEN, bg=Screen.COLOUR_CYAN)
        self._screen.print_at(' ', area_x + area_w - 1, area_y, bg=Screen.COLOUR_GREEN)

        # Middle area (cyan sky with green edges)
        for row in range(area_h - 2):
            y = area_y + 1 + row
            self._screen.print_at(' ', area_x, y, bg=Screen.COLOUR_GREEN)
            self._screen.print_at(' ' * (area_w - 2), area_x + 1, y, bg=Screen.COLOUR_CYAN)
            self._screen.print_at(' ', area_x + area_w - 1, y, bg=Screen.COLOUR_GREEN)

        # Bottom border: solid green - bunny stands IN this
        self._screen.print_at(' ' * area_w, area_x, area_y + area_h - 1, bg=Screen.COLOUR_GREEN)

        # Draw player
        self._screen.print_at(
            self.player_char,
            self.player_x,
            self.player_y,
            bg=Screen.COLOUR_CYAN
        )

        # Instructions
        self._screen.print_at('Press Q to quit', 2, 21, colour=Screen.COLOUR_WHITE)

    @property
    def frame_update_count(self):
        return 1

    @property
    def stop_frame(self):
        return 0

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            key = event.key_code

            # Q to quit
            if key in (ord('q'), ord('Q')):
                raise StopIteration

            # Movement
            area_x, area_y = 2, 14
            area_w, area_h = 40, 6

            if key in (ord('w'), ord('W'), Screen.KEY_UP):
                self.player_y = max(area_y + 1, self.player_y - 1)  # Stay below top (gap)
            elif key in (ord('s'), ord('S'), Screen.KEY_DOWN):
                self.player_y = min(area_y + area_h - 2, self.player_y + 1)  # Stand ON TOP of ground
            elif key in (ord('a'), ord('A'), Screen.KEY_LEFT):
                self.player_x = max(area_x + 1, self.player_x - 1)
            elif key in (ord('d'), ord('D'), Screen.KEY_RIGHT):
                self.player_x = min(area_x + area_w - 3, self.player_x + 1)
            elif key == ord(' '):
                # Cycle character
                idx = self.test_emoji.index(self.player_char) if self.player_char in self.test_emoji else -1
                self.player_char = self.test_emoji[(idx + 1) % len(self.test_emoji)]

        return event


def demo(screen):
    effect = GameDemo(screen)
    screen.set_title('Asciimatics Demo')

    while True:
        effect._update(0)
        screen.refresh()

        event = screen.get_event()
        if event:
            try:
                effect.process_event(event)
            except StopIteration:
                return

        time.sleep(0.05)


def main():
    try:
        Screen.wrapper(demo, unicode_aware=True)
    except Exception as e:
        print(f"Error: {e}")
        print("\nAsciimatics may have issues with your console.")
        print("Try running in Windows Terminal or resize your console window.")
        print("Alternatively, test the blessed demo instead:")
        print("  poetry run python demos/demo_blessed.py")


if __name__ == '__main__':
    main()
