"""
Visualization functions for color extraction results.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . import rgb_to_hex

def plot_single_result(img, img_array, colors, method_name, output_path=None, dpi=150):
    """
    Plot results for a single extraction method.

    Args:
        img: Original PIL Image
        img_array: numpy array of the image
        colors: List of extracted RGB colors
        method_name: Name of the extraction method
        output_path: Path to save the plot (optional)
        dpi: DPI for the plot

    Returns:
        PIL Image object
    """

    # Resize image
    max_width = 840
    max_height = 560
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    # Get resized image dimensions
    img_width, img_height = img.size

    # Calculate dimensions for the composite image
    num_colors = len(colors)

    # Swatch dimensions
    swatch_height = 60
    swatch_spacing = 8
    swatch_width = (max_width - swatch_spacing * (num_colors - 1)) / num_colors

    # Title heights
    title_height = 60
    method_title_height = 60

    # Calculate total height
    total_height = title_height + max_height + method_title_height + swatch_height + 80
    total_width = max_width + 40
    margin_x = (total_width - img_width) // 2

    # Create new image with white background
    composite = Image.new('RGB', (total_width, total_height), color='white')
    draw = ImageDraw.Draw(composite)

    FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'IBMPlexMono-regular.ttf')

    # Try to load a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype(FONT_PATH, 18)
        method_font = ImageFont.truetype(FONT_PATH, 18)
        hex_font = ImageFont.truetype(FONT_PATH, 12)
    except Exception as e:
        title_font = ImageFont.load_default()
        method_font = ImageFont.load_default()
        hex_font = ImageFont.load_default()

    # Draw "Original Image" title
    title_text = "Original Image"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (total_width - title_width) // 2
    draw.text((title_x, 25), title_text, fill='black', font=title_font)

    # Paste original image
    img_y = title_height + (max_height - img_height) // 2
    composite.paste(img, (margin_x, img_y))

    # Draw method name title
    method_bbox = draw.textbbox((0, 0), method_name, font=method_font)
    method_width = method_bbox[2] - method_bbox[0]
    method_x = (total_width - method_width) // 2
    method_y = title_height + max_height + 25
    draw.text((method_x, method_y), method_name, fill='black', font=method_font)

    # Draw color swatches
    swatch_y = title_height + max_height + method_title_height

    for i, color in enumerate(colors):
        # Calculate position
        x = i * (swatch_width + swatch_spacing) + 20

        # Ensure color values are valid integers
        color_tuple = tuple(int(c) for c in color)

        # Draw swatch rectangle
        draw.rectangle(
            [(x, swatch_y), (x + swatch_width, swatch_y + swatch_height)],
            fill=color_tuple,
            # outline='black',
            # width=2
        )

        # Draw hex code below swatch
        hex_code = rgb_to_hex(color)
        hex_bbox = draw.textbbox((0, 0), hex_code, font=hex_font)
        # hex_width = hex_bbox[2] - hex_bbox[0]
        hex_width = swatch_width
        hex_x = x + (swatch_width - hex_width) // 2 + 4
        hex_y = swatch_y + swatch_height + 10

        # Draw text with white background for better readability
        padding = 4
        text_bg_box = [
            hex_x - padding,
            hex_y - padding,
            hex_x + hex_width - padding,
            hex_y + (hex_bbox[3] - hex_bbox[1]) + padding * 3
        ]
        draw.rectangle(text_bg_box, fill='white', outline='lightgray')
        draw.text((hex_x, hex_y), hex_code, fill='black', font=hex_font)

    # Save if output path provided
    if output_path:
        composite.save(output_path, dpi=(dpi, dpi))
        print(f"\nResult saved to {output_path}")

    return composite


def plot_comparison(img, img_array, algorithms_dict, output_path=None, dpi=150):
    """
    Plot comparison of multiple extraction methods.

    Args:
        img: Original PIL Image
        img_array: numpy array of the image
        algorithms_dict: Dictionary mapping method names to extracted colors
        output_path: Path to save the plot (optional)
        dpi: DPI for the plot

    Returns:
        matplotlib figure object
    """
    # Calculate figure size based on image dimensions
    img_width_px, img_height_px = img.size

    # Convert to inches
    img_width_in = img_width_px / dpi
    img_height_in = img_height_px / dpi

    # Number of methods to compare
    n_methods = len(algorithms_dict)

    # Add space for each method's swatches
    fig_width = img_width_in
    fig_height = img_height_in + (n_methods * 2.0) + 1.0  # Image + methods + padding

    fig = plt.figure(figsize=(fig_width * 0.86, fig_height), dpi=dpi)

    # Create gridspec: 1 row for image + n rows for methods
    height_ratios = [img_height_in] + [2.0] * n_methods
    gs = fig.add_gridspec(n_methods + 1, 1, height_ratios=height_ratios,
                          hspace=0.3, left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Show original image on top
    ax_img = fig.add_subplot(gs[0])
    ax_img.imshow(img)
    ax_img.set_title('Original Image', fontsize=18, fontweight='bold', pad=10)
    ax_img.axis('off')

    # Plot each method's color palette in rows below
    for idx, (name, colors) in enumerate(algorithms_dict.items()):
        ax = fig.add_subplot(gs[idx + 1])
        ax.set_title(name, fontsize=18, fontweight='bold', pad=10)
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 2)
        ax.axis('off')

        # Each swatch takes up 1 unit of width
        swatch_width = 0.95

        for i, color in enumerate(colors):
            color_normalized = np.clip(np.array(color) / 255.0, 0, 1)

            # Draw color swatch
            rect = Rectangle((i + 0.025, 0.6), swatch_width, 1.2,
                           facecolor=color_normalized,
                           linewidth=2)
            ax.add_patch(rect)

            # Add hex code below swatch
            hex_code = rgb_to_hex(color)
            ax.text(i + 0.5, 0.4, hex_code,
                   ha='center', va='top', fontsize=12, fontweight='bold')

    if output_path:
        plt.savefig(output_path, dpi=dpi)
        print(f"\nComparison saved to {output_path}")

    return fig


def print_color_results(colors, method_name):
    """
    Print color results to console.

    Args:
        colors: List of extracted RGB colors
        method_name: Name of the extraction method
    """
    console = Console()

    console.print(Panel(f"{method_name}", width=39, box=box.SQUARE, style="#AAAAAA"))

    table = Table(show_header=False, style="#AAAAAA")
    table.add_column("■■■", width=5, justify="center")
    table.add_column("Hex", width=8)
    table.add_column("RGB", width=16)

    # print(f"\n{method_name}:")
    # print("=" * 40)

    for i, color in enumerate(colors, 1):
        hex_code = rgb_to_hex(color)
        rgb_str = f"({int(color[0])}, {int(color[1])}, {int(color[2])})"
        # print(f"  {i}. {hex_code:10s} {rgb_str}")
        table.add_row(f"[{hex_code}]■■■", f"{hex_code:10s}", rgb_str)

    # print("=" * 40)
    console.print(table)


def create_color_palette_image(colors, width=100, height=100):
    """
    Create a simple color palette image as a numpy array.

    Args:
        colors: List of RGB colors
        width: Width of each color swatch
        height: Height of the palette

    Returns:
        numpy array representing the palette image
    """
    n_colors = len(colors)
    palette_width = width * n_colors
    palette = np.zeros((height, palette_width, 3), dtype=np.uint8)

    for i, color in enumerate(colors):
        start_x = i * width
        end_x = (i + 1) * width
        palette[:, start_x:end_x] = color

    return palette
