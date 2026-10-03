from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass
from typing import BinaryIO

from PIL import Image

from bot.models.color import Color, PaletteTheme
from bot.services.color_extractor import ColorExtractor
from bot.services.presets import THEME_PRESETS
from bot.services.theme_generators.android import AndroidThemeGenerator
from bot.services.theme_generators.ios import IosThemeGenerator
from bot.services.theme_generators.tdesktop import TDesktopThemeGenerator


@dataclass(frozen=True, slots=True)
class ProcessedThemeResult:
    """Contains rendered preview cards and compiled theme files."""

    dark_theme: PaletteTheme
    light_theme: PaletteTheme
    dark_preview_png: bytes
    light_preview_png: bytes
    tdesktop_dark: bytes
    tdesktop_light: bytes
    android_dark: bytes
    android_light: bytes
    ios_dark: bytes
    ios_light: bytes
    tdesktop_dark_pure: bytes | None = None
    tdesktop_light_pure: bytes | None = None
    android_dark_pure: bytes | None = None
    android_light_pure: bytes | None = None


class ThemeService:
    """Orchestrates image analysis and theme packaging, offloading CPU work to threads."""

    def __init__(self) -> None:
        self.extractor = ColorExtractor()
        self.tdesktop_gen = TDesktopThemeGenerator()
        self.android_gen = AndroidThemeGenerator()
        self.ios_gen = IosThemeGenerator()

    async def process_image_async(
        self,
        image_bytes: bytes | BinaryIO,
    ) -> ProcessedThemeResult:
        """Asynchronously process an image and generate complete themes in a worker thread."""
        return await asyncio.to_thread(self._process_image_sync, image_bytes)

    def _process_image_sync(self, image_input: bytes | BinaryIO) -> ProcessedThemeResult:
        stream = io.BytesIO(image_input) if isinstance(image_input, bytes) else image_input

        with Image.open(stream) as img:
            rgb_img = img.convert("RGB")
            dominants = self.extractor.extract_from_image(rgb_img)

            dark_theme = self.extractor.generate_theme(dominants, is_dark=True)
            light_theme = self.extractor.generate_theme(dominants, is_dark=False)

            dark_preview = self.extractor.render_preview_card(dark_theme, source_image=rgb_img)
            light_preview = self.extractor.render_preview_card(light_theme, source_image=rgb_img)

            td_dark = self.tdesktop_gen.generate_theme_package(dark_theme, source_image=rgb_img)
            td_light = self.tdesktop_gen.generate_theme_package(light_theme, source_image=rgb_img)
            an_dark = self.android_gen.generate_theme_package(dark_theme, source_image=rgb_img)
            an_light = self.android_gen.generate_theme_package(light_theme, source_image=rgb_img)
            ios_dark = self.ios_gen.generate_theme_package(dark_theme, name="Custom Dark")
            ios_light = self.ios_gen.generate_theme_package(light_theme, name="Custom Light")

            # Lightweight pure themes (no embedded wallpaper)
            td_dark_pure = self.tdesktop_gen.generate_theme_package(dark_theme, source_image=None)
            td_light_pure = self.tdesktop_gen.generate_theme_package(light_theme, source_image=None)
            an_dark_pure = self.android_gen.generate_theme_package(dark_theme, source_image=None)
            an_light_pure = self.android_gen.generate_theme_package(light_theme, source_image=None)

        return ProcessedThemeResult(
            dark_theme=dark_theme,
            light_theme=light_theme,
            dark_preview_png=dark_preview,
            light_preview_png=light_preview,
            tdesktop_dark=td_dark,
            tdesktop_light=td_light,
            android_dark=an_dark,
            android_light=an_light,
            ios_dark=ios_dark,
            ios_light=ios_light,
            tdesktop_dark_pure=td_dark_pure,
            tdesktop_light_pure=td_light_pure,
            android_dark_pure=an_dark_pure,
            android_light_pure=an_light_pure,
        )

    async def process_preset_async(self, preset_id: str) -> ProcessedThemeResult:
        """Asynchronously build complete themes from a curated preset in a worker thread."""
        return await asyncio.to_thread(self._process_preset_sync, preset_id)

    def _process_preset_sync(self, preset_id: str) -> ProcessedThemeResult:
        preset = THEME_PRESETS[preset_id]
        dark_theme = preset.dark_theme
        light_theme = preset.light_theme

        dark_preview = self.extractor.render_preview_card(dark_theme, source_image=None)
        light_preview = self.extractor.render_preview_card(light_theme, source_image=None)

        td_dark = self.tdesktop_gen.generate_theme_package(dark_theme, source_image=None)
        td_light = self.tdesktop_gen.generate_theme_package(light_theme, source_image=None)
        an_dark = self.android_gen.generate_theme_package(
            dark_theme, source_image=None, name=f"{preset.title} Dark"
        )
        an_light = self.android_gen.generate_theme_package(
            light_theme, source_image=None, name=f"{preset.title} Light"
        )
        ios_dark = self.ios_gen.generate_theme_package(
            dark_theme, name=f"{preset.title} Dark"
        )
        ios_light = self.ios_gen.generate_theme_package(
            light_theme, name=f"{preset.title} Light"
        )

        return ProcessedThemeResult(
            dark_theme=dark_theme,
            light_theme=light_theme,
            dark_preview_png=dark_preview,
            light_preview_png=light_preview,
            tdesktop_dark=td_dark,
            tdesktop_light=td_light,
            android_dark=an_dark,
            android_light=an_light,
            ios_dark=ios_dark,
            ios_light=ios_light,
            tdesktop_dark_pure=td_dark,
            tdesktop_light_pure=td_light,
            android_dark_pure=an_dark,
            android_light_pure=an_light,
        )

    async def process_custom_palette_async(
        self,
        palette_data: dict,
    ) -> ProcessedThemeResult:
        """Asynchronously build complete themes from custom WebApp parameters in a worker thread."""
        return await asyncio.to_thread(self._process_custom_palette_sync, palette_data)

    def _process_custom_palette_sync(self, data: dict) -> ProcessedThemeResult:
        theme, title = self._build_custom_palette(data)
        preview_png = self.extractor.render_preview_card(theme, source_image=None)

        td = self.tdesktop_gen.generate_theme_package(theme, source_image=None)
        an = self.android_gen.generate_theme_package(theme, source_image=None, name=title)
        ios = self.ios_gen.generate_theme_package(theme, name=title)

        return ProcessedThemeResult(
            dark_theme=theme,
            light_theme=theme,
            dark_preview_png=preview_png,
            light_preview_png=preview_png,
            tdesktop_dark=td,
            tdesktop_light=td,
            android_dark=an,
            android_light=an,
            ios_dark=ios,
            ios_light=ios,
            tdesktop_dark_pure=td,
            tdesktop_light_pure=td,
            android_dark_pure=an,
            android_light_pure=an,
        )

    def _build_custom_palette(self, data: dict) -> tuple[PaletteTheme, str]:
        accent_color = Color.from_hex(str(data.get("accent", "#00e5ff")))
        bg_color = Color.from_hex(str(data.get("background", "#0b0e14")))
        is_dark = bool(data.get("is_dark", True))
        title = str(data.get("name", "Custom Web Theme"))

        in_alpha = int(data.get("in_bubble_alpha", 255))
        out_alpha = int(data.get("out_bubble_alpha", 255))

        in_b_raw = data.get("in_bubble")
        out_b_raw = data.get("out_bubble")

        surf = bg_color.lighten(0.05) if is_dark else bg_color.darken(0.04)
        surf_var = surf.lighten(0.06) if is_dark else surf.darken(0.05)
        txt = Color(245, 245, 245) if is_dark else Color(25, 25, 25)
        txt_sec = Color(160, 160, 165) if is_dark else Color(115, 115, 120)

        in_b = Color.from_hex(str(in_b_raw)) if in_b_raw else (
            surf.lighten(0.08) if is_dark else Color(255, 255, 255)
        )
        out_b = Color.from_hex(str(out_b_raw)) if out_b_raw else (
            accent_color.darken(0.2) if is_dark else accent_color.lighten(0.3)
        )

        acc_txt = (
            Color(255, 255, 255)
            if accent_color.relative_luminance() < 0.5
            else Color(0, 0, 0)
        )
        out_txt = Color(255, 255, 255) if out_b.relative_luminance() < 0.5 else Color(0, 0, 0)


        theme = PaletteTheme(
            is_dark=is_dark,
            background=bg_color,
            surface=surf,
            surface_variant=surf_var,
            text_primary=txt,
            text_secondary=txt_sec,
            accent=accent_color,
            accent_text=acc_txt,
            out_bubble=out_b,
            out_bubble_text=out_txt,
            out_bubble_subtext=out_txt.blend(out_b, 0.35),
            in_bubble=in_b,
            in_bubble_text=txt.ensure_contrast(in_b, 4.5),
            in_bubble_subtext=txt_sec.ensure_contrast(in_b, 3.0),
            divider=surf_var,
            in_bubble_alpha=max(0, min(255, in_alpha)),
            out_bubble_alpha=max(0, min(255, out_alpha)),
        )
        return theme, title


