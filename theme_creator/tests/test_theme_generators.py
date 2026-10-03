from __future__ import annotations

import io
import zipfile

import yaml
from PIL import Image

from bot.services.color_extractor import ColorExtractor
from bot.services.theme_generators.android import AndroidThemeGenerator
from bot.services.theme_generators.ios import IosThemeGenerator
from bot.services.theme_generators.tdesktop import TDesktopThemeGenerator


def create_sample_theme():
    extractor = ColorExtractor()
    sample_img = Image.new("RGB", (60, 60), (30, 120, 200))
    dominants = extractor.extract_from_image(sample_img)
    return extractor.generate_theme(dominants, is_dark=True), sample_img


def test_tdesktop_palette_syntax() -> None:
    theme, _ = create_sample_theme()
    generator = TDesktopThemeGenerator()
    palette_text = generator.generate_palette_text(theme)

    assert palette_text.startswith("// Telegram Desktop")
    lines = [
        line.strip()
        for line in palette_text.splitlines()
        if line.strip() and not line.startswith("//")
    ]
    assert len(lines) >= 450

    defined_keys: set[str] = set()
    for line in lines:
        assert line.endswith(";"), f"Line missing semicolon: {line}"
        key, val = line[:-1].split(":", 1)
        clean_val = val.strip()
        is_hex = clean_val.startswith("#")
        is_ref = clean_val in defined_keys
        assert is_hex or is_ref, (
            f"Value for {key} is neither valid hex nor previously defined variable: {clean_val}"
        )
        defined_keys.add(key.strip())


def test_tdesktop_theme_package_zip() -> None:
    theme, sample_img = create_sample_theme()
    generator = TDesktopThemeGenerator()
    pkg_bytes = generator.generate_theme_package(theme, source_image=sample_img)

    with zipfile.ZipFile(io.BytesIO(pkg_bytes), mode="r") as archive:
        namelist = archive.namelist()
        assert "colors.tdesktop-palette" in namelist
        assert "colors.tdesktop-theme" in namelist
        assert "background.jpg" in namelist

        wp = archive.read("background.jpg")
        assert wp.startswith(b"\xff\xd8\xff")


def test_android_theme_syntax_integers() -> None:
    theme, _ = create_sample_theme()
    generator = AndroidThemeGenerator()
    theme_text = generator.generate_theme_text(theme, name="Test Theme", author="@tester")

    assert theme_text.startswith("#name=Test Theme\n#author=@tester\n#dark=true\n")

    lines = [
        line.strip() for line in theme_text.splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert len(lines) >= 540

    keys = set()
    for line in lines:
        assert "=" in line
        key, val_str = line.split("=", 1)
        val = int(val_str)
        # Ensure 32-bit signed integer boundary
        assert -2147483648 <= val <= 2147483647, (
            f"Integer out of signed 32-bit range for {key}: {val}"
        )
        keys.add(key)

    # Verify critical UI components that previously caused un-themed defaults
    critical_keys = (
        "actionBarDefaultSubmenuBackground",
        "actionBarDefaultSubmenuItem",
        "actionBarDefaultSubmenuItemIcon",
        "actionBarDefaultIcon",
        "actionBarDefaultSelector",
        "avatar_backgroundBlue",
        "dialogBackground",
        "dialogButton",
        "windowBackgroundWhiteBlackText",
        "chat_messageTextIn",
        "chat_messageTextOut",
        "chat_inText",
        "chat_outText",
        "chat_reactions_active",
        "switchTrackChecked",
    )
    for c_key in critical_keys:
        assert c_key in keys, f"Missing critical theme key: {c_key}"


def test_android_theme_ripple_alpha() -> None:
    theme, _ = create_sample_theme()
    generator = AndroidThemeGenerator()
    entries = generator._build_theme_entries(theme)

    # Verify selectors have translucent alpha (~48/255)
    for selector_key in ("actionBarDefaultSelector", "actionBarActionModeDefaultSelector"):
        val = entries[selector_key]
        alpha = ((val if val >= 0 else val + (1 << 32)) >> 24) & 0xFF
        assert alpha == 48, f"Expected alpha 48 for {selector_key}, got {alpha}"


def test_android_theme_toolbar_wcag_contrast() -> None:
    from bot.models.color import Color

    theme, _ = create_sample_theme()
    generator = AndroidThemeGenerator()
    entries = generator._build_theme_entries(theme)

    def int_to_color(val: int) -> Color:
        u_val = val if val >= 0 else val + (1 << 32)
        return Color(
            r=(u_val >> 16) & 0xFF,
            g=(u_val >> 8) & 0xFF,
            b=u_val & 0xFF,
        )

    ab_bg = int_to_color(entries["actionBarDefault"])
    ab_icon = int_to_color(entries["actionBarDefaultIcon"])
    ab_subtitle = int_to_color(entries["actionBarDefaultSubtitle"])

    assert ab_icon.contrast_ratio(ab_bg) >= 4.5
    assert ab_subtitle.contrast_ratio(ab_bg) >= 4.5


def test_android_theme_package_with_wallpaper() -> None:
    theme, sample_img = create_sample_theme()
    generator = AndroidThemeGenerator()

    # Plain text without wallpaper
    plain_bytes = generator.generate_theme_package(theme, source_image=None)
    assert b"chat_inBubble=" in plain_bytes
    assert b"WPS\n" not in plain_bytes

    # Native attheme with embedded wallpaper
    theme_with_wp = generator.generate_theme_package(theme, source_image=sample_img)
    assert b"chat_inBubble=" in theme_with_wp
    assert b"WPS\n" in theme_with_wp
    assert b"\nWPE\n" in theme_with_wp

    # Extract wallpaper segment
    wps_pos = theme_with_wp.find(b"WPS\n") + 4
    wpe_pos = theme_with_wp.find(b"\nWPE\n")
    wp_bytes = theme_with_wp[wps_pos:wpe_pos]
    assert wp_bytes.startswith(b"\xff\xd8\xff")  # JPEG header


def test_ios_theme_syntax() -> None:
    theme, _ = create_sample_theme()
    generator = IosThemeGenerator()

    # Dark theme
    dark_text = generator.generate_theme_text(theme, name="@my_themes_bot")
    data_dark = yaml.safe_load(dark_text)

    assert data_dark["name"] == "@my_themes_bot"
    assert data_dark["dark"] is True
    assert data_dark["statusBar"] == "black"
    assert "root" in data_dark
    assert "chatList" in data_dark
    assert "chat" in data_dark
    assert "actionSheet" in data_dark
    assert "contextMenu" in data_dark
    assert "notification" in data_dark

    # Light theme
    light_theme = ColorExtractor().generate_theme(
        ColorExtractor().extract_from_image(Image.new("RGB", (30, 30), (240, 240, 240))),
        is_dark=False,
    )
    light_text = generator.generate_theme_text(light_theme, name="Light Custom")
    data_light = yaml.safe_load(light_text)

    assert data_light["name"] == "Light Custom"
    assert data_light["dark"] is False
    assert data_light["statusBar"] == "white"


def test_ios_theme_package_bytes() -> None:
    theme, _ = create_sample_theme()
    generator = IosThemeGenerator()

    pkg_bytes = generator.generate_theme_package(theme, name="Package Test")
    assert isinstance(pkg_bytes, bytes)
    assert len(pkg_bytes) > 2000

    parsed = yaml.safe_load(pkg_bytes.decode("utf-8"))
    assert parsed["name"] == "Package Test"
