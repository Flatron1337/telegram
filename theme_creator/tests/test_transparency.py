from __future__ import annotations

import asyncio

import yaml
from PIL import Image

from bot.models.color import Color
from bot.services.color_extractor import ColorExtractor
from bot.services.theme_generators.android import AndroidThemeGenerator
from bot.services.theme_generators.ios import IosThemeGenerator
from bot.services.theme_generators.tdesktop import TDesktopThemeGenerator
from bot.services.theme_service import ThemeService


def test_color_with_alpha_hex() -> None:
    col = Color(0, 229, 255)
    # 180 is 0xb4
    alpha_hex = col.with_alpha_hex(180)
    assert alpha_hex.lower() == "#b400e5ff"


def test_palette_theme_with_transparency() -> None:
    extractor = ColorExtractor()
    img = Image.new("RGB", (40, 40), (50, 100, 200))
    theme = extractor.generate_theme(extractor.extract_from_image(img), is_dark=True)

    assert theme.in_bubble_alpha == 255
    assert theme.out_bubble_alpha == 255

    glass_theme = theme.with_transparency(in_alpha=180, out_alpha=200)
    assert glass_theme.in_bubble_alpha == 180
    assert glass_theme.out_bubble_alpha == 200
    assert glass_theme.accent == theme.accent


def test_theme_generators_apply_transparency() -> None:
    extractor = ColorExtractor()
    img = Image.new("RGB", (40, 40), (50, 100, 200))
    theme = extractor.generate_theme(extractor.extract_from_image(img), is_dark=True)
    glass_theme = theme.with_transparency(in_alpha=180, out_alpha=200)

    # 1. Android
    an_gen = AndroidThemeGenerator()
    an_entries = an_gen._build_theme_entries(glass_theme)
    # Check that inBubble has alpha 180
    in_bg = an_entries["chat_inBubble"]
    u_val = in_bg if in_bg >= 0 else in_bg + (1 << 32)
    assert (u_val >> 24) & 0xFF == 180

    # 2. TDesktop
    td_gen = TDesktopThemeGenerator()
    td_text = td_gen.generate_palette_text(glass_theme)
    assert f"#{180:02x}" in td_text.lower()
    assert f"#{200:02x}" in td_text.lower()

    # 3. iOS
    ios_gen = IosThemeGenerator()
    ios_text = ios_gen.generate_theme_text(glass_theme)
    data = yaml.safe_load(ios_text)
    in_bg_ios = data["chat"]["message"]["incoming"]["bubble"]["withWp"]["bg"]
    out_bg_ios = data["chat"]["message"]["outgoing"]["bubble"]["withWp"]["bg"]
    assert in_bg_ios.lower().startswith(f"{180:02x}")
    assert out_bg_ios.lower().startswith(f"{200:02x}")


def test_theme_service_custom_palette_with_transparency() -> None:
    async def _run() -> None:
        service = ThemeService()
        payload = {
            "name": "Neon Glass Rem",
            "is_dark": True,
            "accent": "#00e5ff",
            "background": "#0b0e14",
            "in_bubble": "#1a2233",
            "out_bubble": "#005577",
            "in_bubble_alpha": 170,
            "out_bubble_alpha": 210,
            "has_transparency": True,
        }
        res = await service.process_custom_palette_async(payload)

        assert res.dark_theme.in_bubble_alpha == 170
        assert res.dark_theme.out_bubble_alpha == 210
        assert res.dark_preview_png.startswith(b"\x89PNG")
        assert len(res.tdesktop_dark) > 1000
        assert len(res.android_dark) > 1000
        assert len(res.ios_dark) > 1000

    asyncio.run(_run())
