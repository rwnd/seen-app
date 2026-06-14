"""
crop_archetypes.py

Crops the icon/badge from PrinciplesYou archetype share images.
Removes the right-side text panel and the bottom PrinciplesYou footer bar.

Usage:
    python crop_archetypes.py --input ./raw --output ./static/images/archetypes

Input images are the og:image share cards downloaded from PrinciplesYou.
All images share the same layout (1410x740) so a single crop box works for all.

Crop box (pixels): left=25, top=15, right=535, bottom=495
This isolates the sticker badge including the illustration and name label,
excluding the right-side description text and the bottom footer bar.
"""

import argparse
from pathlib import Path
from PIL import Image

# Crop coordinates tuned to 1410x740 PrinciplesYou og:image format.
# Adjust these if your images are a different size.
EXPECTED_WIDTH = 1410
EXPECTED_HEIGHT = 740
CROP_BOX = (25, 15, 650, 550)  # (left, top, right, bottom)


def crop_image(input_path: Path, output_path: Path, force: bool = False) -> bool:
    """Crop a single archetype image. Returns True on success."""
    if output_path.exists() and not force:
        print(f"  SKIP  {input_path.name} (already exists, use --force to overwrite)")
        return False

    try:
        img = Image.open(input_path)

        # Warn if dimensions differ from expected — crop box may be wrong
        if img.size != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
            print(f"  WARN  {input_path.name} — unexpected size {img.size}, "
                  f"expected {(EXPECTED_WIDTH, EXPECTED_HEIGHT)}. Cropping anyway.")

        cropped = img.crop(CROP_BOX)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path, format="PNG", optimize=True)
        print(f"  OK    {input_path.name} → {output_path.name} ({cropped.size[0]}x{cropped.size[1]})")
        return True

    except Exception as e:
        print(f"  ERROR {input_path.name} — {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Crop PrinciplesYou archetype badge images.")
    parser.add_argument("--input", default="./raw", help="Folder containing raw og:image downloads")
    parser.add_argument("--output", default="./static/images/archetypes", help="Output folder for cropped icons")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output files")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"Input folder not found: {input_dir}")
        return

    images = sorted(input_dir.glob("*.png")) + sorted(input_dir.glob("*.jpg"))

    if not images:
        print(f"No PNG or JPG files found in {input_dir}")
        return

    print(f"Found {len(images)} image(s) in {input_dir}")
    print(f"Output → {output_dir}\n")

    ok = 0
    for img_path in images:
        out_path = output_dir / (img_path.stem + ".png")
        if crop_image(img_path, out_path, force=args.force):
            ok += 1

    print(f"\nDone. {ok}/{len(images)} images cropped.")


if __name__ == "__main__":
    main()