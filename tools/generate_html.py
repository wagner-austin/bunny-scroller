#!/usr/bin/env python3
"""Generate HTML file with embedded ASCII frames."""

import sys
from pathlib import Path
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tree_frames.w20_frames import FRAMES as SMALL
from tree_frames.w58_frames import FRAMES as MED
from tree_frames.w100_frames import FRAMES as LARGE

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tree Zoom Animation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            min-height: 100vh;
            overflow: hidden;
        }}
        #ascii-bg {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: flex;
            align-items: center;      /* Center vertically */
            justify-content: center;  /* Center horizontally */
        }}
        #ascii-art {{
            font-family: "Courier New", monospace;
            font-size: clamp(6px, 1.2vw, 14px);
            line-height: 1.0;
            color: #4a4a4a;
            white-space: pre;
            /* Anchor zoom to center of element */
            transform-origin: center center;
        }}
        #info {{
            position: fixed;
            top: 10px; left: 10px;
            color: #666;
            font-family: sans-serif;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="ascii-bg"><pre id="ascii-art"></pre></div>
    <div id="info">Size: <span id="size">-</span></div>
    <script>
const FRAMES_SMALL = {json.dumps(SMALL)};
const FRAMES_MED = {json.dumps(MED)};
const FRAMES_LARGE = {json.dumps(LARGE)};

// Each frame set with its scale factor
// We scale the smaller ones UP so they appear to zoom
const frameSets = [
    {{ frames: FRAMES_SMALL, label: 'far', scale: 1.0 }},
    {{ frames: FRAMES_MED, label: 'medium', scale: 1.0 }},
    {{ frames: FRAMES_LARGE, label: 'close', scale: 1.0 }},
    {{ frames: FRAMES_MED, label: 'medium', scale: 1.0 }},
];

let setIdx = 0, frameIdx = 0;
const el = document.getElementById('ascii-art');
const sizeEl = document.getElementById('size');

function animate() {{
    const current = frameSets[setIdx];
    el.textContent = current.frames[frameIdx];
    sizeEl.textContent = current.label;

    frameIdx++;
    if (frameIdx >= current.frames.length) {{
        frameIdx = 0;
        setIdx = (setIdx + 1) % frameSets.length;
    }}
}}

setInterval(animate, 200);
animate();
    </script>
</body>
</html>'''

output = Path(__file__).parent.parent / "web" / "tree_zoom.html"
output.write_text(html)
print(f"Created {output}")
