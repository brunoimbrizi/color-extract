# color-extract

[![PyPI version](https://badge.fury.io/py/color-extract.svg)](https://badge.fury.io/py/color-extract)
[![Python Support](https://img.shields.io/pypi/pyversions/color-extract.svg)](https://pypi.org/project/color-extract/)

A toolkit to extract dominant colors from images using various K-Means clustering approaches.

| Example |
| :------ | 
| <img width="1256" height="492" alt="colors_Additional_073_all_6" src="https://github.com/user-attachments/assets/54c4f889-4195-4054-9f82-e098325745d0" /> |

## Features

**Extraction Methods**
- **Original K-Means**: Standard K-Means clustering approach
- **Aggressive Weighting**: K-Means with aggressive saturation weighting to emphasize vibrant colors
- **Vibrant Separate**: Separate clustering for vibrant minority colors and base colors
- **LAB Enhanced**: LAB color space with saturation-weighted sampling for perceptually uniform clustering
- **Multi-stage**: Multi-stage extraction: vibrant colors first, then distinct base colors

**Sorting**
- Spatial sorting (left-to-right or top-to-bottom)
- Frequency-based sorting

## Installation

```bash
pip install color-extract
```

## Command Line Usage

```bash
# Basic extraction with default settings
color-extract image.jpg

# Extract 8 colors using the vibrant method
color-extract image.jpg -c 8 -m vibrant

# Compare all methods and define output folder
color-extract image.jpg -m all -o ./my-folder
```

### Example Output
```
┌─────────────────────────────────────┐
│ LAB Enhanced                        │
└─────────────────────────────────────┘
┌───────┬──────────┬──────────────────┐
│  ■■■  │ #277595  │ (39, 117, 149)   │
│  ■■■  │ #68b2c6  │ (104, 178, 198)  │
│  ■■■  │ #6c6963  │ (108, 105, 99)   │
│  ■■■  │ #394d4d  │ (57, 77, 77)     │
│  ■■■  │ #782722  │ (120, 39, 34)    │
│  ■■■  │ #102937  │ (16, 41, 55)     │
└───────┴──────────┴──────────────────┘

Result saved to output/colors_image_lab_6.png
```

## CLI Options

```
usage: color-extract [options] image

Arguments:
  image                Path to the input image

Options:
  -h, --help           Show help message
  --colors, -c         Number of colors to extract (default: 6)
  --method, -m         Extraction method (default: lab)
  --output, -o         Output file path (default: ./output)
  --no-plot            Disable plot generation
  --sort               Color sorting: (default: x-axis)
  --max-dimension      Max dimension for downscaling (default: 64)
  --dpi                DPI for output plots (default: 150)
```

## More Examples

| Aggressive Weighting | LAB Enhanced |
| -------------------- | ------------ |
| <img width="880" height="820" alt="colors_OilDrums_aggressive_6" src="https://github.com/user-attachments/assets/b7d4f23c-efbe-4bb5-9563-085c806f6e02" /> | <img width="880" height="820" alt="colors_Additional_847_lab_6" src="https://github.com/user-attachments/assets/f2edc380-aff7-4e21-bf36-8fc2a80e30a1" /> |

| Multi-stage | K-Means |
| ----------- | ------- |
| <img width="880" height="820" alt="colors_Additional_1974_multistage_6" src="https://github.com/user-attachments/assets/5f3219b4-3ecc-47fb-940f-147f9fc089b3" /> | <img width="880" height="820" alt="colors_Additional_0966_kmeans_6" src="https://github.com/user-attachments/assets/eda3e631-132c-44da-ade7-ffecd9a2b426" /> |



## Python API Usage

```python
import color_extract
import numpy as np
from PIL import Image

# Simple extraction from file
colors = color_extract.extract_colors('image.jpg', method='lab', n_colors=5)
for color in colors:
    print(color_extract.rgb_to_hex(color))

# Use with numpy array
img = Image.open('image.jpg')
img_array = np.array(img)
colors = color_extract.extract_colors(img_array, method='aggressive')

# Advanced usage with visualization
from color_extract import plot_single_result, load_and_prepare_image

img, img_array = load_and_prepare_image('image.jpg')
colors = color_extract.extract_colors_lab_enhanced(img_array, n_colors=6)
sorted_colors = color_extract.sort_colors_by_spatial_position(img_array, colors)

# Generate visualization
plot_single_result(img, img_array, sorted_colors, 'LAB Enhanced', 'output.png')
```

## API Reference

### Main Functions

#### `extract_colors(image, method='lab', n_colors=6, sort_by='x-axis')`

Main convenience function for color extraction.

**Parameters:**
- `image`: File path (str) or numpy array (H, W, 3)
- `method`: Extraction method name
- `n_colors`: Number of colors to extract
- `sort_by`: Sorting method ('x-axis', 'y-axis', 'frequency')

**Returns:**
- List of RGB tuples

### Individual Extraction Methods

Each method can be used directly for more control:

```python
# Original K-Means
colors = extract_colors_kmeans_original(img_array, n_colors=6)

# LAB color space
colors = extract_colors_lab_enhanced(img_array, n_colors=6, saturation_boost=5.0)

# Aggressive saturation weighting
colors = extract_colors_weighted_aggressive(img_array, n_colors=6, saturation_boost=10.0)

# Separate vibrant colors
colors = extract_colors_vibrant_separate(img_array, n_colors=6, n_vibrant=3)

# Multi-stage extraction
colors = extract_colors_multistage(img_array, n_colors=6)
```

### Utility Functions

```python
# Color conversion
hex_color = rgb_to_hex((255, 128, 0))  # Returns '#ff8000'
rgb = hex_to_rgb('#ff8000')  # Returns (255, 128, 0)

# Spatial sorting
sorted_colors = sort_colors_by_spatial_position(img_array, colors, axis='x')

# Calculate statistics
stats = calculate_color_statistics(img_array, colors)

# Normalize arrays (useful for TouchDesigner)
normalized = normalize_image_array(array, input_range=(0, 1), output_range=(0, 255))
```

### Visualization Functions

```python
# Plot single result
fig = plot_single_result(img, img_array, colors, 'Method Name', 'output.png')

# Compare multiple methods
algorithms_dict = {
    'Method 1': colors1,
    'Method 2': colors2
}
fig = plot_comparison(img, img_array, algorithms_dict, 'comparison.png')

# Create simple palette image
palette_array = create_color_palette_image(colors, width=100, height=100)
```

## Further Reading

* [New Approach to Dominant and Prominent Color Extraction in Images with a Wide Range of Hues](https://www.mdpi.com/2227-7080/13/6/230)
* [Dominant Colors with (not just) K-Means](https://tatasz.github.io/dominant_colors/)
