"""
Tree zoom animation - cycles through small/med/large sizes.
Creates a "parallax" or "approaching/receding" effect.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from tree_frames
sys.path.insert(0, str(Path(__file__).parent.parent))

from blessed import Terminal
from tree_frames.w20_frames import FRAMES as FRAMES_SMALL
from tree_frames.w58_frames import FRAMES as FRAMES_MED
from tree_frames.w100_frames import FRAMES as FRAMES_LARGE


class Screen:
    """Double-buffered screen with dirty tracking."""

    def __init__(self, term):
        self.term = term
        self.width = term.width
        self.height = term.height - 1
        self.current = [[' '] * self.width for _ in range(self.height)]
        self.previous = [['X'] * self.width for _ in range(self.height)]  # Force initial draw

    def clear(self):
        """Clear current buffer."""
        for row in self.current:
            for i in range(len(row)):
                row[i] = ' '

    def draw_sprite(self, lines, x, y):
        """Draw sprite to current buffer (non-space chars only)."""
        for i, line in enumerate(lines):
            row = y + i
            if 0 <= row < self.height:
                for j, ch in enumerate(line):
                    col = x + j
                    if 0 <= col < self.width and ch != ' ':
                        self.current[row][col] = ch

    def render(self, out):
        """Output only changed characters."""
        for row in range(self.height):
            for col in range(self.width):
                if self.current[row][col] != self.previous[row][col]:
                    out(self.term.move_xy(col, row) + self.current[row][col])
                    self.previous[row][col] = self.current[row][col]


def get_frame_sets():
    """
    Returns list of (frames, label) tuples in zoom order.
    Pattern: small → med → large → med → repeat
    """
    return [
        (FRAMES_SMALL, "far"),
        (FRAMES_MED, "medium"),
        (FRAMES_LARGE, "close"),
        (FRAMES_MED, "medium"),
    ]


def main():
    term = Terminal()
    out = sys.stdout.write
    flush = sys.stdout.flush

    # Get frame sets in zoom order
    frame_sets = get_frame_sets()

    # Track current position in the zoom cycle
    set_idx = 0  # Which size we're on (0=small, 1=med, 2=large, 3=med)
    frame_idx = 0  # Which frame within the current size

    current_frames, current_label = frame_sets[set_idx]

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        out(term.home + term.clear)
        flush()

        screen = Screen(term)

        while True:
            screen.clear()

            # Get current frame
            frame_lines = current_frames[frame_idx].split('\n')

            # Center horizontally, align to bottom
            frame_width = max(len(line) for line in frame_lines)
            x = (term.width - frame_width) // 2
            y = screen.height - len(frame_lines)

            screen.draw_sprite(frame_lines, x, y)
            screen.render(out)

            # Show status
            out(term.move_xy(0, term.height - 1) +
                f"Size: {current_label:8} | Frame: {frame_idx + 1}/{len(current_frames)} | 'q' to quit".ljust(term.width))
            flush()

            # Input handling
            key = term.inkey(timeout=0.20)
            if key.lower() == 'q':
                break

            # Advance frame
            frame_idx += 1

            # If we've gone through all frames in current size, move to next size
            if frame_idx >= len(current_frames):
                frame_idx = 0
                set_idx = (set_idx + 1) % len(frame_sets)
                current_frames, current_label = frame_sets[set_idx]


if __name__ == "__main__":
    main()
