"""
Visualization functions for color extraction results.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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
        matplotlib figure object
    """
    # Calculate figure size based on image dimensions
    img_width_px, img_height_px = img.size

    # Convert to inches
    img_width_in = img_width_px / dpi
    img_height_in = img_height_px / dpi

    # Add space for titles and swatches
    fig_width = img_width_in
    fig_height = img_height_in + 2.5  # Extra space for title and swatches

    fig = plt.figure(figsize=(fig_width * 0.86, fig_height), dpi=dpi)

    # Create gridspec with precise height ratios
    gs = fig.add_gridspec(2, 1, height_ratios=[img_height_in, 2.5],
                          hspace=0.3, left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Show original image on top
    ax_img = fig.add_subplot(gs[0])
    ax_img.imshow(img)
    ax_img.set_title('Original Image', fontsize=18, fontweight='bold', pad=10)
    ax_img.axis('off')

    # Show color palette below
    ax_colors = fig.add_subplot(gs[1])
    ax_colors.set_title(f'{method_name}', fontsize=18, fontweight='bold', pad=10)

    # Use normalized coordinates (0 to len(colors)) for swatches
    ax_colors.set_xlim(0, len(colors))
    ax_colors.set_ylim(0, 2)
    ax_colors.axis('off')

    # Each swatch takes up 1 unit of width
    swatch_width = 0.95

    for i, color in enumerate(colors):
        color_normalized = np.clip(np.array(color) / 255.0, 0, 1)

        # Draw color swatch
        rect = Rectangle((i + 0.025, 0.6), swatch_width, 1.2,
                       facecolor=color_normalized,
                       linewidth=1)
        ax_colors.add_patch(rect)

        # Add hex code below swatch
        hex_code = rgb_to_hex(color)
        ax_colors.text(i + 0.5, 0.4, hex_code,
                   ha='center', va='top', fontsize=12, fontweight='bold')

    if output_path:
        plt.savefig(output_path, dpi=dpi)
        print(f"\nResult saved to {output_path}")

    return fig


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
    print(f"\n{method_name}:")
    print("=" * 70)

    for i, color in enumerate(colors, 1):
        hex_code = rgb_to_hex(color)
        rgb_str = f"RGB({int(color[0])}, {int(color[1])}, {int(color[2])})"
        print(f"  {i}. {hex_code:10s} {rgb_str}")


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
