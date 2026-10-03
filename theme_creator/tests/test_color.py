from __future__ import annotations

import pytest

from bot.models.color import Color


def test_color_rgb_validation() -> None:
    valid = Color(10, 20, 30)
    assert valid.r == 10
    assert valid.g == 20
    assert valid.b == 30

    with pytest.raises(ValueError, match="Color channel 'r'"):
        Color(-1, 0, 0)

    with pytest.raises(ValueError, match="Color channel 'g'"):
        Color(0, 256, 0)


def test_color_hex_conversions() -> None:
    col = Color(255, 128, 0)
    assert col.hex == "#ff8000"
    assert col.hex_argb == "#ffff8000"

    parsed = Color.from_hex("#ff8000")
    assert parsed == col

    short_parsed = Color.from_hex("#f80")
    assert short_parsed == Color(255, 136, 0)


def test_color_int_argb_android_format() -> None:
    black = Color(0, 0, 0)
    # 0xFF000000 as signed 32-bit integer is -16777216
    assert black.int_argb == -16777216

    white = Color(255, 255, 255)
    # 0xFFFFFFFF as signed 32-bit integer is -1
    assert white.int_argb == -1

    translucent_black = black.with_alpha_int(128)
    # 0x80000000 as signed 32-bit integer is -2147483648
    assert translucent_black == -2147483648


def test_relative_luminance_extremes() -> None:
    black = Color(0, 0, 0)
    white = Color(255, 255, 255)

    assert pytest.approx(black.relative_luminance(), abs=1e-4) == 0.0
    assert pytest.approx(white.relative_luminance(), abs=1e-4) == 1.0


def test_contrast_ratio_wcag() -> None:
    black = Color(0, 0, 0)
    white = Color(255, 255, 255)

    ratio = black.contrast_ratio(white)
    assert pytest.approx(ratio, abs=0.1) == 21.0

    same_ratio = black.contrast_ratio(black)
    assert pytest.approx(same_ratio, abs=0.01) == 1.0


def test_blend_and_lighten_darken() -> None:
    red = Color(200, 0, 0)
    blue = Color(0, 0, 200)

    blended = red.blend(blue, 0.5)
    assert blended.r == 100
    assert blended.b == 100

    darkened = red.darken(0.5)
    assert darkened.r == 100

    lightened = Color(0, 0, 0).lighten(0.5)
    assert lightened.r == 128


def test_ensure_contrast_wcag() -> None:
    black = Color(0, 0, 0)
    dark_gray = Color(30, 30, 30)

    # Initial contrast is low (< 2.0)
    assert dark_gray.contrast_ratio(black) < 2.0

    # ensure_contrast guarantees >= 4.5
    readable = dark_gray.ensure_contrast(black, min_ratio=4.5)
    assert readable.contrast_ratio(black) >= 4.5

    # If already compliant, stays unchanged
    white = Color(255, 255, 255)
    assert white.ensure_contrast(black, min_ratio=4.5) == white
