"""
Command-line interface for color extraction.
"""

import argparse
import os
import re
import pathlib

from . import EXTRACTION_METHODS
from . import load_and_prepare_image, sort_colors_by_spatial_position
from . import plot_single_result, plot_comparison, print_color_results


def main():
    """Main CLI entry point for color extraction."""
    parser = argparse.ArgumentParser(
        description='Extract dominant colors from an image using K-Means clustering.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  color-extract photo.jpg
  color-extract photo.jpg --colors 8
  color-extract photo.jpg --method lab
  color-extract photo.jpg --method all --output comparison.png

Available methods:
  kmeans      - Original K-Means
  aggressive  - Aggressive Weighting
  vibrant     - Vibrant Separate
  lab         - LAB Enhanced (default)
  multistage  - Multi-stage
  all         - Compare all methods
        """
    )

    parser.add_argument('image', help='Path to the input image')
    parser.add_argument('--colors', '-c', type=int, default=6, help='Number of colors to extract (default: 6)')
    parser.add_argument('--method', '-m', default='lab', choices=list(EXTRACTION_METHODS.keys()) + ['all'], help='Extraction method (default: lab)')
    parser.add_argument('--output', '-o', default=None, help='Output file path (default: ./output')
    parser.add_argument('--no-plot', action='store_true', help='Disable plot generation')
    parser.add_argument('--sort', choices=['x-axis', 'y-axis', 'frequency'], default='x-axis', help='Color sorting method (default: x-axis)')
    parser.add_argument('--max-dimension', type=int, default=64, help='Maximum dimension for image downscaling (default: 64)')
    parser.add_argument('--dpi', type=int, default=150, help='DPI for output plots (default: 150)')

    args = parser.parse_args()

    # Output path
    output_path = pathlib.Path(args.output or './output')
    output_path.mkdir(parents=True, exist_ok=True)

    # Get the base filename without path and extension
    base_name = os.path.splitext(os.path.basename(args.image))[0]
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[^\w\-]', '_', base_name)
    # Compose filename
    filename = f'colors_{safe_name}_{args.method}_{args.colors}.png'

    if args.output is None or output_path.is_dir() or (not output_path.exists() and not output_path.suffix):
       args.output = f"{output_path}/{filename}"

    # Load image
    # print(f"Loading image: {args.image}")
    img, img_array = load_and_prepare_image(args.image, args.max_dimension)

    # print(f"Extracting {args.colors} colors...")

    if args.method == 'all':
        # Run all methods and compare
        print("Running all methods for comparison...")
        algorithms_dict = {}

        for method_key, (display_name, func) in EXTRACTION_METHODS.items():
            colors = func(img_array, args.colors)

            # Apply sorting
            if args.sort == 'x-axis':
                sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='x')
            elif args.sort == 'y-axis':
                sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='y')
            else:
                sorted_colors = colors  # Already sorted by frequency from extraction

            algorithms_dict[display_name] = sorted_colors
            print_color_results(sorted_colors, display_name)

        if not args.no_plot:
            plot_comparison(img, img_array, algorithms_dict, args.output, dpi=args.dpi)

    else:
        # Run single method
        display_name, func = EXTRACTION_METHODS[args.method]
        # print(f"Using method: {display_name}")
        colors = func(img_array, args.colors)

        # Apply sorting
        if args.sort == 'x-axis':
            sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='x')
            # print("Colors sorted by spatial position (left→right)")
        elif args.sort == 'y-axis':
            sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='y')
            # print("Colors sorted by spatial position (top→bottom)")
        else:
            sorted_colors = colors
            # print("Colors sorted by frequency")

        print_color_results(sorted_colors, display_name)

        if not args.no_plot:
            plot_single_result(img, img_array, sorted_colors, args.method, display_name,
                             args.output, dpi=args.dpi)

    # print("\nDone!")


if __name__ == "__main__":
    main()
