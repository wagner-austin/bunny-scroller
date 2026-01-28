"""
Demo: blessed library
Run: poetry run python demos/demo_blessed.py

Controls:
- A/D: Move left/right (digs if underground)
- W: Move up (digs up if underground)
- S: Move down (digs into grass)
- SPACE: Jump (simple 3-frame animation)
- Q: Quit
"""

import sys
import os
import time

# Fix Windows encoding for Unicode/emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.system('chcp 65001 > nul 2>&1')

from blessed import Terminal
import wcwidth
import random

def char_width(char: str) -> int:
    """Get display width of a character (emoji = 2, ascii = 1)."""
    w = wcwidth.wcswidth(char)
    return max(1, w)

# Tile types
SKY = 0
GRASS = 1
DIRT = 2

def main():
    term = Terminal()

    # Play area - auto-size to terminal
    area_x = 2
    area_y = 2
    area_w = term.width - 4      # Leave 2 chars padding on each side
    area_h = term.height - 7     # Leave room for header (1) + gap (1) + instructions (3) + padding (2)

    # Terrain grid - top portion sky, rest is grass
    sky_rows = max(6, area_h // 3)  # At least 6 rows, or 1/3 of height
    terrain = []
    for row in range(area_h):
        if row < sky_rows:
            terrain.append([SKY] * area_w)
        else:
            terrain.append([GRASS] * area_w)

    # Ground level - the Y position where bunny stands ON TOP of grass
    ground_y = area_y + sky_rows - 1

    # Player position (tile coordinates)
    player_x = area_x + area_w // 4  # Start 1/4 from left
    player_y = ground_y  # Start on ground

    player_char = '🐇'

    # Jump state
    jumping = False
    jump_frame = 0
    jump_start_y = 0

    def get_tile(gx, gy):
        """Get tile at grid position."""
        row = gy - area_y
        col = gx - area_x
        if 0 <= row < area_h and 0 <= col < area_w:
            return terrain[row][col]
        return -1  # Out of bounds

    def set_tile(gx, gy, tile):
        """Set tile at grid position."""
        row = gy - area_y
        col = gx - area_x
        if 0 <= row < area_h and 0 <= col < area_w:
            terrain[row][col] = tile

    # RGB Colors
    sky_color = term.on_color_rgb(70, 130, 180)  # Steel blue (darker sky)

    # Grass color variations (different greens)
    grass_colors = [
        term.on_color_rgb(34, 139, 34),   # Forest green
        term.on_color_rgb(0, 128, 0),     # Green
        term.on_color_rgb(50, 150, 50),   # Lighter green
        term.on_color_rgb(34, 120, 34),   # Darker forest
    ]

    # Dirt color variations (different browns)
    dirt_colors = [
        term.on_color_rgb(139, 90, 43),   # Saddle brown
        term.on_color_rgb(120, 80, 40),   # Darker brown
        term.on_color_rgb(150, 100, 50),  # Lighter brown
        term.on_color_rgb(130, 85, 45),   # Medium brown
    ]

    def get_grass_color(x, y):
        """Get a deterministic grass color based on position."""
        idx = ((x * 7) + (y * 13)) % len(grass_colors)
        return grass_colors[idx]

    def get_dirt_color(x, y):
        """Get a deterministic dirt color based on position."""
        idx = ((x * 11) + (y * 17)) % len(dirt_colors)
        return dirt_colors[idx]

    # Multi-row ASCII clouds using ▓▒░ (2-3 rows, wide)
    def make_cloud_pattern(size):
        """Generate a cloud pattern. Size: 'small', 'medium', 'large'"""
        if size == 'small':
            # 2 rows, wide and flat
            return [
                (0, 0, '░'), (1, 0, '▒'), (2, 0, '▓'), (3, 0, '▓'), (4, 0, '▓'), (5, 0, '▒'), (6, 0, '░'),
                (1, 1, '░'), (2, 1, '▒'), (3, 1, '▒'), (4, 1, '▒'), (5, 1, '░'),
            ]
        elif size == 'medium':
            # 2 rows, wider
            return [
                (0, 0, '░'), (1, 0, '▒'), (2, 0, '▓'), (3, 0, '▓'), (4, 0, '▓'), (5, 0, '▓'), (6, 0, '▓'), (7, 0, '▒'), (8, 0, '░'),
                (1, 1, '░'), (2, 1, '▒'), (3, 1, '▓'), (4, 1, '▓'), (5, 1, '▓'), (6, 1, '▒'), (7, 1, '░'),
            ]
        else:  # large
            # 3 rows, widest
            return [
                (1, 0, '░'), (2, 0, '▒'), (3, 0, '▓'), (4, 0, '▓'), (5, 0, '▓'), (6, 0, '▓'), (7, 0, '▒'), (8, 0, '░'),
                (0, 1, '░'), (1, 1, '▒'), (2, 1, '▓'), (3, 1, '▓'), (4, 1, '▓'), (5, 1, '▓'), (6, 1, '▓'), (7, 1, '▓'), (8, 1, '▒'), (9, 1, '░'),
                (1, 2, '░'), (2, 2, '▒'), (3, 2, '▒'), (4, 2, '▓'), (5, 2, '▓'), (6, 2, '▒'), (7, 2, '▒'), (8, 2, '░'),
            ]

    # Clouds with parallax - [x, y, speed, pattern, last_move_time, tint]
    init_time = time.time()
    clouds = []
    num_clouds = max(4, area_w // 35)
    for i in range(num_clouds):
        # Parallax: row 0 = far/slow, row 1-2 = closer/faster
        depth = random.randint(0, 2)
        x = area_x + random.randint(0, area_w - 10)
        y = area_y + depth
        # Speed based on depth
        base_speed = [1.4, 0.9, 0.6][depth]
        speed = base_speed + random.random() * 0.3
        # Size based on depth (far = small, close = large)
        size = ['small', 'medium', 'large'][depth]
        pattern = make_cloud_pattern(size)
        # Tint: far = hazier/darker, close = brighter
        tint = [(180, 190, 210), (220, 230, 245), (250, 252, 255)][depth]
        clouds.append([x, y, speed, pattern, init_time + random.random() * 2, tint])

    # Canopy color palettes (fg_color variations)
    canopy_palettes = [
        [(34, 139, 34), (0, 100, 0), (50, 150, 50), (25, 120, 25)],      # Classic green
        [(60, 150, 60), (30, 120, 30), (80, 170, 80), (45, 135, 45)],    # Bright green
        [(25, 100, 25), (10, 80, 10), (40, 115, 40), (20, 90, 20)],      # Dark green
        [(50, 140, 70), (30, 110, 50), (70, 160, 90), (40, 125, 60)],    # Teal-green
    ]

    # Trunk color palettes (fg, bg variations)
    trunk_palettes = [
        [((80, 50, 25), (55, 35, 18)), ((95, 60, 30), (70, 45, 22))],    # Brown
        [((70, 45, 30), (50, 30, 20)), ((85, 55, 35), (60, 40, 25))],    # Dark brown
        [((90, 70, 50), (65, 50, 35)), ((105, 80, 55), (75, 60, 40))],   # Light brown
        [((60, 40, 25), (40, 28, 16)), ((75, 50, 30), (55, 38, 22))],    # Reddish brown
    ]

    def generate_tree(canopy_width, canopy_rows, trunk_width, trunk_height, canopy_palette_idx, trunk_palette_idx):
        """Generate a tree pattern with given parameters."""
        cells = []
        canopy_pal = canopy_palettes[canopy_palette_idx % len(canopy_palettes)]
        trunk_pal = trunk_palettes[trunk_palette_idx % len(trunk_palettes)]

        trunk_center = canopy_width // 2

        # Generate FLAT umbrella canopy - wide and flat
        # Canopy bottom row at dy = -trunk_height (connects to trunk top)
        for row in range(canopy_rows):
            dy = -trunk_height - (canopy_rows - 1 - row)  # Bottom row = -trunk_height
            # Umbrella: all rows nearly same width, top row slightly narrower
            if row == 0:
                row_width = canopy_width - 4
            else:
                row_width = canopy_width
            half_w = row_width // 2

            for dx in range(-half_w, half_w + 1):
                x = trunk_center + dx
                # Style: edges are light, interior is dense
                dist_from_edge = min(abs(dx + half_w), abs(half_w - dx))
                if dist_from_edge <= 1:
                    style = 2  # Light edge (░)
                elif dist_from_edge <= 2:
                    style = 1  # Medium (▒)
                else:
                    style = random.choice([0, 0, 3])  # Dense (▓)
                cells.append((x, dy, 'leaf', style, canopy_pal))

        # Generate trunk - from just under canopy down to grass
        # Canopy ends at dy = -(trunk_height + 1), trunk starts at -(trunk_height)
        wave_offsets = [0, 1, 0, -1, -1, 0, 1, 1, 0, -1]
        for i, dy in enumerate(range(-trunk_height, 2)):  # -trunk_height to 1 inclusive
            wave_idx = i % len(wave_offsets)
            offset = wave_offsets[wave_idx]
            half_tw = trunk_width // 2
            for dx in range(-half_tw, half_tw + 1):
                x = trunk_center + dx + offset
                style = random.randint(0, 1)
                cells.append((x, dy, 'trunk', style, trunk_pal))

        return cells

    # Generate varied trees across the width
    trees = []  # (base_x, cells, grass_depth)
    x = 5
    while x < area_w - 25:
        # Randomize tree parameters
        canopy_w = random.randint(14, 24)
        canopy_rows = random.randint(2, 4)
        trunk_w = random.randint(4, 7)
        trunk_h = random.randint(3, 6)
        canopy_pal = random.randint(0, len(canopy_palettes) - 1)
        trunk_pal = random.randint(0, len(trunk_palettes) - 1)
        grass_depth = random.randint(0, 2)  # 0=on ground, 1=in row 1, 2=in row 2

        cells = generate_tree(canopy_w, canopy_rows, trunk_w, trunk_h, canopy_pal, trunk_pal)
        trees.append((x, cells, grass_depth))

        # Random spacing
        x += random.randint(25, 40)

    # Store which cells are part of trees for redrawing
    # tree_cells[(x,y)] = (cell_type, style_idx, palette)
    tree_cells = {}

    def init_trees():
        """Initialize tree cell data."""
        for base_x, cells, grass_depth in trees:
            for cell in cells:
                dx, dy, cell_type, style_idx, palette = cell
                x = area_x + base_x + dx
                y = ground_y + dy + grass_depth - 1  # Shift up 1 tile
                if area_x <= x < area_x + area_w and area_y <= y < area_y + area_h:
                    tree_cells[(x, y)] = (cell_type, style_idx, palette)

    def draw_tree_cell(x, y, cell_data):
        """Draw a single tree cell."""
        cell_type, style_idx, palette = cell_data
        chars = ['▓', '▒', '░', '▓']
        char = chars[style_idx % len(chars)]

        if cell_type == 'leaf':
            # Leaf: green fg on sky bg
            color = palette[style_idx % len(palette)]
            fg = term.color_rgb(color[0], color[1], color[2])
            print(term.move_xy(x, y) + fg + sky_color + char, end='')
        else:
            # Trunk: brown fg on darker brown bg
            fg_color, bg_color = palette[style_idx % len(palette)]
            fg = term.color_rgb(fg_color[0], fg_color[1], fg_color[2])
            bg = term.on_color_rgb(bg_color[0], bg_color[1], bg_color[2])
            print(term.move_xy(x, y) + fg + bg + char, end='')

    def draw_trees():
        """Draw all trees."""
        for (x, y), cell_data in tree_cells.items():
            if area_x <= x < area_x + area_w:
                draw_tree_cell(x, y, cell_data)
        print('', end='', flush=True)

    def redraw_tree_at(x, y):
        """Redraw tree cell at position if there is one."""
        if (x, y) in tree_cells:
            draw_tree_cell(x, y, tree_cells[(x, y)])

    def get_trunk_bg(cell_data):
        """Get background color for trunk cell from its palette."""
        _, style_idx, palette = cell_data
        _, bg_color = palette[style_idx % len(palette)]
        return term.on_color_rgb(bg_color[0], bg_color[1], bg_color[2])

    def get_bg_at(x, y):
        """Get the background color at a single position (tree, sky, dirt, or grass)."""
        # Check if it's a tree cell
        if (x, y) in tree_cells:
            cell_data = tree_cells[(x, y)]
            if cell_data[0] == 'leaf':
                return sky_color  # Leaves have sky background (see-through effect)
            else:
                return get_trunk_bg(cell_data)
        # Otherwise use terrain
        tile = get_tile(x, y)
        if tile == SKY:
            return sky_color
        elif tile == DIRT:
            return get_dirt_color(x, y)
        else:
            return get_grass_color(x, y)

    def get_entity_bg(x, y, width=2):
        """Get background color for an entity spanning multiple cells.
        If any cell is a tree, use tree color. Otherwise use terrain."""
        # Check all positions the entity covers
        for dx in range(width):
            if (x + dx, y) in tree_cells:
                cell_data = tree_cells[(x + dx, y)]
                if cell_data[0] == 'leaf':
                    return sky_color  # Leaves have sky background (see-through effect)
                else:
                    return get_trunk_bg(cell_data)
        # No tree overlap, use terrain at starting position
        return get_bg_at(x, y)

    def redraw_cell(x, y):
        """Redraw a single cell - tree cell or terrain."""
        if (x, y) in tree_cells:
            draw_tree_cell(x, y, tree_cells[(x, y)])
        else:
            draw_tile(x, y)

    def redraw_cells(x, y, width):
        """Redraw multiple cells starting at x, y."""
        for dx in range(width):
            redraw_cell(x + dx, y)

    # Initialize tree data
    init_trees()

    # Butterflies state - fly in rows 2-4 of sky, spread across width
    num_butterflies = max(2, area_w // 40)
    butterflies = []
    for i in range(num_butterflies):
        butterflies.append({
            'x': area_x + (i + 1) * area_w // (num_butterflies + 1),
            'y': area_y + 2 + (i % 3),
            'last_move': init_time + i * 0.3,
            'emoji': '🦋',
            'speed': 0.8 + random.random() * 0.4
        })

    def draw_butterflies():
        """Draw all butterflies."""
        for b in butterflies:
            if area_x <= b['x'] < area_x + area_w - 1:
                width = char_width(b['emoji'])
                bg = get_entity_bg(b['x'], b['y'], width)
                print(term.move_xy(b['x'], b['y']) + bg(b['emoji']), end='')
        print('', end='', flush=True)

    def clear_butterfly(b):
        """Clear a butterfly position."""
        width = char_width(b['emoji'])
        redraw_cells(b['x'], b['y'], width)

    def update_butterflies():
        """Update butterflies - random movement with flicker on move."""
        now = time.time()

        for b in butterflies:
            if now - b['last_move'] >= b['speed']:
                clear_butterfly(b)
                print('', end='', flush=True)

                # Random direction
                dx = random.choice([-1, 0, 0, 1])
                dy = random.choice([-1, 0, 0, 1])

                new_x = b['x'] + dx
                new_y = b['y'] + dy

                # Constrain to rows 2-4 of sky and within bounds
                if area_x <= new_x < area_x + area_w - 2:
                    b['x'] = new_x
                if area_y + 2 <= new_y <= area_y + 4:
                    b['y'] = new_y

                b['last_move'] = now
                if area_x <= b['x'] < area_x + area_w - 1:
                    width = char_width(b['emoji'])
                    bg = get_entity_bg(b['x'], b['y'], width)
                    print(term.move_xy(b['x'], b['y']) + bg(b['emoji']), end='', flush=True)

    def draw_clouds():
        """Draw all multi-cell clouds."""
        for cloud in clouds:
            cx, cy, _, pattern, _, tint = cloud
            cloud_color = term.color_rgb(tint[0], tint[1], tint[2])
            for dx, dy, char in pattern:
                px, py = cx + dx, cy + dy
                if area_x <= px < area_x + area_w and area_y <= py < area_y + sky_rows:
                    print(term.move_xy(px, py) + sky_color + cloud_color + char, end='')

    def clear_cloud(cloud):
        """Clear a cloud - redraw underlying cells."""
        cx, cy, _, pattern, _, _ = cloud
        for dx, dy, _ in pattern:
            px, py = cx + dx, cy + dy
            if area_x <= px < area_x + area_w and area_y <= py < area_y + sky_rows:
                redraw_cell(px, py)

    def update_clouds():
        """Move clouds based on their speed using real time."""
        now = time.time()
        any_moved = False
        for cloud in clouds:
            last_move = cloud[4]
            speed = cloud[2]
            if now - last_move >= speed:
                # Clear old position
                clear_cloud(cloud)
                # Move cloud
                cloud[0] += 1
                # Wrap around (clouds are wider now)
                if cloud[0] >= area_x + area_w + 5:
                    cloud[0] = area_x - 10
                cloud[4] = now
                any_moved = True
        # Only redraw and flush if something moved
        if any_moved:
            draw_clouds()
            print('', end='', flush=True)

    def draw_tile(x, y):
        """Draw a single tile."""
        tile = get_tile(x, y)
        if tile == SKY:
            print(term.move_xy(x, y) + sky_color(' '), end='')
        elif tile == GRASS:
            print(term.move_xy(x, y) + get_grass_color(x, y)(' '), end='')
        elif tile == DIRT:
            print(term.move_xy(x, y) + get_dirt_color(x, y)(' '), end='')

    def draw_player():
        """Draw the player."""
        bg = get_entity_bg(player_x, player_y, width=2)
        print(term.move_xy(player_x, player_y) + bg(player_char), end='', flush=True)

    def clear_player():
        """Clear player from current position."""
        redraw_cells(player_x, player_y, width=2)

    def is_underground():
        """Check if player is below ground level (in the dirt/grass)."""
        return player_y > ground_y

    def is_on_ground():
        """Check if player is standing on ground level."""
        return player_y == ground_y

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)

        # Header
        print(term.move_xy(0, 0) + term.bold_white_on_blue(
            ' BLESSED DEMO - Dig & Jump! '.center(term.width)
        ))

        # Instructions at bottom - compact centered box
        inst_y = area_y + area_h + 1
        box_color = term.color_rgb(80, 60, 40)
        accent_color = term.color_rgb(180, 140, 80)
        key_color = term.color_rgb(255, 220, 120)
        text_color = term.color_rgb(200, 200, 180)

        content = (key_color + 'A/D' + text_color + ' Move  ' +
                   key_color + 'W' + text_color + ' Up  ' +
                   key_color + 'S' + text_color + ' Dig  ' +
                   key_color + 'SPACE' + text_color + ' Jump  ' +
                   key_color + 'Q' + text_color + ' Quit')

        box_inner = 46  # Content width
        box_w = box_inner + 4
        inst_x = (term.width - box_w) // 2

        print(term.move_xy(inst_x, inst_y) + accent_color + '┌' + '─' * box_inner + '─┐')
        print(term.move_xy(inst_x, inst_y + 1) + accent_color + '│ ' + content + '  ' + accent_color + '│')
        print(term.move_xy(inst_x, inst_y + 2) + accent_color + '└' + '─' * box_inner + '─┘')

        # Draw terrain
        for row in range(area_h):
            for col in range(area_w):
                draw_tile(area_x + col, area_y + row)

        # Draw initial clouds, butterflies, and trees
        draw_clouds()
        draw_butterflies()
        draw_trees()

        # Draw border
        for row in range(area_h):
            y = area_y + row
            print(term.move_xy(area_x - 1, y) + term.on_white(' '), end='')
            print(term.move_xy(area_x + area_w, y) + term.on_white(' '), end='')
        print(term.move_xy(area_x - 1, area_y - 1) + term.on_white(' ' * (area_w + 2)), end='')
        print(term.move_xy(area_x - 1, area_y + area_h) + term.on_white(' ' * (area_w + 2)), end='')

        # Draw player
        draw_player()

        # Game loop
        running = True
        last_jump_time = 0

        while running:
            key = term.inkey(timeout=0.05)

            # Update clouds and butterfly (runs on real time, independent of input)
            update_clouds()
            update_butterflies()

            # Handle jump animation
            if jumping:
                now = time.time()
                elapsed = now - last_jump_time

                if jump_frame == 0 and elapsed > 0:
                    # Frame 1: Go up
                    clear_player()
                    player_y -= 1
                    draw_player()
                    jump_frame = 1
                    last_jump_time = now
                elif jump_frame == 1 and elapsed > 0.15:
                    # Frame 2: Stay up (just wait)
                    jump_frame = 2
                    last_jump_time = now
                elif jump_frame == 2 and elapsed > 0.15:
                    # Frame 3: Come back down
                    clear_player()
                    player_y = jump_start_y
                    draw_player()
                    jumping = False
                    jump_frame = 0

            if key:
                if key.lower() == 'q':
                    running = False

                elif key == ' ' and not jumping:
                    # Jump - only if on ground level
                    if is_on_ground():
                        jumping = True
                        jump_frame = 0
                        jump_start_y = player_y
                        last_jump_time = time.time()

                elif key.lower() == 'a' or key.name == 'KEY_LEFT':
                    # Move left
                    if not jumping:
                        new_x = player_x - 1
                        if new_x >= area_x:
                            target_tile = get_tile(new_x, player_y)
                            if target_tile == SKY or target_tile == DIRT:
                                # Can move freely in sky or already-dug dirt
                                clear_player()
                                player_x = new_x
                                draw_player()
                            elif target_tile == GRASS and is_underground():
                                # Underground: dig into grass
                                clear_player()
                                set_tile(new_x, player_y, DIRT)
                                set_tile(new_x + 1, player_y, DIRT)  # For emoji width
                                player_x = new_x
                                draw_tile(new_x, player_y)
                                draw_tile(new_x + 1, player_y)
                                draw_player()

                elif key.lower() == 'd' or key.name == 'KEY_RIGHT':
                    # Move right
                    if not jumping:
                        new_x = player_x + 1
                        if new_x + 1 < area_x + area_w:
                            # Check tile at right edge of emoji
                            target_tile = get_tile(new_x + 1, player_y)
                            if target_tile == SKY or target_tile == DIRT:
                                clear_player()
                                player_x = new_x
                                draw_player()
                            elif target_tile == GRASS and is_underground():
                                # Underground: dig into grass
                                clear_player()
                                set_tile(new_x, player_y, DIRT)
                                set_tile(new_x + 1, player_y, DIRT)
                                player_x = new_x
                                draw_tile(new_x, player_y)
                                draw_tile(new_x + 1, player_y)
                                draw_player()

                elif key.lower() == 's' or key.name == 'KEY_DOWN':
                    # Move down / dig
                    if not jumping:
                        new_y = player_y + 1
                        if new_y < area_y + area_h:
                            tile_below = get_tile(player_x, new_y)
                            tile_below2 = get_tile(player_x + 1, new_y)

                            if tile_below == GRASS or tile_below2 == GRASS:
                                # Dig into grass
                                clear_player()
                                set_tile(player_x, new_y, DIRT)
                                set_tile(player_x + 1, new_y, DIRT)
                                draw_tile(player_x, new_y)
                                draw_tile(player_x + 1, new_y)
                                player_y = new_y
                                draw_player()
                            elif tile_below == DIRT or tile_below == SKY:
                                # Move into empty space
                                clear_player()
                                player_y = new_y
                                draw_player()

                elif key.lower() == 'w' or key.name == 'KEY_UP':
                    # Move up - ONLY works underground, not on surface
                    if not jumping and is_underground():
                        new_y = player_y - 1
                        tile_above = get_tile(player_x, new_y)
                        tile_above2 = get_tile(player_x + 1, new_y)

                        if tile_above == SKY or tile_above == DIRT:
                            # Move up into dug tunnel or back to surface
                            clear_player()
                            player_y = new_y
                            draw_player()
                        elif tile_above == GRASS:
                            # Dig up through grass
                            clear_player()
                            set_tile(player_x, new_y, DIRT)
                            set_tile(player_x + 1, new_y, DIRT)
                            draw_tile(player_x, new_y)
                            draw_tile(player_x + 1, new_y)
                            player_y = new_y
                            draw_player()

if __name__ == '__main__':
    main()
