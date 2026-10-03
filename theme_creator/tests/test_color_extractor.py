from __future__ import annotations

import io

from PIL import Image

from bot.services.color_extractor import ColorExtractor


def create_dual_tone_image(w: int = 120, h: int = 120) -> Image.Image:
    """Generate a synthetic test image with two distinct color regions."""
    img = Image.new("RGB", (w, h))
    for y in range(h):
        for x in range(w):
            if y < h // 2:
                img.putpixel((x, y), (0, 200, 220))  # Cyan region
            else:
                img.putpixel((x, y), (250, 70, 40))  # Coral region
    return img


def test_extract_dominant_colors() -> None:
    extractor = ColorExtractor(sample_size=60, max_clusters=4)
    img = create_dual_tone_image()
    dominants = extractor.extract_from_image(img)

    assert len(dominants) >= 2
    # Verify that clusters captured both the cool (cyan) and warm (coral) tones
    has_cyan = any(d.color.g > 150 and d.color.b > 150 for d in dominants)
    has_coral = any(d.color.r > 200 and d.color.g < 120 for d in dominants)

    assert has_cyan
    assert has_coral


def test_generate_dark_theme_properties() -> None:
    extractor = ColorExtractor()
    img = create_dual_tone_image()
    dominants = extractor.extract_from_image(img)

    dark_theme = extractor.generate_theme(dominants, is_dark=True)

    assert dark_theme.is_dark is True
    # Dark background should have low relative luminance
    assert dark_theme.background.relative_luminance() < 0.15
    # Primary text should be clearly readable against dark background
    assert dark_theme.background.contrast_ratio(dark_theme.text_primary) >= 7.0
    # Bubble text must meet minimum WCAG accessibility threshold
    assert dark_theme.out_bubble.contrast_ratio(dark_theme.out_bubble_text) >= 4.5
    assert dark_theme.in_bubble.contrast_ratio(dark_theme.in_bubble_text) >= 7.0


def test_generate_light_theme_properties() -> None:
    extractor = ColorExtractor()
    img = create_dual_tone_image()
    dominants = extractor.extract_from_image(img)

    light_theme = extractor.generate_theme(dominants, is_dark=False)

    assert light_theme.is_dark is False
    # Light background should have high relative luminance
    assert light_theme.background.relative_luminance() > 0.85
    # Dark text against light background
    assert light_theme.background.contrast_ratio(light_theme.text_primary) >= 7.0
    # Bubble text contrast
    assert light_theme.out_bubble.contrast_ratio(light_theme.out_bubble_text) >= 4.0
    assert light_theme.in_bubble.contrast_ratio(light_theme.in_bubble_text) >= 7.0


def test_render_preview_card_png_output() -> None:
    extractor = ColorExtractor()
    img = create_dual_tone_image()
    dominants = extractor.extract_from_image(img)
    theme = extractor.generate_theme(dominants, is_dark=True)

    png_bytes = extractor.render_preview_card(theme, source_image=img)

    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    # Verify that Pillow can parse the resulting PNG
    rendered = Image.open(io.BytesIO(png_bytes))
    assert rendered.format == "PNG"
    assert rendered.size == (760, 480)
