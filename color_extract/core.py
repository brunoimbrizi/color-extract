"""
Core color extraction algorithms using various K-Means clustering approaches.
"""

import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
from skimage import color as skimage_color


def extract_colors_kmeans_original(img_array, n_colors=6):
    """
    Original K-Means clustering for color extraction.

    Args:
        img_array: numpy array of shape (height, width, 3) with RGB values 0-255
        n_colors: number of colors to extract

    Returns:
        Array of RGB color values
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    rng = np.random.default_rng(seed=42)

    n_samples = min(20000, len(pixels))
    sample_indices = rng.choice(len(pixels), n_samples, replace=False)
    sampled_pixels = pixels[sample_indices]

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(sampled_pixels)

    colors = kmeans.cluster_centers_
    labels = kmeans.predict(pixels)
    counts = Counter(labels)

    sorted_colors = [colors[i] for i in sorted(counts.keys(), key=lambda x: counts[x], reverse=True)]
    return sorted_colors


def extract_colors_weighted_aggressive(img_array, n_colors=6, saturation_boost=10.0):
    """
    K-Means with aggressive saturation weighting to emphasize vibrant colors.

    Args:
        img_array: numpy array of shape (height, width, 3) with RGB values 0-255
        n_colors: number of colors to extract
        saturation_boost: weight multiplier for saturated colors

    Returns:
        Array of RGB color values
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    max_rgb = np.maximum(np.maximum(np.maximum(r, g), b), 1)
    min_rgb = np.minimum(np.minimum(r, g), b)
    saturations = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)

    weights = 1.0 + (saturations ** 3) * saturation_boost

    rng = np.random.default_rng(seed=222)

    n_samples = min(15000, len(pixels))
    probabilities = weights / weights.sum()
    indices = rng.choice(len(pixels), size=n_samples, replace=True, p=probabilities)
    weighted_pixels = pixels[indices]

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(weighted_pixels)

    return kmeans.cluster_centers_


def extract_colors_vibrant_separate(img_array, n_colors=6, n_vibrant=3, saturation_threshold=0.3):
    """
    Separate clustering for vibrant minority colors and base colors.

    Args:
        img_array: numpy array of shape (height, width, 3) with RGB values 0-255
        n_colors: total number of colors to extract
        n_vibrant: number of vibrant colors to extract separately
        saturation_threshold: minimum saturation to consider a color vibrant

    Returns:
        Array of RGB color values
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    rng = np.random.default_rng(seed=333)

    n_samples = min(20000, len(pixels))
    sample_indices = rng.choice(len(pixels), n_samples, replace=False)
    sampled_pixels = pixels[sample_indices]

    r, g, b = sampled_pixels[:, 0], sampled_pixels[:, 1], sampled_pixels[:, 2]
    max_rgb = np.maximum(np.maximum(np.maximum(r, g), b), 1)
    min_rgb = np.minimum(np.minimum(r, g), b)
    saturations = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)

    vibrant_mask = saturations > saturation_threshold
    vibrant_pixels = sampled_pixels[vibrant_mask]
    non_vibrant_pixels = sampled_pixels[~vibrant_mask]

    colors = []

    if len(vibrant_pixels) > n_vibrant:
        kmeans_vibrant = KMeans(n_clusters=n_vibrant, random_state=42, n_init=10)
        kmeans_vibrant.fit(vibrant_pixels)
        colors.extend(kmeans_vibrant.cluster_centers_)

    n_base = n_colors - len(colors)
    if n_base > 0 and len(non_vibrant_pixels) > n_base:
        kmeans_base = KMeans(n_clusters=n_base, random_state=42, n_init=10)
        kmeans_base.fit(non_vibrant_pixels)
        colors.extend(kmeans_base.cluster_centers_)

    while len(colors) < n_colors:
        if len(vibrant_pixels) > 0:
            idx = np.argmax(saturations[vibrant_mask])
            colors.append(vibrant_pixels[idx])
            vibrant_mask[np.where(vibrant_mask)[0][idx]] = False
        else:
            break

    return np.array(colors[:n_colors])


def extract_colors_lab_enhanced(img_array, n_colors=6, saturation_boost=5.0):
    """
    LAB color space with saturation-weighted sampling for perceptually uniform clustering.

    Args:
        img_array: numpy array of shape (height, width, 3) with RGB values 0-255
        n_colors: number of colors to extract
        saturation_boost: weight multiplier for saturated colors

    Returns:
        Array of RGB color values
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    max_rgb = np.maximum(np.maximum(np.maximum(r, g), b), 1)
    min_rgb = np.minimum(np.minimum(r, g), b)
    saturations = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)

    weights = 1.0 + (saturations ** 2) * saturation_boost
    probabilities = weights / weights.sum()

    rng = np.random.default_rng(seed=444)

    n_samples = min(15000, len(pixels))
    indices = rng.choice(len(pixels), size=n_samples, replace=True, p=probabilities)
    sampled_pixels = pixels[indices]

    lab_pixels = skimage_color.rgb2lab(sampled_pixels / 255.0)

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(lab_pixels)

    lab_colors = kmeans.cluster_centers_
    rgb_colors = skimage_color.lab2rgb(lab_colors) * 255

    return np.clip(rgb_colors, 0, 255)


def extract_colors_multistage(img_array, n_colors=6):
    """
    Multi-stage extraction: vibrant colors first, then distinct base colors.

    Args:
        img_array: numpy array of shape (height, width, 3) with RGB values 0-255
        n_colors: number of colors to extract

    Returns:
        Array of RGB color values
    """
    pixels = img_array.reshape(-1, 3).astype(np.float32)

    rng = np.random.default_rng(seed=555)

    n_samples = min(20000, len(pixels))
    sample_indices = rng.choice(len(pixels), n_samples, replace=False)
    sampled_pixels = pixels[sample_indices]

    # Calculate saturation for all pixels
    r, g, b = sampled_pixels[:, 0], sampled_pixels[:, 1], sampled_pixels[:, 2]
    max_rgb = np.maximum(np.maximum(np.maximum(r, g), b), 1)
    min_rgb = np.minimum(np.minimum(r, g), b)
    saturations = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)

    # Stage 1: Extract 2 vibrant colors
    vibrant_threshold = 0.5
    vibrant_mask = saturations > vibrant_threshold
    vibrant_pixels = sampled_pixels[vibrant_mask]

    colors = []

    if len(vibrant_pixels) > 2:
        kmeans_vibrant = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans_vibrant.fit(vibrant_pixels)
        colors.extend(kmeans_vibrant.cluster_centers_)

    # Stage 2: Extract remaining colors with distance constraint
    n_remaining = n_colors - len(colors)
    if n_remaining > 0:
        if len(colors) > 0:
            # Calculate minimum distance from existing colors
            min_distances = []
            for pixel in sampled_pixels:
                distances = [np.linalg.norm(pixel - c) for c in colors]
                min_distances.append(min(distances))

            # Weight by distance from existing colors
            min_distances = np.array(min_distances)
            distance_weights = min_distances ** 2

            # Combine with moderate saturation weight
            combined_weights = distance_weights * (1 + saturations * 2)
            probabilities = combined_weights / combined_weights.sum()

            # Sample with weights
            n_stage2_samples = min(10000, len(sampled_pixels))
            indices = rng.choice(len(sampled_pixels),
                                     size=n_stage2_samples,
                                     replace=True,
                                     p=probabilities)
            stage2_pixels = sampled_pixels[indices]
        else:
            stage2_pixels = sampled_pixels

        kmeans_base = KMeans(n_clusters=n_remaining, random_state=42, n_init=10)
        kmeans_base.fit(stage2_pixels)
        colors.extend(kmeans_base.cluster_centers_)

    return np.array(colors[:n_colors])


# Dictionary mapping method names to functions
EXTRACTION_METHODS = {
    'kmeans': ('Original K-Means', extract_colors_kmeans_original),
    'aggressive': ('Aggressive Weighting', extract_colors_weighted_aggressive),
    'vibrant': ('Vibrant Separate', extract_colors_vibrant_separate),
    'lab': ('LAB Enhanced', extract_colors_lab_enhanced),
    'multistage': ('Multi-stage', extract_colors_multistage)
}
