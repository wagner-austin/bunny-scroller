#!/usr/bin/env python3
"""
Export Python frame files to TypeScript/JavaScript format.

Usage:
    python export_frames_ts.py tree_frames/ --output web/frames/
"""

import argparse
import json
from pathlib import Path
import importlib.util


def load_frames_from_py(py_file: Path) -> list[str]:
    """Load FRAMES array from a Python file."""
    spec = importlib.util.spec_from_file_location("frames", py_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FRAMES


def export_to_typescript(frames: list[str], output_path: Path, name: str):
    """Export frames as TypeScript file."""
    with open(output_path, 'w') as f:
        f.write(f'/** {name} - {len(frames)} frames */\n\n')
        f.write('export const FRAMES: string[] = [\n')
        for frame in frames:
            # Escape backticks and ${} in template literals
            escaped = frame.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
            f.write(f'  `{escaped}`,\n')
        f.write('];\n')


def export_to_json(frames: list[str], output_path: Path):
    """Export frames as JSON file."""
    with open(output_path, 'w') as f:
        json.dump(frames, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Export frames to TypeScript/JSON")
    parser.add_argument("input_dir", help="Directory containing *_frames.py files")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--format", choices=["ts", "json", "both"], default="ts",
                        help="Output format (default: ts)")

    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all *_frames.py files
    frame_files = list(input_path.glob("*_frames.py"))

    if not frame_files:
        print(f"No *_frames.py files found in {input_path}")
        return

    for py_file in frame_files:
        name = py_file.stem  # e.g., "w20_frames"
        print(f"Processing {py_file.name}...")

        frames = load_frames_from_py(py_file)

        if args.format in ["ts", "both"]:
            ts_file = output_path / f"{name}.ts"
            export_to_typescript(frames, ts_file, name)
            print(f"  -> {ts_file}")

        if args.format in ["json", "both"]:
            json_file = output_path / f"{name}.json"
            export_to_json(frames, json_file)
            print(f"  -> {json_file}")

    # Create index.ts if exporting TypeScript
    if args.format in ["ts", "both"]:
        index_file = output_path / "index.ts"
        with open(index_file, 'w') as f:
            f.write("// Auto-generated index\n\n")
            for py_file in frame_files:
                name = py_file.stem
                f.write(f"export {{ FRAMES as {name.upper()} }} from './{name}';\n")
        print(f"Created {index_file}")


if __name__ == "__main__":
    main()
