"""
Demo: curses library (with windows-curses on Windows)
Run: poetry run python demos/demo_curses.py

Tests:
- Emoji rendering and alignment
- Colors
- Keyboard input
- Raw curses experience
"""

import sys
import os
import locale

# Fix Windows encoding for Unicode/emoji support
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')  # Set console to UTF-8

# Set locale for curses Unicode support
locale.setlocale(locale.LC_ALL, '')

import curses
import time


def main(stdscr):
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(50)  # 50ms timeout for getch

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)
    curses.init_pair(6, curses.COLOR_YELLOW, -1)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Grass bg
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Sky bg
    curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_CYAN)  # Grass border on sky

    # Game state
    # Play area: x=2, y=13, width=40, height=6
    player_x = 20
    player_y = 13 + 6 - 2  # Start on top of ground
    player_char = '🐇'
    test_emoji = ['🐇', '🌲', '🐦', '💎', '🥕', '🐰', '🦋', '🍄']
    char_idx = 0

    running = True

    while running:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # === HEADER ===
        title = ' CURSES DEMO '
        try:
            stdscr.addstr(0, 0, title.center(width), curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass

        # === EMOJI ALIGNMENT TEST ===
        try:
            stdscr.addstr(2, 2, 'Emoji Alignment Test:', curses.color_pair(6))
        except curses.error:
            pass

        # Draw box - 38 cols: ╔ + 36×═ + ╗
        box_y = 3
        try:
            stdscr.addstr(box_y, 2, '╔════════════════════════════════════╗')

            # Emoji: 8×2=16 display cols, 7 spaces=7, total=23. Plus "║ "=2, need 38-2-23-1=12 padding
            emoji_content = ' '.join(test_emoji)
            line = '║ ' + emoji_content + ' ' * 12 + '║'
            stdscr.addstr(box_y + 1, 2, line)

            # Text line: needs to be 38 cols total
            stdscr.addstr(box_y + 2, 2, '║ Does this border align? ------>    ║')
            stdscr.addstr(box_y + 3, 2, '╚════════════════════════════════════╝')
        except curses.error:
            pass

        # === COLOR TEST ===
        try:
            stdscr.addstr(8, 2, 'Color Test:', curses.color_pair(6))

            colors = [
                (1, 'Red'),
                (2, 'Green'),
                (3, 'Blue'),
                (4, 'Cyan'),
                (5, 'Magenta'),
                (6, 'Yellow'),
            ]

            # Foreground colors
            stdscr.move(9, 2)
            for pair, name in colors:
                stdscr.addstr(name + ' ', curses.color_pair(pair))

            # Background colors
            x_pos = 2
            for pair, _ in colors:
                stdscr.addstr(10, x_pos, '  ', curses.color_pair(pair) | curses.A_REVERSE)
                x_pos += 2
            stdscr.addstr(10, x_pos, ' Background colors')
        except curses.error:
            pass

        # === MOVEMENT TEST ===
        try:
            stdscr.addstr(11, 2, 'Movement Test (WASD or Arrows, Q to quit, Space to change):', curses.color_pair(6))
        except curses.error:
            pass

        # Draw area
        area_x, area_y = 2, 13
        area_w, area_h = 40, 6

        try:
            # Top border: ▀ half-block (green on cyan) - bunny stays below
            stdscr.addstr(area_y, area_x, ' ', curses.color_pair(8))
            stdscr.addstr(area_y, area_x + 1, '▀' * (area_w - 2), curses.color_pair(10))
            stdscr.addstr(area_y, area_x + area_w - 1, ' ', curses.color_pair(8))

            # Middle rows
            for row in range(area_h - 2):
                y = area_y + 1 + row
                # Left edge
                stdscr.addstr(y, area_x, ' ', curses.color_pair(8))
                # Middle (sky)
                stdscr.addstr(y, area_x + 1, ' ' * (area_w - 2), curses.color_pair(9))
                # Right edge
                stdscr.addstr(y, area_x + area_w - 1, ' ', curses.color_pair(8))

            # Bottom border: solid green - bunny stands IN this
            stdscr.addstr(area_y + area_h - 1, area_x, ' ' * area_w, curses.color_pair(8))

            # Draw player
            stdscr.addstr(player_y, player_x, player_char, curses.color_pair(9))
        except curses.error:
            pass

        # Instructions
        try:
            stdscr.addstr(20, 2, 'Press Q to quit', curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()

        # Input
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key != -1:
            if key in (ord('q'), ord('Q')):
                running = False
            elif key in (ord('w'), ord('W'), curses.KEY_UP):
                player_y = max(area_y + 1, player_y - 1)  # Stay below top (gap)
            elif key in (ord('s'), ord('S'), curses.KEY_DOWN):
                player_y = min(area_y + area_h - 2, player_y + 1)  # Stand ON TOP of ground
            elif key in (ord('a'), ord('A'), curses.KEY_LEFT):
                player_x = max(area_x + 1, player_x - 1)
            elif key in (ord('d'), ord('D'), curses.KEY_RIGHT):
                player_x = min(area_x + area_w - 3, player_x + 1)
            elif key == ord(' '):
                char_idx = (char_idx + 1) % len(test_emoji)
                player_char = test_emoji[char_idx]


if __name__ == '__main__':
    curses.wrapper(main)
