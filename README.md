# Bunny Scroller

ASCII art animation of a running bunny with a scrolling tree background.

## Demo

Open `web/combined.html` in a browser.

## Controls

- **Left Arrow / A** - Bunny faces left, background scrolls right
- **Right Arrow / D** - Bunny faces right, background scrolls left
- **R** - Reset tree position

## Project Structure

```
frames/
  bunny/       # Bunny ASCII frames (left and right facing)
  tree/        # Tree ASCII frames at different sizes
tools/
  gif_to_ascii.py           # Convert GIF/images to ASCII art
  generate_combined_html.py # Generate the HTML animation
web/
  combined.html             # The animation (open this)
```

## Regenerating

If you modify frames or the generator:

```bash
python tools/generate_combined_html.py
```

## Converting Images to ASCII

```bash
python tools/gif_to_ascii.py image.png --width 40 --gradient minimalist --invert
python tools/gif_to_ascii.py image.png --width 40 --gradient minimalist --invert --flip  # Mirror horizontally
```

## Vanilla Python Animation

`demos/bunny_anim_vanilla.py` - dependency-free version using only stdlib.

Settings used to generate frames:
- **contrast**: 1.5
- **invert**: True
- **width**: 40
- **gradient**: ` .-+#` (space, dot, dash, plus, hash)
